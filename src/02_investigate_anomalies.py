
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, min, max

spark = (
    SparkSession.builder
    .appName("TrafficAnomalyInvestigation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/traffic_data.csv")
)

print("\n=== RECORDS WITH ZERO TEMPERATURE ===")
df.filter(col("temp") == 0).show(20, truncate=False)

print("\n=== HIGHEST RAINFALL RECORDS ===")
df.orderBy(col("rain_1h").desc()).select(
    "date_time",
    "temp",
    "rain_1h",
    "snow_1h",
    "weather_main",
    "weather_description",
    "traffic_volume"
).show(10, truncate=False)

print("\n=== RECORDS WITH ZERO TRAFFIC ===")
df.filter(col("traffic_volume") == 0).select(
    "date_time",
    "temp",
    "rain_1h",
    "snow_1h",
    "weather_main",
    "weather_description",
    "traffic_volume"
).show(10, truncate=False)

print("\n=== DUPLICATED COMPLETE RECORDS ===")
df.groupBy(*df.columns).agg(
    count("*").alias("copies")
).filter(
    col("copies") > 1
).show(20, truncate=False)

print("\n=== TIMESTAMP RANGE & TEMPORAL STATS ===")
df.select(
    min("date_time").alias("earliest_timestamp"),
    max("date_time").alias("latest_timestamp"),
    count("*").alias("total_records"),
    count("date_time").alias("valid_timestamps")
).show(truncate=False)

spark.stop()

