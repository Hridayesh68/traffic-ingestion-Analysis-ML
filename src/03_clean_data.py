
"""
Traffic Data Cleaning & Feature Engineering Pipeline
---------------------------------------------------
This script implements Phase 2 of the Traffic Congestion Analysis project:
1. Loads raw CSV data (48,204 rows, 9 columns).
2. Deduplicates exact matching rows (17 exact duplicate rows removed; 
   repeated timestamps with different weather conditions are preserved).
3. Sanitizes physical sensor anomalies:
   - Sets temp == 0.0 K (unphysical sensor default) to NULL.
   - Sets rain_1h > 100.0 mm (sensor gauge malfunction e.g. 9831.3 mm) to NULL.
   - Valid zeros in rainfall, snowfall, and traffic volume are strictly preserved.
4. Engineers temporal features:
   - 'date': Date extracted from timestamp (to_date).
   - 'hour': Hour of day (0-23).
   - 'day_of_week': Day of week integer index. 
     NOTE: In Spark SQL dayofweek(), Sunday = 1, Monday = 2, ..., Saturday = 7.
   - 'month': Month index (1-12).
   - 'is_weekend': Binary indicator (1 if day_of_week in (1, 7), else 0).
5. Validates and saves clean dataset to Parquet format (output/traffic_cleaned.parquet).
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, lit, hour, dayofweek, month,
    to_date, count, min, max, round as spark_round
)

spark = (
    SparkSession.builder
    .appName("TrafficDataCleaning")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# 1. Load raw data
raw_path = "data/traffic_data.csv"
df_raw = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(raw_path)
)

raw_count = df_raw.count()
print("\n" + "=" * 50)
print("1. PRE-CLEANING DATA OVERVIEW")
print("=" * 50)
print(f"Total raw observations: {raw_count:,}")

# Pre-cleaning anomaly checks
df_raw.select(
    count(when(col("temp") == 0, 1)).alias("zero_temp_count"),
    count(when(col("rain_1h") > 100, 1)).alias("extreme_rain_count"),
    count(when(col("traffic_volume") == 0, 1)).alias("zero_traffic_count")
).show()

# 2. Remove exact duplicate records across all columns
# NOTE: df.dropDuplicates() without arguments compares all 9 columns.
# Rows sharing the same timestamp but having distinct weather descriptions
# (e.g., simultaneous Mist and Rain) are preserved as legitimate observations.
df_dedup = df_raw.dropDuplicates()
dedup_count = df_dedup.count()
exact_dupes = raw_count - dedup_count

print("=" * 50)
print("2. DEDUPLICATION METRICS")
print("=" * 50)
print(f"Exact duplicates removed: {exact_dupes}")
print(f"Observations remaining:   {dedup_count:,}")

# 3. Correct suspicious values by marking them as missing (NULL)
# - Temperature of 0.0 Kelvin is absolute zero (-273.15 deg C), a clear sensor failure.
# - Rainfall > 100 mm in a single hour is physically unviable in Minnesota (gauge glitch).
# - These will be imputed via Spark MLlib Imputer during model training.
df_sanitized = df_dedup.withColumn(
    "temp",
    when(col("temp") == 0, lit(None).cast("double"))
    .otherwise(col("temp"))
).withColumn(
    "rain_1h",
    when(col("rain_1h") > 100, lit(None).cast("double"))
    .otherwise(col("rain_1h"))
)

# 4. Extract time-based features
# NOTE: Spark's dayofweek() function adheres to the standard where:
# 1 = Sunday, 2 = Monday, 3 = Tuesday, 4 = Wednesday, 5 = Thursday, 6 = Friday, 7 = Saturday.
# Hence, weekend is defined where dayofweek in (1, 7).
df_featured = (
    df_sanitized
    .withColumn("date", to_date("date_time"))
    .withColumn("hour", hour("date_time"))
    .withColumn("day_of_week", dayofweek("date_time"))
    .withColumn("month", month("date_time"))
    .withColumn(
        "is_weekend",
        when(dayofweek("date_time").isin(1, 7), 1)
        .otherwise(0)
    )
)

# 5. Review cleaned data
print("\n" + "=" * 50)
print("3. POST-CLEANING QUALITY AUDIT")
print("=" * 50)
df_featured.select(
    count("*").alias("final_rows"),
    min("date_time").alias("earliest_timestamp"),
    max("date_time").alias("latest_timestamp"),
    count(when(col("temp").isNull(), 1)).alias("sanitized_temp_nulls"),
    count(when(col("rain_1h").isNull(), 1)).alias("sanitized_rain_nulls"),
    count(when(col("traffic_volume") == 0, 1)).alias("preserved_zero_traffic"),
    count(when(col("snow_1h") == 0, 1)).alias("preserved_zero_snow")
).show(truncate=False)

print("\nSample Cleaned Records:")
df_featured.select(
    "date_time", "hour", "day_of_week", "month",
    "is_weekend", "temp", "rain_1h",
    "snow_1h", "traffic_volume"
).show(5, truncate=False)

# 6. Save as Parquet
output_path = "output/traffic_cleaned.parquet"
df_featured.write.mode("overwrite").parquet(output_path)
print(f"\nCleaned dataset successfully written to: {output_path}")

spark.stop()

