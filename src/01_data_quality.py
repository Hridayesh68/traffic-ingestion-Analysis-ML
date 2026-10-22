
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, when, isnan, min, max, mean
)

spark = (
    SparkSession.builder
    .appName("TrafficDataQuality")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# Load dataset
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/traffic_data.csv")
)

# 1. Basic overview
print("\n========== DATASET OVERVIEW ==========")
print("Rows:", df.count())
print("Columns:", len(df.columns))
print("Column names:", df.columns)

print("\n========== SCHEMA ==========")
df.printSchema()

print("\n========== SAMPLE RECORDS ==========")
df.show(5, truncate=False)

# 2. Missing values and NaN values
print("\n========== MISSING VALUES ==========")

missing_exprs = []

for field in df.schema.fields:
    c = col(field.name)
    if field.dataType.typeName() in ("double", "float"):
        missing_exprs.append(
            count(
                when(c.isNull() | isnan(c), 1)
            ).alias(field.name)
        )
    else:
        missing_exprs.append(
            count(when(c.isNull(), 1)).alias(field.name)
        )

df.select(*missing_exprs).show(truncate=False)

# 3. Duplicate rows
print("\n========== DUPLICATE ROWS ==========")
duplicate_count = df.count() - df.dropDuplicates().count()
print("Duplicate rows:", duplicate_count)

# 4. Numeric statistics
print("\n========== NUMERIC SUMMARY ==========")
df.describe(
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "traffic_volume"
).show(truncate=False)

# 5. Zero and positive values in snowfall
print("\n========== SNOWFALL DISTRIBUTION ==========")

df.select(
    count("*").alias("total_rows"),
    count(when(col("snow_1h") == 0, 1)).alias("zero_snow_rows"),
    count(when(col("snow_1h") > 0, 1)).alias("positive_snow_rows"),
    count(when(col("snow_1h") < 0, 1)).alias("negative_snow_rows"),
    count(when(col("snow_1h").isNull(), 1)).alias("null_snow_rows"),
    max("snow_1h").alias("max_snowfall")
).show(truncate=False)

# 6. Check suspicious values
print("\n========== BASIC VALIDITY CHECKS ==========")

df.select(
    count(when(col("traffic_volume") < 0, 1)).alias("negative_traffic"),
    count(when(col("rain_1h") < 0, 1)).alias("negative_rainfall"),
    count(when(col("snow_1h") < 0, 1)).alias("negative_snowfall"),
    count(when(col("clouds_all") < 0, 1)).alias("negative_clouds"),
    count(when(col("clouds_all") > 100, 1)).alias("clouds_over_100")
).show()

spark.stop()
