import requests
from pyspark.sql import SparkSession

VM_URL = "http://localhost:8428/api/v1/import/prometheus"

spark = (
    SparkSession.builder
    .appName("SPRUCE-to-VictoriaMetrics")
    .getOrCreate()
)

# Read SPRUCE output
df = spark.read.parquet("outputs/result")

metrics = []

for row in df.collect():

    # ---------------------------------------------------------
    # Common labels
    # ---------------------------------------------------------
    region = row["RegionName"] or "unknown"
    service = row["ServiceName"] or "unknown"
    category = row["ServiceCategory"] or "unknown"
    sku = row["SkuId"] or "unknown"
    resource_group = row["ResourceGroup"] or "unknown"
    provider = row["ProviderName"] or "Azure"

    labels = (
        f'region="{region}",'
        f'service="{service}",'
        f'category="{category}",'
        f'sku="{sku}",'
        f'resource_group="{resource_group}",'
        f'provider="{provider}"'
    )

    # ---------------------------------------------------------
    # Cost metrics
    # ---------------------------------------------------------
    billed_cost = float(row["BilledCost"] or 0)
    effective_cost = float(row["EffectiveCost"] or 0)
    contracted_cost = float(row["ContractedCost"] or 0)
    list_cost = float(row["ListCost"] or 0)
    billed_cost_usd = float(row["x_BilledCostInUsd"] or 0)
    unit_price = float(row["ListUnitPrice"] or 0)

    metrics.append(f'cloud_cost{{{labels}}} {billed_cost}')
    metrics.append(f'cloud_effective_cost{{{labels}}} {effective_cost}')
    metrics.append(f'cloud_contracted_cost{{{labels}}} {contracted_cost}')
    metrics.append(f'cloud_list_cost{{{labels}}} {list_cost}')
    metrics.append(f'cloud_cost_usd{{{labels}}} {billed_cost_usd}')
    metrics.append(f'cloud_unit_price{{{labels}}} {unit_price}')

    # ---------------------------------------------------------
    # Usage
    # ---------------------------------------------------------
    usage = float(row["ConsumedQuantity"] or 0)

    metrics.append(
        f'cloud_usage_quantity{{{labels}}} {usage}'
    )

    # ---------------------------------------------------------
    # Sustainability metrics (provided by SPRUCE)
    # ---------------------------------------------------------
    operational_energy = float(row["operational_energy_kwh"] or 0)
    operational_emissions = float(row["operational_emissions_co2eq_g"] or 0)
    embodied_emissions = float(row["embodied_emissions_co2eq_g"] or 0)
    carbon_intensity = float(row["carbon_intensity"] or 0)
    pue = float(row["power_usage_effectiveness"] or 0)
    wue = float(row["water_usage_effectiveness"] or 0)
    water_cooling = float(row["water_cooling_l"] or 0)
    water_electricity = float(row["water_electricity_production_l"] or 0)
    water_stress = float(row["water_consumption_stress_area_l"] or 0)

    metrics.append(
        f'cloud_operational_energy_kwh{{{labels}}} {operational_energy}'
    )

    metrics.append(
        f'cloud_operational_emissions_co2eq_g{{{labels}}} {operational_emissions}'
    )

    metrics.append(
        f'cloud_embodied_emissions_co2eq_g{{{labels}}} {embodied_emissions}'
    )

    metrics.append(
        f'cloud_carbon_intensity{{{labels}}} {carbon_intensity}'
    )

    metrics.append(
        f'cloud_power_usage_effectiveness{{{labels}}} {pue}'
    )

    metrics.append(
        f'cloud_water_usage_effectiveness{{{labels}}} {wue}'
    )

    metrics.append(
        f'cloud_water_cooling_l{{{labels}}} {water_cooling}'
    )

    metrics.append(
        f'cloud_water_electricity_production_l{{{labels}}} {water_electricity}'
    )

    metrics.append(
        f'cloud_water_consumption_stress_area_l{{{labels}}} {water_stress}'
    )

    # ---------------------------------------------------------
    # Resource inventory
    # ---------------------------------------------------------
    inventory_labels = (
        labels +
        f',resource="{row["ResourceName"] or "unknown"}"'
        f',resource_type="{row["ResourceType"] or "unknown"}"'
        f',subscription="{row["SubscriptionId"] or "unknown"}"'
    )

    metrics.append(
        f'cloud_resource_info{{{inventory_labels}}} 1'
    )

    metrics.append(
        f'cloud_resources_total{{{labels}}} 1'
    )

    # ---------------------------------------------------------
    # Meter inventory
    # ---------------------------------------------------------
    meter_labels = (
        labels +
        f',meter="{row["MeterName"] or "unknown"}"'
        f',meter_category="{row["MeterCategory"] or "unknown"}"'
        f',meter_subcategory="{row["MeterSubCategory"] or "unknown"}"'
    )

    metrics.append(
        f'cloud_meter_info{{{meter_labels}}} 1'
    )

# ---------------------------------------------------------
# Push everything to VictoriaMetrics
# ---------------------------------------------------------

payload = "\n".join(metrics)

response = requests.post(VM_URL, data=payload)

print(f"Pushed {len(metrics)} metrics to VictoriaMetrics")
print(f"HTTP Status: {response.status_code}")

if response.status_code != 204:
    print(response.text)

spark.stop()
