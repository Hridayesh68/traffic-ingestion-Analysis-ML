# Presentation: Traffic Congestion Analysis & Prediction Using PySpark

**Project:** Metro Interstate I-94 Traffic Volume Analytics & Machine Learning Pipeline  
**Author:** Senior Data Engineer & Data Scientist  
**Technology Stack:** Apache Spark 3.5.9 (PySpark, Spark SQL, Spark MLlib), Python 3.10, Streamlit, Parquet  

---

## Slide 1: Title & Problem Statement
- **Title:** Intelligent Traffic Congestion Analysis & Real-Time Flow Prediction
- **Subtitle:** Scalable Big Data Pipeline & Machine Learning Using Apache PySpark
- **Problem Statement:** 
  - Urban interstate corridors experience severe capacity constraints during peak commute hours.
  - Traffic management authorities require accurate, real-time volume forecasts to optimize ramp metering, dynamic tolling, and lane allocations.
  - Challenge: Processing large-scale time-series sensor telemetry joined with fluctuating weather phenomena requires resilient Big Data infrastructure.
- **Presenter Notes:** Welcome stakeholders. Today we present an end-to-end data engineering and machine learning solution built on Apache Spark that transforms raw highway sensor and weather telemetry into an actionable predictive application.

---

## Slide 2: Motivation & Project Objectives
- **Key Objectives:**
  1. **Big Data Data Quality & Sanitization:** Detect, diagnose, and treat sensor defaults, extreme precipitation anomalies, and duplicate records across 48,000+ hourly observations.
  2. **Exploratory Data Analysis at Scale:** Employ Spark SQL and PySpark DataFrames to isolate diurnal rush-hour dynamics, weekend leisure behaviors, and meteorological patterns.
  3. **High-Performance Machine Learning:** Build a Spark MLlib Pipeline using strict chronological train/test splitting to predict hourly volume without temporal data leakage.
  4. **Interactive Decision Dashboard:** Deliver a low-latency Streamlit application allowing stakeholders to explore historical insights and simulate real-time traffic scenarios.
- **Presenter Notes:** Emphasize that the project moves beyond toy analytics to demonstrate a presentation-ready enterprise pipeline adhering to strict data engineering and ML best practices.

---

## Slide 3: Dataset Source & Architecture
- **Data Source:** UCI Machine Learning Repository / Minnesota Department of Transportation (MnDOT).
- **Corridor:** Westbound Interstate 94 (I-94) connecting Minneapolis and St. Paul, MN.
- **Scope:** Hourly observations from October 2012 through September 2018 (6 full years).
- **Core Attributes:**
  - **Temporal:** `date_time` (timestamp)
  - **Target:** `traffic_volume` (hourly vehicle throughput, range: 0–7,280 vph)
  - **Meteorological:** `temp` (Kelvin), `rain_1h` (mm), `snow_1h` (mm), `clouds_all` (%), `weather_main`, `weather_description`
  - **Calendar:** `holiday` (US Federal / Minnesota state holiday name or `'None'`)
- **Presenter Notes:** The dataset pairs continuous traffic loop-detector counts with weather station telemetry, providing an ideal testbed for modeling multi-variate time-series flow.

---

## Slide 4: Data Quality Findings & Cleaning Methodology
- **Quality Audit Findings:**
  - **Initial Nulls:** Zero schema-level nulls in raw CSV, but domain anomalies existed.
  - **Deduplication:** Exactly 17 complete duplicate records were identified and dropped (48,204 $\rightarrow$ 48,187 rows).
  - **Multi-Weather Preservation:** Legitimate repeated timestamps with differing weather descriptions (e.g. simultaneous Mist + Rain) were strictly preserved.
  - **Sensor Anomaly 1 (`temp = 0.0 K`):** 10 instances of absolute zero ($-273.15^\circ\text{C}$) flagged as sensor default faults $\rightarrow$ converted to `NULL` for median imputation.
  - **Sensor Anomaly 2 (`rain_1h = 9831.3 mm`):** Unphysical 9.8-meter deluge on 2016-07-11 flagged as gauge failure $\rightarrow$ converted to `NULL`.
  - **Physical Zeros Preserved:** Dry rainfall (0.0 mm), dry snowfall (48,124 zero rows), and highway closure traffic volume (2 zero rows) strictly maintained.
- **Presenter Notes:** Transparently explain our decision framework: we do not blindly drop rows; we repair corrupted sensor values while preserving operational facts.

---

## Slide 5: System Architecture & Technologies
- **Distributed Computing Engine:** Apache Spark 3.5.9 on WSL Ubuntu.
- **Storage Layer:** Columnar Parquet with Snappy compression (`output/traffic_cleaned.parquet`), yielding fast I/O throughput and predicate pushdown.
- **Analytical Engine:** PySpark DataFrame API combined with ANSI Spark SQL temp views (`traffic`).
- **Modeling Framework:** Spark MLlib Pipelines integrating `Imputer`, `StringIndexer`, `OneHotEncoder`, and `VectorAssembler`.
- **Application Layer:** Streamlit interactive web dashboard utilizing cached pipeline inference.
- **Presenter Notes:** Highlighting the decoupled architecture: data cleaning and model training run as distributed batch jobs, while the dashboard consumes optimized Parquet artifacts and pre-fitted models without redundant retraining.

