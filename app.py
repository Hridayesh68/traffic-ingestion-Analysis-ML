# Traffic Congestion Analysis & Prediction - Streamlit Dashboard
# Run: streamlit run app.py

import os
import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="Traffic Analysis Dashboard",
    layout="wide"
)

# ---- Load data ----
@st.cache_data
def load_data():
    files = {
        "hourly": "output/eda/hourly_traffic.csv",
        "weekday_weekend": "output/eda/weekday_weekend_traffic.csv",
        "monthly": "output/eda/monthly_traffic.csv",
        "weather": "output/eda/weather_traffic.csv",
        "holiday": "output/eda/holiday_summary.csv",
        "stats": "output/eda/traffic_summary_stats.csv",
        "model_comp": "output/models/model_comparison.csv",
        "test_sample": "output/models/test_predictions_sample.csv"
    }
    data = {}
    for key, path in files.items():
        if os.path.exists(path):
            data[key] = pd.read_csv(path)
        else:
            data[key] = None
    return data

@st.cache_resource
def load_spark_model():
    from pyspark.sql import SparkSession
    from pyspark.ml import PipelineModel

    spark = (
        SparkSession.builder
        .appName("TrafficApp")
        .master("local[1]")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    model_path = "output/models/rf_traffic_pipeline"
    model = PipelineModel.load(model_path) if os.path.exists(model_path) else None
    return spark, model

data = load_data()

# ---- Sidebar ----
st.sidebar.title("Traffic Dashboard")
page = st.sidebar.radio("Go to", [
    "Overview",
    "EDA",
    "Model Results",
    "Predict Traffic"
])

st.sidebar.markdown("---")
st.sidebar.write("**Tools Used:** PySpark, Spark SQL, MLlib, Streamlit")
st.sidebar.write("Dataset: Metro Interstate I-94 Traffic")

# ==============================================================
# Page 1: Overview
# ==============================================================
if page == "Overview":
    st.title("Metro Interstate Traffic Analysis")
    st.write("This project analyses hourly traffic data collected on Interstate 94 (westbound) "
             "between Minneapolis and St. Paul, Minnesota from 2012 to 2018.")

    st.write("The dataset has **48,187 records** with weather and calendar information. "
             "We cleaned the data, did exploratory analysis, and trained a Random Forest model to predict traffic volume.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", "48,187")
    col2.metric("Avg Traffic", "3,260 vph")
    col3.metric("Peak Volume", "6,190 vph")
    col4.metric("Model R²", "0.9120")

    st.markdown("---")
    st.subheader("Project Pipeline")
    st.write("""
    1. **Data Quality Check** — checked for nulls, duplicates, and data types
    2. **Anomaly Investigation** — found sensor errors like 0 K temperature and extreme rain values
    3. **Data Cleaning** — removed duplicates, fixed anomalies, added time features (hour, day, month)
    4. **Analysis** — grouped traffic by hour, day type, month, weather, and holidays
    5. **ML Model** — trained a Random Forest regressor using Spark MLlib (R² = 0.912)
    """)

    # Show sample figures if available
    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists("output/figures/01_hourly_traffic_profile.png"):
            st.image("output/figures/01_hourly_traffic_profile.png",
                     caption="Hourly Traffic Profile")
    with c2:
        if os.path.exists("output/figures/02_weekday_vs_weekend_comparison.png"):
            st.image("output/figures/02_weekday_vs_weekend_comparison.png",
                     caption="Weekday vs Weekend Traffic")

# ==============================================================
# Page 2: EDA
# ==============================================================
elif page == "EDA":
    st.title("Exploratory Data Analysis")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Hourly Trends", "Monthly Trends", "Weather", "Holidays"
    ])

    with tab1:
        st.subheader("Traffic by Hour - Weekday vs Weekend")
        ww = data.get("weekday_weekend")
        if ww is not None:
            pivot = ww.pivot(index="hour", columns="day_type", values="avg_traffic")
            st.line_chart(pivot)
            st.write("- Weekdays show two peaks: morning (7-8 AM) and evening (4-5 PM)")
            st.write("- Weekends have a single broad peak in the afternoon")
            with st.expander("Show data"):
                st.dataframe(ww)

    with tab2:
        st.subheader("Average Traffic by Month")
        monthly = data.get("monthly")
        if monthly is not None:
            st.bar_chart(monthly.set_index("month_name")["avg_traffic"])
            st.write("- Summer months (June-August) have higher traffic")
            st.write("- Winter months show lower volumes due to cold weather")
            with st.expander("Show data"):
                st.dataframe(monthly)

    with tab3:
        st.subheader("Traffic by Weather Condition")
        weather = data.get("weather")
        if weather is not None:
            st.bar_chart(weather.set_index("weather_main")["avg_traffic"])
            st.write("- Most traffic occurs during 'Clouds' and 'Clear' weather (because those are common during commute hours)")
            st.write("- Bad weather like fog and thunderstorms shows lower traffic")
            with st.expander("Show data"):
                st.dataframe(weather)

    with tab4:
        st.subheader("Holiday vs Regular Day Traffic")
        holiday = data.get("holiday")
        if holiday is not None:
            st.bar_chart(holiday.set_index("holiday_classification")["avg_traffic"])
            st.write("- Traffic drops by about 73% on holidays compared to regular days")
            with st.expander("Show data"):
                st.dataframe(holiday)

