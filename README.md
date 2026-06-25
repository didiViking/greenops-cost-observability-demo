# 🌱 GreenOps Observability Demo (CUR → VictoriaMetrics → Grafana)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-demo-orange.svg)
![Stack](https://img.shields.io/badge/stack-spark%20%7C%20victoriametrics%20%7C%20grafana-green.svg)

A GreenOps observability pipeline that transforms AWS Cost and Usage Report (CUR)-like data into cost and carbon metrics, then visualizes them using **VictoriaMetrics + Grafana**.

This project demonstrates how sustainability can be treated as a **first-class observability signal**.

## 🧩 Role of SPRUCE in this GreenOps Architecture

This project follows a cloud-native observability pattern inspired by open source ecosystem tools, where data generation, processing, and observability are clearly separated into independent layers.

Within this architecture, **SPRUCE is used strictly as a synthetic data generation and normalization layer**.

What is SPRUCE? Check it out: 👉 https://opensourcegreenops.cloud/latest/, 👉 https://github.com/digitalpebble/spruce.

---

### 📦 Output Contract

SPRUCE produces a structured dataset containing cloud usage and cost attributes such as:

- `product_region_code`
- `line_item_product_code`
- `line_item_usage_account_id`
- `line_item_usage_start_date`
- `line_item_usage_end_date`
- `line_item_unblended_cost`

This dataset acts as the **source of truth for downstream GreenOps metrics generation**.

---

### 🔄 Downstream Flow

After SPRUCE completes dataset generation, the pipeline continues as follows:

1. **SPRUCE (Batch Processing Layer)**
   - Produces CUR-like Parquet dataset

2. **Python Transformation Layer (Metrics Adapter)**
   - Converts cost data into Prometheus-compatible metrics
   - Aggregates by service, region, and account
   - Enriches metrics with CO₂ emission factors

3. **VictoriaMetrics (Observability Storage Layer)**
   - Stores time-series cost and carbon metrics
   - Provides PromQL-compatible query interface

4. **Grafana (Visualization Layer)**
   - Displays GreenOps dashboards
   - Enables cost and carbon observability across services

---

### 🧭 Design Principle

This architecture follows a typical separation of concerns:

- **Batch/Data Generation Layer → SPRUCE**
- **Metrics Transformation Layer → Python exporter**
- **Time-Series Storage Layer → VictoriaMetrics**
- **Visualization Layer → Grafana**

This separation ensures the system remains:
- Modular
- Reproducible
- Observability-native
- Vendor-neutral

---

### 🌍 In this GreenOps demo:

- SPRUCE is the **data plane simulator**
- VictoriaMetrics is the **metrics backbone**
- Grafana is the **insight layer**

Together, they form a lightweight cloud-native observability pipeline for cost and carbon intelligence.

---

## 🏗️ Architecture

```text
┌──────────────────────┐
│   CUR (Spark job)    │
└─────────┬────────────┘
          ↓
┌──────────────────────┐
│  Parquet dataset     │
└─────────┬────────────┘
          ↓
┌──────────────────────┐
│ Python metric export │
│ (CUR → Prom metrics) │
└─────────┬────────────┘
          ↓
┌──────────────────────┐
│ VictoriaMetrics      │
└─────────┬────────────┘
          ↓
┌──────────────────────┐
│ Grafana dashboards   │
└──────────────────────┘

```

---

## 📊 Metrics Model

### 💰 Cost metrics

- `aws_cost_total`
- `aws_cost_service`
- `aws_cost_region`

### 🌍 Carbon metric

- `aws_co2_estimate`

Derived from:

aws_co2_estimate = aws_cost_total × region_emission_factor

---

## 📁 Repository structure

```text
spruce-greenops-vm-demo/
┌──────────────────────────────┐
│ generate_cur.py             │
│ (Spark CUR generator)       │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│ cur_to_victoriametrics.py   │
│ (CUR → Prometheus metrics)  │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│ grafana/                    │
│ └── dashboard.json          │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│ curs/                       │
│ ├── part-*.parquet          │
│ └── _SUCCESS                │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│ output/                     │
│ (optional artifacts)        │
└──────────────────────────────┘
```

---

## 🚀 Getting Started

---

### 1. Clone repo and enter directory

git clone <your-repo-url>
cd spruce-greenops-vm-demo

---

### 2. Create Python environment (optional but recommended)

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install pyspark requests pandas

---

### 3. Generate CUR dataset

python generate_cur.py

Expected output:
✔ CUR dataset written to: curs

Check output:

ls curs

---

### 4. Start VictoriaMetrics

docker run -d --name victoriametrics -p 8428:8428 victoriametrics/victoria-metrics

Verify:

http://localhost:8428/vmui

---

### 5. Push CUR metrics to VictoriaMetrics

pip install requests
python cur_to_victoriametrics.py

---

### 6. Validate ingestion in VMUI

Open:
http://localhost:8428/vmui

Query:

{__name__=~".*cost.*"}

Expected metrics:
- aws_cost_total
- aws_cost_service
- aws_cost_region
- aws_co2_estimate

Example from vmui query `sum(aws_cost_total) / sum(aws_co2_estimate)`


<img width="1687" height="819" alt="Screenshot 2026-06-25 at 11 55 51" src="https://github.com/user-attachments/assets/470dd0b1-233c-40d9-9d29-ef84cd93b42f" />

Example from vmui's Cardinality Explorer for `aws_co2_estimate` metric

<img width="1682" height="971" alt="Screenshot 2026-06-25 at 12 02 13" src="https://github.com/user-attachments/assets/f37bdee6-e8d8-4ca0-bc78-c6ae280fd885" />



---

### 7. Start Grafana

docker run -d --name grafana -p 3000:3000 grafana/grafana

Login:
http://localhost:3000
admin / admin

---

### 8. Add a Prometheus data source:

http://localhost:8428

---

### 9. Import dashboard:

grafana/dashboard.json

---

## 📈 Example Queries

### Total cost

sum(aws_cost_total)

### Cost by service

sum by (service) (aws_cost_service)

### CO₂ by region

sum by (region) (aws_co2_estimate)

### GreenOps efficiency score

sum(aws_cost_total) / sum(aws_co2_estimate)

---

## 📊 Suggested Grafana Dashboard

Panels:

- 💰 Total Cost (Stat)
- 🌍 Total CO₂ (Stat)
- 📈 Cost over time (Time series)
- 📈 CO₂ over time (Time series)
- ☁️ Cost by service (Bar chart)
- 🌍 CO₂ by region (Heatmap)
- ⚡ Efficiency score (Stat panel)

Below an example from my GreenOps CUR Dashboard

<img width="1689" height="817" alt="Screenshot 2026-06-25 at 10 07 49" src="https://github.com/user-attachments/assets/fdda7ce0-d409-424f-b26f-035f1ffbb735" />


---

## ⚠️ Disclaimer

This project does **not** use real AWS Cost and Usage Report (CUR) data.

The dataset is synthetically generated for demonstration and educational purposes using Apache Spark. Cost metrics, carbon estimates, and GreenOps dashboards shown in this repository are intended to demonstrate an observability workflow and should not be interpreted as accurate cloud billing or carbon accounting results.

This project is inspired by the ideas presented by the SPRUCE project but does not reproduce SPRUCE's complete functionality, data model, enrichment pipeline, or carbon accounting methodology.

This project uses a set of custom-defined observability metrics and queries to demonstrate a GreenOps pipeline built on open source tools.

The PromQL queries used in Grafana and VictoriaMetrics (such as cost aggregation, regional breakdowns, and carbon efficiency calculations) are **not sourced from Spruce or any upstream project**.

### 🧠 Origin of the metrics and queries

The following elements were designed specifically for this demo:

- Metric names:
  - `aws_cost_total`
  - `aws_cost_service`
  - `aws_cost_region`
  - `aws_co2_estimate`

- Derived GreenOps model:
  - `aws_co2_estimate = aws_cost_total × region_emission_factor`

- Observability queries used in VictoriaMetrics and Grafana dashboards:
  - cost aggregation queries
  - region/service breakdowns
  - CO₂ estimation queries
  - efficiency ratio calculations (cost vs carbon)

These were created as part of a **custom GreenOps observability model** built for this demonstration project.

### 🧩 Role of SPRUCE

SPRUCE is used only as a **synthetic CUR-like data generator and preprocessing layer**. It is responsible for producing structured cost and usage datasets, but it does not define:

- Prometheus/VictoriaMetrics metric naming
- Carbon estimation logic
- Dashboard queries
- Observability model design

### 🌱 Purpose of this project

This repository is intended as a **reference implementation of GreenOps observability**, showing how:

- cost data can be transformed into metrics
- carbon impact can be modeled from usage signals
- open source observability tools can be composed into a sustainability pipeline

It is not intended to replicate or extend SPRUCE functionality, but to demonstrate how its output can be used in downstream observability systems.

--- 

## 🌍 Why this matters

Cloud sustainability is usually invisible.

This project shows that:

- Cost and carbon can be unified under observability
- Emissions can be derived from usage signals
- Infrastructure decisions can be made “green-aware”

---

## ⚡ Why VictoriaMetrics

- High-performance time-series engine
- Low resource usage (efficient footprint)
- PromQL compatible
- Ideal for cost + sustainability metrics

---

## 🧭 Future Work

- Real AWS CUR ingestion
- Kubernetes workload carbon tracking
- Carbon budgets per team/service
- Alerting on emission spikes
- Multi-cloud GreenOps comparison

---

## 📜 License

MIT