---

## Slide 6: Exploratory Analysis Findings & Traffic Dynamics
- **Finding 1 (Diurnal Commute Profile):**
  - **Morning Peak:** 7:00 AM – 8:00 AM (~4,750 vph overall, ~6,030 vph on weekdays).
  - **Evening Peak:** 4:00 PM – 5:00 PM (~4,850 vph overall, ~6,190 vph on weekdays).
  - **Overnight Valley:** 2:00 AM – 4:00 AM drops to 350–500 vph.
- **Finding 2 (Weekday vs. Weekend Contrast):**
  - Weekdays exhibit a classic **bimodal curve** driven by workforce commute.
  - Weekends exhibit a **unimodal plateau** rising smoothly from 11:00 AM to 5:00 PM (~4,350 vph).
- **Finding 3 (Holiday Reductions):**
  - Statutory holidays experience a **73.5% reduction** in average volume (865 vph vs. 3,263 vph on regular days).
- **Finding 4 (Seasonality):**
  - Peak traffic occurs in summer and autumn (June–October, ~3,390 vph); winter slumps in Dec–Jan (~3,024 vph).
- **Presenter Notes:** Walk the audience through the generated charts (`output/figures/01_hourly_traffic_profile.png` and `02_weekday_vs_weekend_comparison.png`). Note: correlation between weather and traffic reflects commute timing rather than direct causality.

---

## Slide 7: Machine Learning Methodology & Chronological Split
- **Guarding Against Data Leakage:**
  - Random K-fold splitting on time series introduces future lookahead bias.
  - Implemented strict **chronological 80%/20% split**:
    - **Training Set (80.0%):** 38,546 observations (Oct 2, 2012 – Nov 1, 2017)
    - **Testing Set (20.0%):** 9,641 observations (Nov 1, 2017 – Sep 30, 2018)
- **MLlib Feature Pipeline:**
  - Imputation: Median replacement for missing temperature and rainfall.
  - Encodings: `weather_main` and `holiday` encoded via StringIndexer + OneHotEncoder.
  - Assembly: 10 temporal and weather features combined into a unified Spark `DenseVector`.
- **Presenter Notes:** Emphasize that all encoders and imputers were fitted strictly on training data and applied out-of-sample to the test data.

---

## Slide 8: Model Performance & Evaluation Metrics
- **Models Evaluated on Out-of-Time Test Set:**
  1. Baseline Linear Regression
  2. Random Forest Regressor (`numTrees=60`, `maxDepth=12`)
- **Verified Evaluation Metrics:**

| Metric | Baseline Linear Regression | Random Forest Regressor | Improvement |
| :--- | :---: | :---: | :---: |
| **Root Mean Squared Error (RMSE)** | 1,759.91 vph | **583.51 vph** | **66.8% reduction** |
| **Mean Absolute Error (MAE)** | 1,540.79 vph | **382.78 vph** | **75.2% reduction** |
| **Coefficient of Determination ($R^2$)** | 0.1997 | **0.9120** | **+0.712 ($R^2 > 0.91$)** |

- **Actual vs. Predicted Alignment:**
  - The Random Forest model closely tracks both the morning rush surges and weekend midday plateaus across consecutive weeks.
- **Presenter Notes:** Refer to `output/figures/06_actual_vs_predicted_traffic.png`. The non-linear ensemble successfully decodes the complex interactions between calendar features and hour of the day.

---

## Slide 9: Operational Limitations & Risk Factors
- **Critical Model Boundaries:**
  1. **Volume vs. Speed:** The model predicts **vehicle volume throughput (vph)**, not vehicular travel speed (mph) or road congestion duration (minutes).
  2. **Gridlock Paradox:** During catastrophic incidents or gridlock, volume drops because vehicles are stopped. Low volume does not always imply free flow.
  3. **No Unscheduled Incident Telemetry:** Accidents, construction detours, and emergency closures are not captured in the raw dataset.
  4. **Geographic Specificity:** The model applies strictly to westbound I-94 between the Twin Cities and cannot be transferred without retraining to eastbound corridors or other metropolitan areas.
- **Presenter Notes:** Demonstrates technical maturity. Being explicit about limitations builds trust with transportation engineering stakeholders.

---

## Slide 10: Conclusion & Next Steps
- **Key Takeaways:**
  - Successfully built a reproducible Big Data pipeline utilizing PySpark, Spark SQL, Parquet, and MLlib.
  - Reached **$R^2 = 0.912$** and **MAE = 382 vph** on unseen chronological test data.
  - Delivered an interactive Streamlit application (`app.py`) for live stakeholder simulation.
- **Future Improvements:**
  - Integrate real-time Doppler radar telemetry via streaming Kafka ingestion.
  - Incorporate upstream loop-detector lag features (e.g. Volume at $t-1$, $t-2$) for autoregressive forecasting.
  - Deploy containerized pipeline via Docker and Kubernetes for automated batch scoring.
- **Presenter Notes:** Thank the audience. Open the floor for questions and transition to a live demonstration of the Streamlit dashboard (`streamlit run app.py`).