# ==============================================================
# Page 3: Model Results
# ==============================================================
elif page == "Model Results":
    st.title("ML Model Evaluation")
    st.write("We trained two models using Spark MLlib and compared them:")

    model_comp = data.get("model_comp")
    if model_comp is not None:
        st.table(model_comp)

    st.write("The Random Forest model performed much better than the Linear Regression baseline.")

    col1, col2, col3 = st.columns(3)
    col1.metric("R² Score", "0.9120")
    col2.metric("MAE", "382.78 vph")
    col3.metric("RMSE", "583.51 vph")

    st.markdown("---")
    st.subheader("Actual vs Predicted")
    if os.path.exists("output/figures/06_actual_vs_predicted_traffic.png"):
        st.image("output/figures/06_actual_vs_predicted_traffic.png",
                 caption="Actual vs Predicted Traffic (Test Set)")

    test_sample = data.get("test_sample")
    if test_sample is not None:
        with st.expander("View prediction samples"):
            cols_to_show = ["date_time", "hour", "day_of_week", "weather_main",
                           "temp", "traffic_volume", "prediction"]
            available_cols = [c for c in cols_to_show if c in test_sample.columns]
            st.dataframe(test_sample[available_cols].head(50))

# ==============================================================
# Page 4: Predict Traffic
# ==============================================================
elif page == "Predict Traffic":
    st.title("Traffic Volume Predictor")
    st.write("Enter weather and time details below to predict the expected traffic volume.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Time Details")
        hour_val = st.slider("Hour of Day", 0, 23, 8)
        day_options = {
            "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4,
            "Thursday": 5, "Friday": 6, "Saturday": 7
        }
        day_name = st.selectbox("Day of Week", list(day_options.keys()), index=2)
        day_of_week = day_options[day_name]
        is_weekend = 1 if day_of_week in (1, 7) else 0
        month_val = st.slider("Month", 1, 12, 10)

    with col2:
        st.subheader("Weather Details")
        weather_list = ["Clear", "Clouds", "Rain", "Drizzle", "Snow",
                       "Mist", "Haze", "Fog", "Thunderstorm", "Squall", "Smoke"]
        weather_val = st.selectbox("Weather", weather_list, index=1)
        temp_c = st.slider("Temperature (°C)", -30, 40, 15)
        temp_k = round(temp_c + 273.15, 2)
        st.write(f"Temperature in Kelvin: {temp_k} K")
        clouds_val = st.slider("Cloud Cover (%)", 0, 100, 40)
        rain_val = st.number_input("Rain in last hour (mm)", 0.0, 80.0, 0.0, step=0.5)
        snow_val = st.number_input("Snow in last hour (mm)", 0.0, 1.0, 0.0, step=0.05)

    holiday_list = [
        "None", "Columbus Day", "Veterans Day", "Thanksgiving Day",
        "Christmas Day", "New Years Day", "Martin Luther King Jr Day",
        "Washingtons Birthday", "Memorial Day", "Independence Day",
        "State Fair", "Labor Day"
    ]
    holiday_val = st.selectbox("Holiday", holiday_list, index=0)

    if st.button("Predict", type="primary"):
        with st.spinner("Running prediction..."):
            spark, model = load_spark_model()
            if model is None:
                st.error("Model not found. Run src/05_train_model.py first.")
            else:
                input_data = [{
                    "hour": int(hour_val),
                    "day_of_week": int(day_of_week),
                    "month": int(month_val),
                    "is_weekend": int(is_weekend),
                    "temp": float(temp_k),
                    "rain_1h": float(rain_val),
                    "snow_1h": float(snow_val),
                    "clouds_all": int(clouds_val),
                    "weather_main": str(weather_val),
                    "holiday": str(holiday_val)
                }]

                input_df = spark.createDataFrame(input_data)
                result = model.transform(input_df)
                predicted = int(round(result.select("prediction").collect()[0][0]))

                # Show result
                if predicted < 1500:
                    level = "Low"
                elif predicted < 3500:
                    level = "Moderate"
                elif predicted < 5000:
                    level = "High"
                else:
                    level = "Very High"

                st.success(f"Predicted Traffic Volume: **{predicted:,} vehicles/hour** ({level})")

# Footer
st.markdown("---")
st.write("Traffic Congestion Analysis and Prediction | PySpark, Spark SQL, MLlib, Streamlit")
