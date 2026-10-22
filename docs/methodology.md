# Technical Methodology: Traffic Congestion Analysis & Prediction Using PySpark

## 1. System Architecture & Big Data Pipeline

The end-to-end architecture is organized into 5 sequential stages built on **Apache Spark 3.5.9** (PySpark, Spark SQL, Spark MLlib) and Python 3.10:

```
[ Raw CSV Data: data/traffic_data.csv (48,204 rows) ]
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 1 & 2: Data Quality, Sanitization & Cleaning      │
│ - Exact deduplication (17 rows dropped)                │
│ - Physical sensor sanitization (temp 0K, rain > 100mm)  │
│ - Temporal feature engineering (hour, dow, month, etc.) │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
[ Cleaned Parquet Storage: output/traffic_cleaned.parquet (48,187 rows) ]
            │                                      │
            ▼                                      ▼
┌────────────────────────────────┐   ┌────────────────────────────────┐
│ Phase 3: Distributed EDA       │   │ Phase 4: Spark MLlib Pipeline  │
│ - Diurnal rush-hour profiles   │   │ - Chronological 80/20 split    │
│ - Weekday vs. Weekend curves   │   │ - Train: Oct 2012 - Nov 2017   │
│ - Meteorological impact        │   │ - Test:  Nov 2017 - Sep 2018   │
│ - Holiday volume analysis      │   │ - Median Imputer, OneHotEnc    │
│ - Aggregate CSVs & 300 DPI PNG │   │ - Baseline LR vs Random Forest │
└────────────────────────────────┘   └────────────────────────────────┘
                                                   │
                                                   ▼
                                     [ Fitted Pipeline Artifact: ]
                                     [ output/models/rf_pipeline ]
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 5: Interactive Streamlit Web Application (app.py)             │
│ - Executive KPI dashboard                                           │
│ - Interactive analytics & pre-rendered charts                       │
│ - Real-time MLlib pipeline inference & congestion grading           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Cleaning & Sanitization Decisions

1. **Deduplication Rationale**:
   - Out of 48,204 raw records, exactly **17 duplicate rows** had identical values across all 9 fields.
   - These 17 copies were verified as transmission artifacts and safely dropped.
   - Crucially, rows with identical timestamps but differing weather conditions (e.g., simultaneous Mist and Rain) were **strictly preserved** because they represent multi-category meteorological events reported at the same hour.
2. **Temperature Anomaly (0.0 Kelvin)**:
   - 10 records recorded `temp = 0.0`. In Kelvin, 0.0 K is absolute zero ($-273.15^\circ\text{C}$), which is physically impossible in Minnesota ambient weather.
   - Setting these to `NULL` prevents skewing the regression baseline and enables rigorous median imputation within the ML pipeline.
3. **Rainfall Anomaly (9831.3 mm/h)**:
   - On `2016-07-11 17:00:00`, `rain_1h = 9831.3` mm was recorded. A rainfall depth of nearly 10 meters in a single hour is physically unviable and reflects gauge telemetry failure.
   - Values exceeding 100 mm were converted to `NULL` to avoid severe outlier distortion.
4. **Preservation of Valid Zeros**:
   - `rain_1h = 0.0` (dry conditions) and `snow_1h = 0.0` (no snowfall in 48,124 observations) are legitimate physical states and were strictly retained.
   - Two records with `traffic_volume = 0` occurred on `2016-07-23` at 18:00 and 23:00, representing temporary interstate closures/sensor outages; these were preserved to maintain realistic operational fidelity.

---

## 3. Exploratory Data Analysis & Statistical Principles

1. **Spark SQL Aggregations**:
   - All aggregations were executed distributedly using Spark SQL temp views (`traffic`) and PySpark DataFrame operations (`groupBy`, `agg`, `pivot`).
2. **Avoiding Small Group Fallacies**:
   - Individual statutory holidays represent only 5 to 7 hourly observations each across the 6-year span. While individual holiday averages were tabulated, conclusions were drawn from the broader aggregate comparison of **Regular Days (48,126 observations)** vs. **Holidays (61 observations)**.
3. **Association vs. Causation**:
   - High traffic volumes under "Clouds" or "Clear" weather coincide with morning/afternoon commute hours when driving demand is structurally elevated. Weather descriptions must be understood as contemporaneous environmental conditions, not sole causal drivers of interstate demand.

---

## 4. Machine Learning Methodology (Spark MLlib)

### A. Chronological Split (No Temporal Leakage)
Time-series forecasting cannot rely on random cross-validation, as future records would leak into training estimators. 
- **Training Set (80.0%)**: 38,546 observations spanning `2012-10-02 09:00:00` to `2017-11-01 18:00:00`.
- **Testing Set (20.0%)**: 9,641 observations spanning `2017-11-01 19:00:00` to `2018-09-30 23:00:00`.

### B. Pipeline Transformations
All transformers were fit strictly on `train_df`:
- `Imputer`: Median imputation for `temp` and `rain_1h` nulls.
- `StringIndexer` & `OneHotEncoder`: Encodes `weather_main` and `holiday`.
- `VectorAssembler`: Compiles 10 feature inputs into an assembled feature vector.

### C. Models Trained & Compared
1. **Baseline**: Linear Regression (`regParam=0.1`, `maxIter=50`).
2. **Ensemble**: Random Forest Regressor (`numTrees=60`, `maxDepth=12`, `seed=42`).

### D. Verified Test Set Results

| Model Architecture | Test RMSE (vph) | Test MAE (vph) | Test R² |
| :--- | :---: | :---: | :---: |
| **Baseline Linear Regression** | 1,759.91 | 1,540.79 | 0.1997 |
| **Random Forest Regressor** | **583.51** | **382.78** | **0.9120** |

The Random Forest model captures the pronounced non-linear diurnal and calendar dynamics, reducing prediction error by **75.1%** compared to the linear baseline.
