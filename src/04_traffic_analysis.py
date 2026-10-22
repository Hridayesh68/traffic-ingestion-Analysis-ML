"""
Phase 3: Exploratory Data Analysis & Aggregate Visualizations
-----------------------------------------------------------
This script computes comprehensive traffic metrics using PySpark DataFrames and Spark SQL:
1. Hourly traffic volume profiles (identifying commute peaks).
2. Weekday vs. Weekend traffic curves (bimodal commute vs. unimodal leisure).
3. Monthly & seasonal traffic trends.
4. Traffic distribution across meteorological conditions (weather_main and weather_description).
5. Holiday vs. Non-holiday traffic comparison (handling literal 'None' vs holiday strings).
6. Traffic volume statistical distributions & percentiles.

Outputs:
- CSV aggregates saved to: output/eda/
- Presentation-quality figures saved to: output/figures/
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, min, max, stddev, round as spark_round,
    when, desc, asc, expr
)

def run_eda():
    # 1. Initialize SparkSession
    spark = (
        SparkSession.builder
        .appName("TrafficEDA")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Ensure output directories exist
    os.makedirs("output/eda", exist_ok=True)
    os.makedirs("output/figures", exist_ok=True)

    # 2. Load Cleaned Parquet Data
    parquet_path = "output/traffic_cleaned.parquet"
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Cleaned parquet dataset not found at {parquet_path}. Run src/03_clean_data.py first.")

    print(f"Loading cleaned dataset from {parquet_path}...")
    df = spark.read.parquet(parquet_path)
    df.createOrReplaceTempView("traffic")

    total_records = df.count()
    print(f"Successfully loaded {total_records:,} cleaned records for analysis.\n")

    # =========================================================================
    # 1. Hourly Traffic Volume Analysis (PySpark DataFrame API)
    # =========================================================================
    print("--- Calculating Hourly Traffic Volume ---")
    hourly_df = (
        df.groupBy("hour")
        .agg(
            spark_round(avg("traffic_volume"), 2).alias("avg_traffic"),
            spark_round(stddev("traffic_volume"), 2).alias("std_traffic"),
            min("traffic_volume").alias("min_traffic"),
            max("traffic_volume").alias("max_traffic"),
            count("*").alias("observation_count")
        )
        .orderBy("hour")
    )
    hourly_pdf = hourly_df.toPandas()
    hourly_pdf.to_csv("output/eda/hourly_traffic.csv", index=False)
    print("Saved: output/eda/hourly_traffic.csv")

    # =========================================================================
    # 2. Weekday vs Weekend Traffic Comparison (Spark SQL)
    # =========================================================================
    print("--- Calculating Weekday vs Weekend Hourly Profiles ---")
    weekday_weekend_sql = """
    SELECT 
        hour,
        is_weekend,
        CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
        ROUND(AVG(traffic_volume), 2) AS avg_traffic,
        ROUND(STDDEV(traffic_volume), 2) AS std_traffic,
        COUNT(*) AS observation_count
    FROM traffic
    GROUP BY hour, is_weekend
    ORDER BY hour, is_weekend
    """
    weekday_weekend_df = spark.sql(weekday_weekend_sql)
    ww_pdf = weekday_weekend_df.toPandas()
    ww_pdf.to_csv("output/eda/weekday_weekend_traffic.csv", index=False)
    print("Saved: output/eda/weekday_weekend_traffic.csv")

    # Pivoted table for reporting
    pivot_ww = ww_pdf.pivot(index="hour", columns="day_type", values="avg_traffic").reset_index()
    pivot_ww["difference_weekday_minus_weekend"] = pivot_ww["Weekday"] - pivot_ww["Weekend"]
    pivot_ww.to_csv("output/eda/weekday_weekend_pivot.csv", index=False)

    # =========================================================================
    # 3. Monthly Traffic Analysis (PySpark DataFrame API)
    # =========================================================================
    print("--- Calculating Monthly Traffic Profiles ---")
    monthly_df = (
        df.groupBy("month")
        .agg(
            spark_round(avg("traffic_volume"), 2).alias("avg_traffic"),
            spark_round(stddev("traffic_volume"), 2).alias("std_traffic"),
            spark_round(avg("temp"), 2).alias("avg_temp_kelvin"),
            spark_round(avg("rain_1h"), 3).alias("avg_rain_mm"),
            count("*").alias("observation_count")
        )
        .orderBy("month")
    )
    monthly_pdf = monthly_df.toPandas()
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    monthly_pdf["month_name"] = monthly_pdf["month"].map(month_names)
    monthly_pdf.to_csv("output/eda/monthly_traffic.csv", index=False)
    print("Saved: output/eda/monthly_traffic.csv")

    # =========================================================================
    # 4. Weather Category Impact (Spark SQL)
    # =========================================================================
    print("--- Calculating Weather Impact on Traffic ---")
    weather_sql = """
    SELECT 
        weather_main,
        COUNT(*) AS observation_count,
        ROUND(AVG(traffic_volume), 2) AS avg_traffic,
        ROUND(STDDEV(traffic_volume), 2) AS std_traffic,
        ROUND(AVG(temp), 2) AS avg_temp_kelvin,
        ROUND(AVG(rain_1h), 3) AS avg_rain_mm,
        ROUND(AVG(clouds_all), 1) AS avg_clouds_pct
    FROM traffic
    GROUP BY weather_main
    ORDER BY avg_traffic DESC
    """
    weather_df = spark.sql(weather_sql)
    weather_pdf = weather_df.toPandas()
    weather_pdf.to_csv("output/eda/weather_traffic.csv", index=False)
    print("Saved: output/eda/weather_traffic.csv")

    # =========================================================================
    # 5. Holiday vs Non-Holiday Comparison
    # IMPORTANT: In this dataset, holiday is string 'None' for regular days!
    # =========================================================================
    print("--- Calculating Holiday vs Non-Holiday Traffic ---")
    holiday_sql = """
    SELECT 
        CASE 
            WHEN holiday IS NULL OR holiday = 'None' THEN 'Regular Day'
            ELSE 'Holiday'
        END AS holiday_classification,
        COUNT(*) AS observation_count,
        ROUND(AVG(traffic_volume), 2) AS avg_traffic,
        ROUND(STDDEV(traffic_volume), 2) AS std_traffic,
        MIN(traffic_volume) AS min_traffic,
        MAX(traffic_volume) AS max_traffic
    FROM traffic
    GROUP BY CASE WHEN holiday IS NULL OR holiday = 'None' THEN 'Regular Day' ELSE 'Holiday' END
    """
    holiday_summary_df = spark.sql(holiday_sql)
    holiday_summary_pdf = holiday_summary_df.toPandas()
    holiday_summary_pdf.to_csv("output/eda/holiday_summary.csv", index=False)

    # Detailed breakdown by specific holiday (noting small group sizes)
    specific_holiday_sql = """
    SELECT 
        holiday,
        COUNT(*) AS observation_count,
        ROUND(AVG(traffic_volume), 2) AS avg_traffic,
        ROUND(STDDEV(traffic_volume), 2) AS std_traffic
    FROM traffic
    WHERE holiday != 'None' AND holiday IS NOT NULL
    GROUP BY holiday
    ORDER BY avg_traffic ASC
    """
    specific_holiday_df = spark.sql(specific_holiday_sql)
    specific_holiday_pdf = specific_holiday_df.toPandas()
    specific_holiday_pdf.to_csv("output/eda/specific_holidays.csv", index=False)
    print("Saved: output/eda/holiday_summary.csv & output/eda/specific_holidays.csv")

    # =========================================================================
    # 6. Overall Traffic Volume Summary & Percentiles
    # =========================================================================
    print("--- Calculating Traffic Volume Distribution Statistics ---")
    quantiles = df.stat.approxQuantile("traffic_volume", [0.05, 0.25, 0.50, 0.75, 0.95], 0.001)
    summary_df = df.select("traffic_volume").describe()
    summary_pdf = summary_df.toPandas()
    
    # Add quantiles
    q_rows = pd.DataFrame([
        {"summary": "p05", "traffic_volume": str(quantiles[0])},
        {"summary": "p25 (Q1)", "traffic_volume": str(quantiles[1])},
        {"summary": "p50 (Median)", "traffic_volume": str(quantiles[2])},
        {"summary": "p75 (Q3)", "traffic_volume": str(quantiles[3])},
        {"summary": "p95", "traffic_volume": str(quantiles[4])}
    ])
    summary_pdf = pd.concat([summary_pdf, q_rows], ignore_index=True)
    summary_pdf.to_csv("output/eda/traffic_summary_stats.csv", index=False)
    print("Saved: output/eda/traffic_summary_stats.csv")

    spark.stop()

    # =========================================================================
    # 7. Generate Presentation-Quality Visualizations
    # =========================================================================
    print("\n--- Generating Publication-Quality Figures ---")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 11

    # --- FIGURE 1: Hourly Traffic Profile ---
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.plot(hourly_pdf["hour"], hourly_pdf["avg_traffic"], marker="o", color="#1f77b4", linewidth=2.5, label="Mean Traffic Volume")
    ax.fill_between(
        hourly_pdf["hour"],
        hourly_pdf["avg_traffic"] - hourly_pdf["std_traffic"] * 0.5,
        hourly_pdf["avg_traffic"] + hourly_pdf["std_traffic"] * 0.5,
        color="#1f77b4", alpha=0.15, label="±0.5 Std Dev Band"
    )
    ax.set_title("Metro Interstate Hourly Traffic Volume Profile", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day (0–23)", fontsize=12)
    ax.set_ylabel("Average Traffic Volume (Vehicles / Hour)", fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle="--", alpha=0.6)
    
    # Annotate peaks
    ax.annotate("Morning Peak (7-8 AM)\n~4,750 vph", xy=(7, 4750), xytext=(3, 5200),
                arrowprops=dict(facecolor="#d62728", arrowstyle="->", lw=1.5),
                fontweight="bold", color="#d62728")
    ax.annotate("Evening Peak (4-5 PM)\n~4,850 vph", xy=(16, 4850), xytext=(17, 5400),
                arrowprops=dict(facecolor="#d62728", arrowstyle="->", lw=1.5),
                fontweight="bold", color="#d62728")
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig("output/figures/01_hourly_traffic_profile.png")
    plt.close(fig)
    print("Saved: output/figures/01_hourly_traffic_profile.png")

    # --- FIGURE 2: Weekday vs Weekend Comparison ---
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    weekday_data = ww_pdf[ww_pdf["day_type"] == "Weekday"]
    weekend_data = ww_pdf[ww_pdf["day_type"] == "Weekend"]

    ax.plot(weekday_data["hour"], weekday_data["avg_traffic"], marker="s", color="#2ca02c", linewidth=2.5, label="Weekday (Mon–Fri)")
    ax.plot(weekend_data["hour"], weekend_data["avg_traffic"], marker="^", color="#ff7f0e", linewidth=2.5, linestyle="--", label="Weekend (Sat–Sun)")
    
    ax.set_title("Commute Dynamics: Weekday vs. Weekend Hourly Traffic Curves", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day (0–23)", fontsize=12)
    ax.set_ylabel("Average Traffic Volume (Vehicles / Hour)", fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.annotate("Bimodal Commute Curves", xy=(16, 6189), xytext=(11, 6400),
                arrowprops=dict(facecolor="#2ca02c", arrowstyle="->", lw=1.5),
                fontweight="bold", color="#2ca02c")
    ax.annotate("Unimodal Leisure Plateau", xy=(13, 4362), xytext=(14, 2500),
                arrowprops=dict(facecolor="#ff7f0e", arrowstyle="->", lw=1.5),
                fontweight="bold", color="#ff7f0e")
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig("output/figures/02_weekday_vs_weekend_comparison.png")
    plt.close(fig)
    print("Saved: output/figures/02_weekday_vs_weekend_comparison.png")

    # --- FIGURE 3: Monthly Traffic Trends ---
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bars = ax.bar(monthly_pdf["month_name"], monthly_pdf["avg_traffic"], color="#4a90e2", edgecolor="#1a5276", width=0.6)
    ax.set_title("Seasonal Traffic Variation: Average Volume by Month", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Month of Year", fontsize=12)
    ax.set_ylabel("Average Traffic Volume (Vehicles / Hour)", fontsize=12)
    ax.set_ylim(2500, 3700)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{int(height):,}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.tight_layout()
    fig.savefig("output/figures/03_monthly_traffic_trends.png")
    plt.close(fig)
    print("Saved: output/figures/03_monthly_traffic_trends.png")

    # --- FIGURE 4: Weather Main Category Impact ---
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    weather_sorted = weather_pdf.sort_values(by="avg_traffic", ascending=True)
    bars = ax.barh(weather_sorted["weather_main"], weather_sorted["avg_traffic"], color="#34495e", edgecolor="#1c2833", height=0.65)
    ax.set_title("Interstate Traffic Volume Across Main Weather Conditions", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Average Traffic Volume (Vehicles / Hour)", fontsize=12)
    ax.set_ylabel("Weather Condition", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.6)

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f"{int(width):,} vph",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    fig.savefig("output/figures/04_weather_impact_on_traffic.png")
    plt.close(fig)
    print("Saved: output/figures/04_weather_impact_on_traffic.png")

    # --- FIGURE 5: Holiday vs Regular Day Comparison ---
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    bars = ax.bar(holiday_summary_pdf["holiday_classification"], holiday_summary_pdf["avg_traffic"],
                  color=["#2980b9", "#c0392b"], width=0.45)
    ax.set_title("Traffic Volume: Regular Days vs. Statutory Holidays", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Average Traffic Volume (Vehicles / Hour)", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{int(h):,} vph",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    fig.savefig("output/figures/05_holiday_traffic_comparison.png")
    plt.close(fig)
    print("Saved: output/figures/05_holiday_traffic_comparison.png")

    print("\nPhase 3 EDA calculations and presentation figures generated successfully!")

if __name__ == "__main__":
    run_eda()
