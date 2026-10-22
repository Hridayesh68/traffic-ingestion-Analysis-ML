"""
Phase 4: Machine Learning Pipeline using Spark MLlib
---------------------------------------------------
This script trains and evaluates regression models to predict traffic_volume:
1. Chronological Train/Test Split (80% Train, 20% Test) respecting time-series ordering.
2. Spark MLlib Pipeline:
   - Median Imputation for sanitized nulls ('temp', 'rain_1h').
   - Categorical Encoding ('weather_main', 'holiday') using StringIndexer and OneHotEncoder.
   - VectorAssembler to construct feature vectors from numeric and encoded columns.
3. Baseline Model: Linear Regression.
4. Advanced Model: Random Forest Regressor.
5. Evaluation Metrics: MAE, RMSE, and R2 on the out-of-time test set.
6. Artifact Persistence:
   - Fitted Random Forest Pipeline saved to output/models/rf_traffic_pipeline
   - Model metrics comparison table saved to output/models/model_comparison.csv
   - Test predictions saved to output/models/test_predictions.parquet
   - Actual vs. Predicted evaluation chart saved to output/figures/06_actual_vs_predicted_traffic.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, unix_timestamp, from_unixtime, expr, round as spark_round
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Imputer, StringIndexer, OneHotEncoder, VectorAssembler
)
from pyspark.ml.regression import (
    LinearRegression, RandomForestRegressor
)
from pyspark.ml.evaluation import RegressionEvaluator

def train_and_evaluate():
    # 1. Initialize SparkSession
    spark = (
        SparkSession.builder
        .appName("TrafficMLlibTraining")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Ensure output directories exist
    os.makedirs("output/models", exist_ok=True)
    os.makedirs("output/figures", exist_ok=True)

    # 2. Load Cleaned Dataset
    parquet_path = "output/traffic_cleaned.parquet"
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {parquet_path}. Run src/03_clean_data.py first.")

    print(f"Loading data from {parquet_path}...")
    df = spark.read.parquet(parquet_path)
    total_count = df.count()
    print(f"Total observations loaded: {total_count:,}")

    # 3. Chronological Train / Test Split (Strict 80% / 20%)
    # NOTE: Time series observations MUST NOT be randomly shuffled to prevent temporal data leakage.
    print("\n--- Performing Chronological Split ---")
    cutoff_ts = (
        df.select(expr("percentile_approx(unix_timestamp(date_time), 0.80)"))
        .collect()[0][0]
    )
    
    train_df = df.filter(unix_timestamp("date_time") <= cutoff_ts).cache()
    test_df = df.filter(unix_timestamp("date_time") > cutoff_ts).cache()

    train_count = train_df.count()
    test_count = test_df.count()

    train_start = train_df.selectExpr("min(date_time)").collect()[0][0]
    train_end = train_df.selectExpr("max(date_time)").collect()[0][0]
    test_start = test_df.selectExpr("min(date_time)").collect()[0][0]
    test_end = test_df.selectExpr("max(date_time)").collect()[0][0]

    print(f"Training set: {train_count:,} records ({train_count / total_count * 100:.1f}%) | {train_start} to {train_end}")
    print(f"Testing set:  {test_count:,} records ({test_count / total_count * 100:.1f}%) | {test_start} to {test_end}")

    # 4. Feature Transformations & Pipeline Construction
    # Feature columns:
    # Continuous & discrete numeric: hour, day_of_week, month, is_weekend, temp, rain_1h, snow_1h, clouds_all
    # Categorical: weather_main, holiday

    # A. Imputer for missing numeric features (fit on train only)
    imputer = Imputer(
        inputCols=["temp", "rain_1h"],
        outputCols=["temp_imputed", "rain_1h_imputed"],
        strategy="median"
    )

    # B. String Indexers
    weather_indexer = StringIndexer(
        inputCol="weather_main",
        outputCol="weather_main_idx",
        handleInvalid="keep"
    )

    holiday_indexer = StringIndexer(
        inputCol="holiday",
        outputCol="holiday_idx",
        handleInvalid="keep"
    )

    # C. One-Hot Encoders
    encoder = OneHotEncoder(
        inputCols=["weather_main_idx", "holiday_idx"],
        outputCols=["weather_main_vec", "holiday_vec"],
        handleInvalid="keep"
    )

    # D. Vector Assembler
    feature_cols = [
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "temp_imputed",
        "rain_1h_imputed",
        "snow_1h",
        "clouds_all",
        "weather_main_vec",
        "holiday_vec"
    ]

    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features"
    )

    # 5. Define Models
    # Model 1: Baseline Linear Regression
    lr = LinearRegression(
        featuresCol="features",
        labelCol="traffic_volume",
        maxIter=50,
        regParam=0.1
    )

    # Model 2: Random Forest Regressor
    rf = RandomForestRegressor(
        featuresCol="features",
        labelCol="traffic_volume",
        numTrees=60,
        maxDepth=12,
        seed=42
    )

    # Construct Pipelines
    lr_pipeline = Pipeline(stages=[imputer, weather_indexer, holiday_indexer, encoder, assembler, lr])
    rf_pipeline = Pipeline(stages=[imputer, weather_indexer, holiday_indexer, encoder, assembler, rf])

    # 6. Train Models
    print("\n--- Training Baseline Linear Regression Model ---")
    lr_model = lr_pipeline.fit(train_df)

    print("--- Training Random Forest Regressor Model ---")
    rf_model = rf_pipeline.fit(train_df)
    print("Model training completed successfully!")

    # 7. Evaluate on Out-of-Time Test Set
    evaluator_rmse = RegressionEvaluator(labelCol="traffic_volume", predictionCol="prediction", metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol="traffic_volume", predictionCol="prediction", metricName="mae")
    evaluator_r2 = RegressionEvaluator(labelCol="traffic_volume", predictionCol="prediction", metricName="r2")

    print("\n--- Evaluating Models on Test Set ---")
    # Linear Regression predictions
    lr_preds = lr_model.transform(test_df)
    lr_rmse = evaluator_rmse.evaluate(lr_preds)
    lr_mae = evaluator_mae.evaluate(lr_preds)
    lr_r2 = evaluator_r2.evaluate(lr_preds)

    # Random Forest predictions
    rf_preds = rf_model.transform(test_df)
    rf_rmse = evaluator_rmse.evaluate(rf_preds)
    rf_mae = evaluator_mae.evaluate(rf_preds)
    rf_r2 = evaluator_r2.evaluate(rf_preds)

    # Comparison DataFrame
    results_data = [
        {"Model": "Baseline Linear Regression", "RMSE": round(lr_rmse, 2), "MAE": round(lr_mae, 2), "R2": round(lr_r2, 4)},
        {"Model": "Random Forest Regressor (Trees=60, Depth=12)", "RMSE": round(rf_rmse, 2), "MAE": round(rf_mae, 2), "R2": round(rf_r2, 4)}
    ]
    comparison_df = pd.DataFrame(results_data)
    print("\n" + "=" * 65)
    print("TEST SET EVALUATION METRICS COMPARISON")
    print("=" * 65)
    print(comparison_df.to_string(index=False))

    # Save metrics table
    comparison_df.to_csv("output/models/model_comparison.csv", index=False)
    print("\nSaved evaluation results to: output/models/model_comparison.csv")

    # 8. Save Fitted Random Forest Pipeline Model
    rf_model_path = "output/models/rf_traffic_pipeline"
    print(f"\nPersisting fitted Random Forest pipeline to: {rf_model_path}...")
    rf_model.write().overwrite().save(rf_model_path)
    print("Fitted pipeline persisted successfully!")

    # 9. Save Predictions for Analysis and Dashboard
    rf_preds_selected = rf_preds.select(
        "date_time", "hour", "day_of_week", "month", "is_weekend",
        "weather_main", "holiday", "temp", "rain_1h", "snow_1h",
        "traffic_volume", spark_round(col("prediction"), 1).alias("prediction")
    )
    
    # Save test sample to CSV for quick dashboard loading
    test_sample_pdf = rf_preds_selected.orderBy("date_time").limit(2000).toPandas()
    test_sample_pdf.to_csv("output/models/test_predictions_sample.csv", index=False)
    print("Saved sample predictions to: output/models/test_predictions_sample.csv")

    # 10. Generate Actual vs Predicted Presentation Figure
    print("\n--- Generating Actual vs. Predicted Visualizations ---")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # 10A: 7-Day Time Series actual vs predicted snapshot
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    # Take first 168 hours (1 full week) from test set
    week_slice = test_sample_pdf.head(168).copy()
    week_slice["date_time_str"] = pd.to_datetime(week_slice["date_time"]).dt.strftime("%b %d %H:00")

    ax.plot(range(len(week_slice)), week_slice["traffic_volume"], label="Actual Traffic Volume", color="#1f77b4", linewidth=2.0)
    ax.plot(range(len(week_slice)), week_slice["prediction"], label="Random Forest Prediction", color="#ff7f0e", linestyle="--", linewidth=2.0)
    
    # Set x-ticks every 24 hours
    tick_indices = range(0, len(week_slice), 24)
    tick_labels = [week_slice.iloc[i]["date_time_str"] for i in tick_indices]
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, rotation=25, ha="right")

    ax.set_title("Test Set Evaluation: 7-Day Hourly Actual vs. Predicted Traffic Volume", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Timestamp", fontsize=11)
    ax.set_ylabel("Traffic Volume (Vehicles / Hour)", fontsize=11)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig("output/figures/06_actual_vs_predicted_traffic.png")
    plt.close(fig)
    print("Saved: output/figures/06_actual_vs_predicted_traffic.png")

    spark.stop()
    print("\nPhase 4 Machine Learning training and evaluation finished successfully!")

if __name__ == "__main__":
    train_and_evaluate()
