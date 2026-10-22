# Metro Interstate Traffic Congestion Analysis & Prediction

[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.9-E25A1C?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.65.0-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Parquet](https://img.shields.io/badge/Storage-Snappy%20Parquet-blue?style=flat)](https://parquet.apache.org/)

An enterprise-grade Big Data engineering, exploratory analytics, and machine learning application predicting hourly traffic volume on westbound Interstate 94 (Minneapolis–St. Paul, MN). The system leverages **PySpark**, **Spark SQL**, **Spark MLlib**, and **Streamlit** to ingest, sanitize, analyze, and forecast traffic flow across 48,187 hourly observations.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Architecture & Pipeline](#-architecture--pipeline)
3. [Repository Structure](#-repository-structure)
4. [Reproduction Guide (Fresh Terminal)](#-reproduction-guide-fresh-terminal)
5. [Data Quality & Cleaning Methodology](#-data-quality--cleaning-methodology)
6. [Key Exploratory Findings (EDA)](#-key-exploratory-findings-eda)
7. [Machine Learning with Spark MLlib](#-machine-learning-with-spark-mllib)
8. [Interactive Streamlit Dashboard](#-interactive-streamlit-dashboard)
9. [Operational Assumptions & Limitations](#-operational-assumptions--limitations)

---

## 🚀 Project Overview
Urban highway networks face acute congestion during weekday commute windows. This project demonstrates how distributed Big Data technologies process multi-year highway loop-detector counts joined with hourly meteorological station readings to produce robust, leak-free volume forecasts.

- **Corridor**: Westbound Interstate 94 (I-94) between Minneapolis and St. Paul, MN.
- **Timeframe**: October 2012 to September 2018 (6 years of hourly sensor records).
- **Core Challenge**: High-volume, non-linear diurnal cycles influenced by adverse weather (heavy rain, snowstorms, freezing temperatures) and statutory holidays.

---

## 🏗️ Architecture & Pipeline

```
[ Raw CSV: data/traffic_data.csv (48,204 rows) ]
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Phase 1 & 2: Data Quality & Sanitization                     │
│ • Drop 17 exact duplicate rows (preserving multi-weather)   │
│ • Flag 0.0 K temp and 9,831.3 mm rainfall sensor glitches     │
│ • Decompose timestamp into: hour, day_of_week, month, is_wknd │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
[ Cleaned Parquet: output/traffic_cleaned.parquet (48,187 rows) ]
            │                                      │
            ▼                                      ▼
┌────────────────────────────────┐   ┌────────────────────────────────┐
│ Phase 3: Distributed EDA       │   │ Phase 4: Spark MLlib Pipeline  │
│ • 24-Hour diurnal commute curve│   │ • Chronological 80/20 split    │
│ • Weekday vs. Weekend profiles │   │ • Median Imputer for nulls     │
│ • Weather & holiday impacts    │   │ • StringIndexer + OneHotEncoder│
│ • 300 DPI publication figures  │   │ • Random Forest Regressor      │
│ • Summary CSVs in output/eda/  │   │   (R² = 0.9120, MAE = 382 vph) │
└────────────────────────────────┘   └────────────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 5: Interactive Web Application (app.py)                       │
│ • Executive KPI dashboard & interactive exploratory charts          │
│ • Real-time Spark MLlib Pipeline inference for volume simulation    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
traffic-project/
├── data/
│   └── traffic_data.csv                     # Raw UCI Metro Interstate Traffic CSV (48,204 rows)
├── docs/
│   ├── data_dictionary.md                   # Column definitions, units, types, and constraints
│   ├── methodology.md                       # Comprehensive technical design and data decisions
│   └── presentation_outline.md              # 10-slide executive presentation with speaker notes
├── execution/
│   └── traffic_data_cleaning_and_analysis.ipynb # Interactive Jupyter Notebook version
├── output/
│   ├── eda/                                 # Aggregate Spark SQL CSV outputs
│   │   ├── hourly_traffic.csv
│   │   ├── weekday_weekend_traffic.csv
│   │   ├── weekday_weekend_pivot.csv
│   │   ├── monthly_traffic.csv
│   │   ├── weather_traffic.csv
│   │   ├── holiday_summary.csv
│   │   ├── specific_holidays.csv
│   │   └── traffic_summary_stats.csv
│   ├── figures/                             # 300 DPI presentation-quality visualizations
│   │   ├── 01_hourly_traffic_profile.png
│   │   ├── 02_weekday_vs_weekend_comparison.png
│   │   ├── 03_monthly_traffic_trends.png
│   │   ├── 04_weather_impact_on_traffic.png
│   │   ├── 05_holiday_traffic_comparison.png
│   │   └── 06_actual_vs_predicted_traffic.png
│   ├── models/                              # Trained Spark MLlib models and evaluation metrics
│   │   ├── model_comparison.csv
│   │   ├── test_predictions_sample.csv
│   │   └── rf_traffic_pipeline/             # Persisted fitted Spark MLlib Pipeline
│   └── traffic_cleaned.parquet/             # Snappy-compressed partitioned Parquet dataset
├── src/
│   ├── 01_data_quality.py                   # Phase 1: Ingestion, schema audit, nulls & duplicates
│   ├── 02_investigate_anomalies.py          # Phase 1: Anomaly diagnostics (temp, rain, closures)
│   ├── 03_clean_data.py                     # Phase 2: Sanitization, feature extraction & Parquet export
│   ├── 04_traffic_analysis.py               # Phase 3: Distributed EDA, Spark SQL & figure generation
│   └── 05_train_model.py                    # Phase 4: Chronological split & Spark MLlib regression
├── app.py                                   # Phase 5: Interactive Streamlit web application
├── requirements.txt                         # Python dependencies
├── .gitignore                               # Git exclusion rules
└── README.md                                # Project documentation
```

---

## 💻 Reproduction Guide (Fresh Terminal)

### 1. Prerequisites
- **Operating System**: Linux / WSL Ubuntu 22.04+
- **Java**: OpenJDK 1.8.0 or 11+
- **Apache Spark**: Spark 3.5.x
- **Python**: Python 3.10+

### 2. Configure Environment Variables
Ensure `SPARK_HOME` and `PYTHONPATH` are configured in your shell:
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=$HOME/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH"
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Execute the End-to-End Pipeline

Execute each pipeline stage sequentially:

```bash
# Step 1: Run Data Quality Audit
python3 src/01_data_quality.py

# Step 2: Investigate Domain Anomalies
python3 src/02_investigate_anomalies.py

# Step 3: Clean, Sanitize, and Persist Cleaned Parquet Data
python3 src/03_clean_data.py

# Step 4: Run Distributed EDA and Generate Figures
python3 src/04_traffic_analysis.py

# Step 5: Train MLlib Pipeline & Evaluate on Out-of-Time Test Set
python3 src/05_train_model.py
```

### 5. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧹 Data Quality & Cleaning Methodology

| Anomaly Observed | Root Cause | Impact | Cleaning Action |
| :--- | :--- | :--- | :--- |
| **17 Duplicate Rows** | Upstream telemetry transmission replay | Redundant exact matches across all 9 columns | Dropped via `dropDuplicates()`. Repeated timestamps with differing weather conditions were preserved. |
| **`temp = 0.0 K` (10 rows)** | Temperature sensor default/unplugged state | Absolute zero ($-273.15^\circ\text{C}$) severely distorts regression gradients | Converted to `NULL`. Imputed with training set median in Spark MLlib pipeline. |
| **`rain_1h = 9831.3 mm`** | Gauge malfunction on 2016-07-11 17:00 | Physically unviable rainfall (> 9.8 meters/hour) | Converted values > 100 mm to `NULL`. Dry zeros (0.0 mm) were strictly preserved. |
| **Zero Snowfall (48,124 rows)** | Normal dry weather in Minnesota | Heavy zero-inflation | Retained as legitimate zeros; positive values preserved. |
| **Zero Traffic (2 rows)** | Road closure / sensor outage on 2016-07-23 | Operational highway events | Retained to maintain full empirical integrity. |

---

## 📊 Key Exploratory Findings (EDA)

1. **Commute Rush Hours**:
   - **Morning Peak**: 7:00 AM – 8:00 AM (averaging **6,030 vph** on weekdays).
   - **Evening Peak**: 4:00 PM – 5:00 PM (averaging **6,189 vph** on weekdays).
   - **Night Valley**: 2:00 AM – 4:00 AM (dropping to **300–400 vph**).
2. **Weekday vs. Weekend Separation**:
   - **Weekdays**: Pronounced bimodal surge curves coinciding with employment commuting.
   - **Weekends**: Smooth unimodal plateau between 12:00 PM and 5:00 PM (~4,350 vph) with no morning rush.
3. **Holiday Reductions**:
   - Normal working days average **3,263 vph**, whereas statutory holidays drop by **73.5%** to **865 vph**.
4. **Seasonal Fluctuations**:
   - Summer and early autumn (June–October) experience peak traffic (~3,390 vph), while winter (December–January) registers reduced flow (~3,024 vph).

---

## 🤖 Machine Learning with Spark MLlib

### Validation Strategy: Chronological Split
To prevent temporal data leakage, records were ordered chronologically and split at the 80th percentile:
- **Training Set (80.0%)**: 38,546 observations (`2012-10-02 09:00:00` to `2017-11-01 18:00:00`)
- **Testing Set (20.0%)**: 9,641 observations (`2017-11-01 19:00:00` to `2018-09-30 23:00:00`)

### Spark MLlib Pipeline
1. `Imputer`: Median imputation for `temp` and `rain_1h` nulls.
2. `StringIndexer` & `OneHotEncoder`: Encodes `weather_main` and `holiday`.
3. `VectorAssembler`: Assembles 10 feature inputs into an assembled feature vector.

### Model Comparison Results on Out-of-Time Test Set

| Model Architecture | Test RMSE | Test MAE | Test R² | Error Reduction |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline Linear Regression** | 1,759.91 vph | 1,540.79 vph | 0.1997 | Baseline |
| **Random Forest Regressor (Trees=60, Depth=12)** | **583.51 vph** | **382.78 vph** | **0.9120** | **-75.2% MAE** |

---

## 🖥️ Interactive Streamlit Dashboard (`app.py`)

The Streamlit web application provides:
- **Executive KPI Cards**: Real-time summary metrics on observations, averages, and model scores.
- **Interactive EDA Explorer**: Interactive multi-series charts for hourly, monthly, and weather distributions.
- **Model Evaluation Lab**: Out-of-time test set comparisons and 7-day actual vs. predicted curves.
- **Live Traffic Predictor**: Interactive sliders and selectors that call the cached Spark MLlib pipeline for instant volume prediction and congestion grading (Light Flow, Moderate, Heavy, Severe).

---

## ⚠️ Operational Assumptions & Limitations

1. **Volume vs. Speed**: The model predicts hourly vehicle count (throughput), **not** road speed (mph) or travel delay (minutes). In total gridlock, volume can paradoxically decrease as traffic comes to a complete standstill.
2. **Correlation vs. Causation**: Weather associations (e.g. high volume during "Clouds") reflect commute timing rather than weather-induced travel demand.
3. **Unforeseen Incidents**: The model cannot predict emergency closures, crashes, or unannounced construction detours.
4. **Geographic Scope**: Trained specifically on westbound I-94 in Minneapolis-St. Paul; retraining is required for other corridors.

---

## 📄 License
This project is open-source under the MIT License. Data courtesy of the Minnesota Department of Transportation via the UCI Machine Learning Repository.
