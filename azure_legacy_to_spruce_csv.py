import os
import pandas as pd

INPUT = "exports/cost-reports/azure_legacy.csv"
OUTPUT = "outputs/spruce_input.csv"

df = pd.read_csv(INPUT, dtype=str)

print(f"Loaded {len(df)} rows")
print(f"Original columns: {len(df.columns)}")

# ---------------------------------------------------------------------
# Azure Legacy -> SPRUCE compatibility mappings
# ---------------------------------------------------------------------

mapping = {
    "resourceGroupName": "ResourceGroup",
    "resourceLocation": "ResourceLocation",
    "quantity": "Quantity",
    "costInBillingCurrency": "CostInBillingCurrency",
    "consumedService": "ConsumedService",
    "meterCategory": "MeterCategory",
    "meterSubCategory": "MeterSubCategory",
    "meterName": "MeterName",
    "unitOfMeasure": "UnitOfMeasure",
    "ResourceId": "ResourceID97",
    "SubscriptionId": "SubscriptionId",
}

for src, dst in mapping.items():
    if src in df.columns and dst not in df.columns:
        df[dst] = df[src]

# ---------------------------------------------------------------------
# Required Azure columns
# ---------------------------------------------------------------------

required_defaults = {
    "ResourceLocation": "",
    "ResourceGroup": "",
    "ConsumedService": "",
    "MeterCategory": "",
    "MeterSubCategory": "",
    "MeterName": "",
    "UnitOfMeasure": "",
    "Quantity": "0",
    "CostInBillingCurrency": "0",
    "ChargeType": "Usage",
    "SubscriptionId": "",
    "ResourceID97": "",
    "Date": "",
}

for col, default in required_defaults.items():
    if col not in df.columns:
        df[col] = default

# ---------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------

if "date" in df.columns:
    df["Date"] = df["date"].astype(str).str[:10]
elif "servicePeriodStartDate" in df.columns:
    df["Date"] = df["servicePeriodStartDate"].astype(str).str[:10]
elif "billingPeriodStartDate" in df.columns:
    df["Date"] = df["billingPeriodStartDate"].astype(str).str[:10]

df["Date"] = df["Date"].fillna("").astype(str)

# ---------------------------------------------------------------------
# VM normalization
# ---------------------------------------------------------------------

vm_mask = df["MeterCategory"].astype(str) == "Virtual Machines"

df.loc[vm_mask, "UnitOfMeasure"] = "Hours"

# ---------------------------------------------------------------------
# Force Azure text columns to strings
# ---------------------------------------------------------------------

string_columns = [
    "ResourceLocation",
    "ResourceID97",
    "ResourceGroup",
    "ConsumedService",
    "MeterCategory",
    "MeterSubCategory",
    "MeterName",
    "UnitOfMeasure",
    "ChargeType",
    "SubscriptionId",
    "Date",
]

for c in string_columns:
    df[c] = df[c].fillna("").astype(str)

# ---------------------------------------------------------------------
# Numeric columns
# ---------------------------------------------------------------------

for c in ["Quantity", "CostInBillingCurrency"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ---------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------

print("\nAzure compatibility columns:")

for c in [
    "ResourceLocation",
    "ResourceID97",
    "ResourceGroup",
    "ConsumedService",
    "MeterCategory",
    "MeterSubCategory",
    "MeterName",
    "UnitOfMeasure",
    "Quantity",
    "CostInBillingCurrency",
    "ChargeType",
    "SubscriptionId",
    "Date",
]:
    print(f"  ✓ {c}")

print(f"\nFinal columns: {len(df.columns)}")

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8",
)

print(f"Wrote {OUTPUT}")
