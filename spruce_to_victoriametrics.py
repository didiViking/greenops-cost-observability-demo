import requests
import pandas as pd
from pathlib import Path

VM_URL = "http://localhost:8428/api/v1/import/prometheus"

PARQUET_DIR = Path("outputs/result")

parquet_files = sorted(PARQUET_DIR.glob("*.parquet"))

if not parquet_files:
    raise FileNotFoundError(f"No parquet files found in {PARQUET_DIR}")

parquet_file = parquet_files[0]

print(f"Reading {parquet_file}")

df = pd.read_parquet(parquet_file)

metrics = []

REGION_FACTORS = {
    "ES Central": 0.00020,
    "West Europe": 0.00018,
    "North Europe": 0.00017,
}

for _, row in df.iterrows():

    provider = str(row.get("ProviderName", "unknown"))
    service = str(row.get("ServiceName", "unknown"))
    region = str(row.get("RegionName", row.get("Region", "unknown")))
    subscription = str(row.get("SubscriptionName", "unknown"))
    resource_group = str(row.get("ResourceGroupName", "unknown"))
    resource = str(row.get("ResourceName", row.get("ResourceId", "unknown")))

    cost = float(row.get("BilledCost", 0) or 0)
    usage = float(row.get("ConsumedQuantity", 0) or 0)

    labels = (
        f'provider="{provider}",'
        f'service="{service}",'
        f'region="{region}",'
        f'subscription="{subscription}",'
        f'resource_group="{resource_group}",'
        f'resource="{resource}"'
    )

    metrics.append(
        f'greenops_cost_total{{{labels}}} {cost}'
    )

    metrics.append(
        f'greenops_cost_provider{{provider="{provider}"}} {cost}'
    )

    metrics.append(
        f'greenops_cost_service{{service="{service}"}} {cost}'
    )

    metrics.append(
        f'greenops_cost_region{{region="{region}"}} {cost}'
    )

    metrics.append(
        f'greenops_cost_resource_group{{resource_group="{resource_group}"}} {cost}'
    )

    metrics.append(
        f'greenops_cost_subscription{{subscription="{subscription}"}} {cost}'
    )

    metrics.append(
        f'greenops_usage_quantity{{service="{service}",region="{region}"}} {usage}'
    )

    factor = REGION_FACTORS.get(region, 0.00025)
    co2 = cost * factor

    metrics.append(
        f'greenops_co2_estimate{{region="{region}"}} {co2}'
    )

payload = "\n".join(metrics)

print(f"Generated {len(metrics)} Prometheus samples")

response = requests.post(
    VM_URL,
    data=payload,
    headers={"Content-Type": "text/plain"},
)

print(f"VictoriaMetrics response: {response.status_code}")

if response.status_code != 204:
    print(response.text)
else:
    print("Metrics successfully imported.")
