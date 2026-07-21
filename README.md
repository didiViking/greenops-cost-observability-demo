# 🌱 GreenOps Observability Pipeline
## Azure Cost Management → SPRUCE → VictoriaMetrics → Grafana

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-demo-orange.svg)
![Stack](https://img.shields.io/badge/stack-Azure%20%7C%20SPRUCE%20%7C%20VictoriaMetrics%20%7C%20Grafana-green.svg)

This repository demonstrates how to build an end-to-end **GreenOps observability pipeline** using **Azure Cost Management exports**, **SPRUCE**, **VictoriaMetrics**, and **Grafana**.

Instead of treating cloud billing as static reports, this project transforms cloud cost and sustainability data into **Prometheus-compatible time series metrics** that can be queried, aggregated, visualized, and correlated alongside traditional infrastructure telemetry.

The result is a workflow where cloud cost, operational energy, carbon emissions, water consumption, and other sustainability indicators become first-class observability signals.

---

> **📖 Looking for the engineering story?**
>
> This repository accompanies my Medium article:
>
> **Building a GreenOps Observability Pipeline: From SPRUCE to Carbon-Aware Metrics with Open Source**
>
> where I document the complete engineering journey—from experimenting with Azure billing exports, collaborating with the SPRUCE maintainers, enriching billing data with sustainability metrics, and exposing everything through VictoriaMetrics and Grafana.
>
> 👉 https://medium.com/@dianatodea/building-a-greenops-observability-pipeline-from-spruce-to-carbon-aware-metrics-with-open-source-c7e496dbc236

---

# Why This Project?

Traditional FinOps workflows usually end with reports and dashboards consumed by finance teams.

This project explores a different idea:

> **Cloud cost is telemetry. Sustainability is telemetry.**

Once billing information becomes metrics, engineers can use the same tools they already rely on for infrastructure observability to:

- query cloud spend using PromQL
- visualize cost trends alongside operational metrics
- correlate deployments with cloud spending
- explore sustainability indicators
- identify expensive services and SKUs
- analyze operational energy consumption
- inspect carbon emissions
- build dashboards and alerts using existing observability tooling

Rather than introducing another platform dedicated to sustainability, this project demonstrates how GreenOps can naturally integrate into modern observability stacks.

---

# What You'll Build

Following this repository you'll build a complete GreenOps observability pipeline capable of:

- exporting Azure Cost Management billing data
- normalizing billing data with SPRUCE
- enriching billing records with sustainability metrics
- converting enriched records into Prometheus metrics
- storing them inside VictoriaMetrics
- exploring them through VMUI
- visualizing them with Grafana

---

# Technologies

This demo uses:

- Azure Cost Management (Legacy CSV export)
- SPRUCE
- Apache Spark / PySpark
- Python
- VictoriaMetrics
- Grafana
- Prometheus exposition format

---

# Architecture (NEW-Recommended)

```text
Azure FOCUS 1.0 Export
        │
        ▼
      SPRUCE
        │
        ▼
 Enriched Parquet
        │
        ▼
Python exporter
        │
        ▼
VictoriaMetrics
        │
        ▼
Grafana
```

# Architecture (legacy)

```text
Azure Legacy Export
        │
        ▼
Compatibility script
        │
        ▼
FOCUS-compatible CSV
        │
        ▼
SPRUCE
```
---

# Why SPRUCE?

This project intentionally separates **billing normalization** from **observability**.

Azure Cost Management exports are designed for billing analysis, not for observability. Their schema varies depending on the export format and is not directly consumable by Prometheus-based monitoring systems.

SPRUCE bridges that gap.

It reads the Azure billing export, normalizes the data into a **FOCUS-compatible Parquet dataset**, and enriches each billing record with sustainability-related attributes derived from open environmental models.

For this project, SPRUCE is responsible for:

- normalizing Azure billing exports
- transforming them into a standardized FOCUS-compatible dataset
- enriching records with environmental indicators
- exporting the results as Parquet files

Those enriched records become the foundation for the observability pipeline implemented in this repository.

The Python exporter included here then converts the Parquet dataset into Prometheus-compatible metrics that are imported into VictoriaMetrics.

This separation keeps each component focused on a single responsibility:

| Component | Responsibility |
|-----------|----------------|
| Azure Cost Management | Billing export |
| SPRUCE | Normalization + sustainability enrichment |
| Python exporter | Prometheus metric generation |
| VictoriaMetrics | Time-series storage |
| Grafana | Visualization |

Learn more about SPRUCE:

- https://opensourcegreenops.cloud/latest/
- https://github.com/digitalpebble/spruce

---

# Why VictoriaMetrics?

Once billing data becomes metrics, it can be treated like any other operational signal.

VictoriaMetrics provides a lightweight, high-performance time-series database that is fully compatible with the Prometheus ecosystem while requiring very little operational overhead.

Instead of opening spreadsheets every month, engineers can query cloud cost and sustainability data using familiar PromQL expressions.

This enables:

- PromQL querying
- historical analysis
- label-based aggregation
- dashboards
- anomaly detection
- recording rules
- alerting
- cardinality analysis
- correlation with infrastructure telemetry

VictoriaMetrics also includes **VMUI**, an interface that makes exploring large metric sets particularly convenient.

Throughout this project you'll use VMUI to:

- discover metrics
- inspect labels
- experiment with PromQL
- explore metric cardinality
- validate the exported sustainability metrics

Learn more:

- https://github.com/VictoriaMetrics/VictoriaMetrics
- https://docs.victoriametrics.com/

---

# Getting Started

## 1. Export Azure billing data

Create an **Azure Cost Management Legacy CSV export** from your Azure subscription.

The generated CSV serves as the input for the entire pipeline.

> **Note**
>
> During development I experimented with both Azure **Legacy** and **FOCUS 1.0** exports.
>
> At the time this repository was published, the Legacy export completed the full workflow successfully. Azure FOCUS support is actively evolving within the SPRUCE project and is being validated in collaboration with the SPRUCE maintainers.

---

## 2. Prepare the SPRUCE input

Use the helper script included in this repository to convert the Azure export into the CSV format expected by SPRUCE.

```bash
python azure_legacy_to_spruce_csv.py
```

This generates:

```
outputs/spruce_input.csv
```

---

## 3. Run SPRUCE

Execute SPRUCE against the generated input file:

```bash
docker run --rm \
  -v "$(pwd)/outputs:/outputs" \
  ghcr.io/digitalpebble/spruce:latest \
  -p AZURE \
  -i /outputs/spruce_input.csv \
  -c /outputs/config.json \
  -o /outputs/result
```

SPRUCE produces a normalized Parquet dataset similar to:

```
outputs/result/
    part-xxxxxxxx.snappy.parquet
```

The dataset now contains both billing information and environmental enrichment produced by SPRUCE.

---

## 4. Start VictoriaMetrics

```bash
docker run -d \
  --name victoriametrics \
  -p 8428:8428 \
  victoriametrics/victoria-metrics
```

Open VMUI:

```
http://localhost:8428/vmui
```

---

## 5. Export Prometheus metrics

Convert the SPRUCE Parquet dataset into Prometheus metrics:

```bash
python cur_to_victoriametrics.py
```

The exporter imports all generated metrics directly into VictoriaMetrics using the Prometheus import API.

---

## 6. Start Grafana

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

Default credentials:

```
admin
admin
```

Configure a Prometheus datasource pointing to:

```
http://host.docker.internal:8428
```

(or `http://localhost:8428`, depending on your environment)

Finally, import:

```
grafana/dashboard.json
```

to explore the complete GreenOps dashboard.

---

# Repository Structure

```text
.
├── exports/
│   └── cost-reports/
│       └── azure_legacy.csv
│
├── outputs/
│   ├── spruce_input.csv
│   ├── config.json
│   └── result/
│       └── *.parquet
│
├── grafana/
│   └── dashboard.json
│
├── azure_legacy_to_spruce_csv.py
├── cur_to_victoriametrics.py
├── requirements.txt
└── README.md
```

---

# Exported Metrics

The exporter converts every enriched SPRUCE billing record into Prometheus metrics.

Rather than exposing only cloud cost, it also publishes the environmental indicators calculated by SPRUCE, allowing them to be queried exactly like any other infrastructure metric.

| Metric | Description |
|---------|-------------|
| `cloud_cost` | Monetary cost for each billing record |
| `cloud_usage_quantity` | Resource consumption quantity |
| `cloud_operational_energy_kwh` | Estimated operational energy consumption |
| `cloud_operational_emissions_co2eq_g` | Operational CO₂ emissions |
| `cloud_embodied_emissions_co2eq_g` | Embodied carbon emissions |
| `cloud_carbon_intensity` | Carbon intensity associated with the region |
| `cloud_power_usage_effectiveness` | Data center Power Usage Effectiveness (PUE) |
| `cloud_water_usage_effectiveness` | Water Usage Effectiveness (WUE) |
| `cloud_water_cooling_l` | Estimated cooling water consumption |
| `cloud_water_electricity_production_l` | Water consumed during electricity production |
| `cloud_water_consumption_stress_area_l` | Water consumption in stressed regions |
| `cloud_resource_info` | Inventory metric representing cloud resources |

Every metric shares a common set of labels that make aggregation and filtering straightforward.

Typical labels include:

- provider
- service
- category
- region
- resource_group
- sku
- resource_name

This allows PromQL queries such as:

```promql
sum by(service)(cloud_cost)
```

or

```promql
sum by(region)(cloud_operational_emissions_co2eq_g)
```

without requiring additional preprocessing.

---

# Exploring the Metrics in VMUI

Once imported into VictoriaMetrics, open VMUI:

```
http://localhost:8428/vmui
```

A good first query is:

```promql
{__name__=~"cloud_.*"}
```

This lists every metric generated by the exporter.

---

## Cost Analysis

Total cloud cost

```promql
sum(cloud_cost)
```

Cost by service

```promql
sum by(service)(cloud_cost)
```

Cost by category

```promql
sum by(category)(cloud_cost)
```

Cost by region

```promql
sum by(region)(cloud_cost)
```

Top 10 most expensive SKUs

```promql
topk(10, sum by(sku)(cloud_cost))
```

Cost by resource group

```promql
sum by(resource_group)(cloud_cost)
```

---

## Sustainability Analysis

Operational energy consumption

```promql
sum(cloud_operational_energy_kwh)
```

Operational emissions

```promql
sum(cloud_operational_emissions_co2eq_g)
```

Embodied emissions

```promql
sum(cloud_embodied_emissions_co2eq_g)
```

Carbon intensity by region

```promql
avg by(region)(cloud_carbon_intensity)
```

Average PUE

```promql
avg(cloud_power_usage_effectiveness)
```

Average WUE

```promql
avg(cloud_water_usage_effectiveness)
```

Cooling water consumption

```promql
sum(cloud_water_cooling_l)
```

Water consumed for electricity production

```promql
sum(cloud_water_electricity_production_l)
```

Water consumption in stressed regions

```promql
sum(cloud_water_consumption_stress_area_l)
```

---

## Cloud Inventory

Resources by region

```promql
count by(region)(cloud_resource_info)
```

Resources by service

```promql
count by(service)(cloud_resource_info)
```

Resources by SKU

```promql
count by(sku)(cloud_resource_info)
```

Resources by resource group

```promql
count by(resource_group)(cloud_resource_info)
```

---

# VictoriaMetrics Features Worth Exploring

Besides running PromQL queries, VMUI offers several powerful tools that help explore the dataset:

- **Metric Explorer** — discover available metrics and labels
- **Cardinality Explorer** — inspect metric cardinality and label distribution
- **Query Analyzer** — understand query execution and performance
- **Metrics Explorer** — browse metric metadata interactively

Together these tools make it easy to understand both the financial and environmental dimensions of the enriched SPRUCE dataset before building Grafana dashboards.

---

# Example Visualizations

The repository includes a ready-to-import Grafana dashboard that demonstrates how cloud billing and sustainability data can be explored using standard observability workflows.

The dashboard combines financial, operational, and environmental metrics into a single view.

## Dashboard Highlights

### Financial Overview

- 💰 Total Cloud Cost
- 📈 Cloud Cost Over Time
- 🏷️ Cost by Service
- 🌍 Cost by Region
- 📦 Cost by SKU
- 🏢 Cost by Resource Group

### Sustainability Overview

- ⚡ Operational Energy Consumption
- 🌱 Operational CO₂ Emissions
- 🏭 Embodied CO₂ Emissions
- 🌍 Carbon Intensity by Region
- 💧 Water Consumption
- ⚙️ Power Usage Effectiveness (PUE)
- 🚰 Water Usage Effectiveness (WUE)

### Resource Inventory

- Resources by Service
- Resources by Region
- Resources by SKU
- Resources by Resource Group

---

## Grafana Dashboard

<img width="1678" height="760" alt="Screenshot 2026-07-14 at 21 24 35" src="https://github.com/user-attachments/assets/20393392-33a4-402f-91a4-38941e91b798" />

<img width="1676" height="603" alt="Screenshot 2026-07-14 at 21 25 18" src="https://github.com/user-attachments/assets/7abd9245-82bb-4310-b6d6-9f19df656f82" />


---

## VictoriaMetrics VMUI

VMUI makes it easy to inspect every exported metric before building dashboards.

Use it to:

- discover metrics
- inspect labels
- validate imported data
- experiment with PromQL
- explore metric cardinality

Cardinality Explorer

<img width="1687" height="666" alt="Screenshot 2026-07-14 at 21 29 58" src="https://github.com/user-attachments/assets/adcd94ee-4889-48fb-abda-464cbd342904" />

<img width="1701" height="765" alt="Screenshot 2026-07-14 at 21 30 08" src="https://github.com/user-attachments/assets/9b7d8a79-6c52-4ca3-9084-ddb55fb81328" />

<img width="1692" height="666" alt="Screenshot 2026-07-14 at 21 30 34" src="https://github.com/user-attachments/assets/5c31e7c3-233b-4574-9e22-6685a959c6c7" />


---

# Engineering Notes

This project intentionally separates responsibilities across the pipeline.

| Component | Responsibility |
|-----------|----------------|
| Azure Cost Management | Billing export |
| SPRUCE | Billing normalization and sustainability enrichment |
| Python exporter | Prometheus metric generation |
| VictoriaMetrics | Time-series storage |
| VMUI | Interactive metric exploration |
| Grafana | Dashboards and visualization |

Keeping each component focused on a single responsibility makes the workflow easy to understand, modify, and extend.

---

# Disclaimer

This project is intended for **educational and demonstration purposes**.

It is **not** a production-ready GreenOps platform.

Some important notes:

- Azure billing data comes from Azure Cost Management exports.
- SPRUCE performs billing normalization and sustainability enrichment.
- The Prometheus exporter included in this repository was developed specifically for this demonstration.
- VictoriaMetrics stores the generated metrics.
- Grafana visualizes those metrics.
- The dashboards included here are examples designed to demonstrate how sustainability data can become part of everyday observability workflows.

This repository is **not affiliated with the SPRUCE project**, although it builds upon SPRUCE's excellent normalization and enrichment capabilities.

---

# Future Work

This project opens the door to several interesting directions.

## Better sustainability analysis

- Native Azure FOCUS support
- Multi-cloud support
- Carbon budgets
- Sustainability scorecards
- Team-level carbon reporting

## Better observability

- Recording rules
- VictoriaMetrics alerting
- Cost anomaly detection
- Carbon anomaly detection
- Forecasting cloud spend

## Kubernetes

- Namespace-level attribution
- Cluster cost analysis
- OpenCost integration
- Kubernetes carbon attribution

## OpenTelemetry

One particularly exciting direction is integrating GreenOps directly into OpenTelemetry.

Rather than exporting sustainability data as standalone metrics, cloud cost and environmental indicators could become part of a broader telemetry pipeline alongside traces, metrics, and logs, enabling richer correlations between application behavior, infrastructure usage, cloud spending, and environmental impact.

---

# Acknowledgements

A special thank you to the **SPRUCE maintainers** for their responsiveness, technical discussions, and willingness to investigate Azure billing support throughout this project.

Their feedback and collaboration helped improve both this demonstration and Azure compatibility within SPRUCE itself.

---

# License

MIT
