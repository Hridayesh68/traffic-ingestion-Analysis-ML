"""
Traffic Congestion Analysis & Prediction Dashboard
=================================================
A Streamlit web application providing interactive analytics, model evaluation,
and real-time MLlib inference for the Metro Interstate Traffic Volume dataset.

Run command:
    streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Metro Interstate Traffic Analytics & ML Prediction",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2563EB;
    }
    .callout-box {
        background-color: #EFF6FF;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #BFDBFE;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching Functions
# -----------------------------------------------------------------------------
@st.cache_data
def load_eda_data():
    """Loads precomputed aggregate CSV tables from output/eda/."""
    hourly_df = pd.read_csv("output/eda/hourly_traffic.csv") if os.path.exists("output/eda/hourly_traffic.csv") else None
    ww_df = pd.read_csv("output/eda/weekday_weekend_traffic.csv") if os.path.exists("output/eda/weekday_weekend_traffic.csv") else None
    monthly_df = pd.read_csv("output/eda/monthly_traffic.csv") if os.path.exists("output/eda/monthly_traffic.csv") else None
    weather_df = pd.read_csv("output/eda/weather_traffic.csv") if os.path.exists("output/eda/weather_traffic.csv") else None
    holiday_df = pd.read_csv("output/eda/holiday_summary.csv") if os.path.exists("output/eda/holiday_summary.csv") else None
    stats_df = pd.read_csv("output/eda/traffic_summary_stats.csv") if os.path.exists("output/eda/traffic_summary_stats.csv") else None
    model_comp_df = pd.read_csv("output/models/model_comparison.csv") if os.path.exists("output/models/model_comparison.csv") else None
    test_sample_df = pd.read_csv("output/models/test_predictions_sample.csv") if os.path.exists("output/models/test_predictions_sample.csv") else None
    return hourly_df, ww_df, monthly_df, weather_df, holiday_df, stats_df, model_comp_df, test_sample_df

@st.cache_resource
def get_spark_and_model():
    """Initializes SparkSession and loads the pre-trained MLlib PipelineModel once."""
    from pyspark.sql import SparkSession
    from pyspark.ml import PipelineModel

    spark = (
        SparkSession.builder
        .appName("TrafficStreamlitApp")
        .master("local[1]")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    model_path = "output/models/rf_traffic_pipeline"
    if os.path.exists(model_path):
        model = PipelineModel.load(model_path)
    else:
        model = None
    return spark, model

# Load aggregate data
hourly_df, ww_df, monthly_df, weather_df, holiday_df, stats_df, model_comp_df, test_sample_df = load_eda_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Context
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/traffic-jam.png", width=70)
st.sidebar.title("Navigation")
nav_choice = st.sidebar.radio(
    "Select Section",
    [
        "Executive Overview",
        "Exploratory Analysis (EDA)",
        "Model Performance & Evaluation",
        "Live Traffic Predictor",
        "Data Dictionary & Limitations"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Project Stack:**")
st.sidebar.markdown("- Apache Spark 3.5.9 (PySpark, Spark SQL, Spark MLlib)")
st.sidebar.markdown("- Python 3.10 & Streamlit")
st.sidebar.markdown("- Parquet Storage")
st.sidebar.caption("Metro Interstate I-94 Traffic Dataset (Minneapolis-St. Paul, MN)")

# -----------------------------------------------------------------------------
# Section 1: Executive Overview
# -----------------------------------------------------------------------------
if nav_choice == "Executive Overview":
    st.markdown('<div class="main-header">Metro Interstate Traffic Volume & Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Scalable Big Data Processing, Analytical Modeling & Real-Time MLlib Forecasting</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box">
    <strong>Executive Summary:</strong> This Big Data application processes <strong>48,187</strong> hourly traffic observations 
    collected along westbound Interstate 94 between Minneapolis and St. Paul, Minnesota (2012–2018). 
    Using <strong>Apache PySpark</strong>, the pipeline handles data sanitization, feature engineering, distributed SQL querying, 
    and predictive modeling using <strong>Spark MLlib</strong>.
    </div>
    """, unsafe_allow_html=True)

    # Key KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Observations", "48,187", "Deduplicated")
    with col2:
        st.metric("Average Volume", "3,260 vph", "Overall Mean")
    with col3:
        st.metric("Peak Evening Volume", "6,190 vph", "Weekday 4-5 PM")
    with col4:
        st.metric("Model Test R²", "0.9120", "Random Forest")
    with col5:
        st.metric("Model Test MAE", "382.8 vph", "Vehicles / Hour")

    st.markdown("---")
    st.subheader("Data Pipeline Architecture")
    st.markdown("""
    1. **Ingestion & Quality Assessment (`01_data_quality.py`)**: Validates schema datatypes, nulls, and duplicate records.
    2. **Diagnostics & Anomaly Treatment (`02_investigate_anomalies.py`)**: Identifies sensor defaults (0.0 K temp) and gauge glitches (>100 mm rain).
    3. **Sanitization & Feature Engineering (`03_clean_data.py`)**: Implements strict deduplication, timestamp decomposition, and writes optimized Snappy Parquet.
    4. **Aggregations & Analytics (`04_traffic_analysis.py`)**: Computes diurnal profiles, weekday/weekend variances, and meteorological distributions.
    5. **Machine Learning (`05_train_model.py`)**: Implements chronological 80/20 train/test split with Random Forest Regressor achieving 0.912 R².
    """)

    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if os.path.exists("output/figures/01_hourly_traffic_profile.png"):
            st.image("output/figures/01_hourly_traffic_profile.png", caption="Diurnal Traffic Profile across 24 Hours", use_container_width=True)
    with col_img2:
        if os.path.exists("output/figures/02_weekday_vs_weekend_comparison.png"):
            st.image("output/figures/02_weekday_vs_weekend_comparison.png", caption="Commute Patterns: Weekday vs. Weekend Hourly Curves", use_container_width=True)

# -----------------------------------------------------------------------------
# Section 2: Exploratory Analysis (EDA)
# -----------------------------------------------------------------------------
elif nav_choice == "Exploratory Analysis (EDA)":
    st.markdown('<div class="main-header">Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Patterns in Interstate Congestion, Commute Dynamics, and Weather Impacts</div>', unsafe_allow_html=True)

    eda_tab1, eda_tab2, eda_tab3, eda_tab4 = st.tabs([
        "Hourly & Commute Trends",
        "Monthly & Seasonality",
        "Weather Conditions",
        "Holidays vs. Regular Days"
    ])

    with eda_tab1:
        st.subheader("Diurnal Traffic Volume & Day-Type Comparison")
        if ww_df is not None:
            # Interactive filter
            day_filter = st.multiselect(
                "Filter Day Classification:",
                options=["Weekday", "Weekend"],
                default=["Weekday", "Weekend"]
            )
            filtered_ww = ww_df[ww_df["day_type"].isin(day_filter)]
            
            # Line Chart using Streamlit native line_chart
            pivot_view = filtered_ww.pivot(index="hour", columns="day_type", values="avg_traffic")
            st.line_chart(pivot_view)

            st.markdown("""
            **Key Findings:**
            - **Weekday Commute Curve (Bimodal):** Displays sharp morning peak at 7:00–8:00 AM (~6,030 vph) and evening peak at 4:00–5:00 PM (~6,190 vph).
            - **Weekend Leisure Curve (Unimodal):** Traffic builds gradually to a broad plateau between 12:00 PM and 5:00 PM (~4,350 vph) with no sharp morning peak.
            """)

            with st.expander("View Underlying Data Table"):
                st.dataframe(filtered_ww, use_container_width=True)

    with eda_tab2:
        st.subheader("Seasonal Variations Across Months")
        if monthly_df is not None:
            col_m1, col_m2 = st.columns([3, 2])
            with col_m1:
                st.bar_chart(data=monthly_df.set_index("month_name")["avg_traffic"])
            with col_m2:
                st.markdown("""
                **Seasonal Observations:**
                - **Summer & Autumn Volume Peak:** June, August, and October exhibit highest traffic averages (>3,390 vph) due to favorable travel conditions and tourism.
                - **Winter Slump:** December and January register lower traffic (~3,024–3,051 vph), driven by sub-zero temperatures, snowstorms, and holiday closures.
                """)
                st.dataframe(monthly_df[["month_name", "avg_traffic", "avg_temp_kelvin", "avg_rain_mm", "observation_count"]], use_container_width=True)

    with eda_tab3:
        st.subheader("Traffic Flow by Weather Category")
        if weather_df is not None:
            st.bar_chart(data=weather_df.set_index("weather_main")["avg_traffic"])
            st.markdown("""
            **Important Methodological Note:**
            - Association does **not** imply causation. For example, high volumes recorded during "Clouds" or "Clear" weather coincide with normal peak daytime commuting hours.
            - Severe inclement weather ("Squall", "Fog", "Thunderstorm") shows reduced average vehicle counts due to reduced travel demand and cautious driving behaviors.
            """)
            st.dataframe(weather_df, use_container_width=True)

    with eda_tab4:
        st.subheader("Impact of Statutory Holidays")
        if holiday_df is not None:
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.bar_chart(data=holiday_df.set_index("holiday_classification")["avg_traffic"])
            with col_h2:
                st.markdown("""
                **Holiday Impact Analysis:**
                - **Regular Days:** Average volume ~3,263 vph.
                - **Statutory Holidays:** Average volume ~865 vph (a **73.5% drop** in interstate volume).
                - *Caution:* Observations on specific holidays represent small sample sizes (5–7 hours each); aggregate holiday comparisons are much more statistically reliable.
                """)
                st.dataframe(holiday_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 3: Model Performance & Evaluation
# -----------------------------------------------------------------------------
elif nav_choice == "Model Performance & Evaluation":
    st.markdown('<div class="main-header">Machine Learning Model Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Spark MLlib Regression Pipeline: Baseline vs. Random Forest</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="callout-box">
    <strong>Chronological Train / Test Validation Strategy:</strong><br>
    To prevent temporal data leakage, records were split strictly chronologically (first 80% train: Oct 2012 – Nov 2017; remaining 20% test: Nov 2017 – Sep 2018).
    Imputers, string indexers, and one-hot encoders were fit exclusively on training records.
    </div>
    """, unsafe_allow_html=True)

    # Metrics comparison
    if model_comp_df is not None:
        st.subheader("Test Set Performance Summary")
        st.table(model_comp_df)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Random Forest R²", "0.9120", "+0.712 vs Linear Baseline")
        with col_m2:
            st.metric("Random Forest MAE", "382.78 vph", "-1,158 vph error reduction")
        with col_m3:
            st.metric("Random Forest RMSE", "583.51 vph", "-1,176 vph error reduction")

    st.markdown("---")
    st.subheader("Actual vs. Predicted Traffic Snapshot (Test Set)")
    if os.path.exists("output/figures/06_actual_vs_predicted_traffic.png"):
        st.image("output/figures/06_actual_vs_predicted_traffic.png", caption="7-Day Consecutive Actual vs. Predicted Traffic Curve", use_container_width=True)

    if test_sample_df is not None:
        with st.expander("Explore Test Set Predictions Sample (First 50 Records)"):
            st.dataframe(
                test_sample_df[["date_time", "hour", "day_of_week", "weather_main", "temp", "traffic_volume", "prediction"]].head(50),
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# Section 4: Live Traffic Predictor
# -----------------------------------------------------------------------------
elif nav_choice == "Live Traffic Predictor":
    st.markdown('<div class="main-header">Real-Time Traffic Volume Estimator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive Inference Powered by Spark MLlib Random Forest Model</div>', unsafe_allow_html=True)

    st.info("Adjust the temporal, calendar, and meteorological parameters below to estimate expected hourly interstate traffic volume.")

    col_input1, col_input2, col_input3 = st.columns(3)

    with col_input1:
        st.markdown("### 🕒 Temporal Parameters")
        hour_val = st.slider("Hour of Day (0–23):", 0, 23, 8)
        day_mapping = {
            "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4,
            "Thursday": 5, "Friday": 6, "Saturday": 7
        }
        day_name = st.selectbox("Day of Week:", list(day_mapping.keys()), index=2) # Tuesday default
        day_of_week_val = day_mapping[day_name]
        is_weekend_val = 1 if day_of_week_val in (1, 7) else 0

        month_val = st.slider("Month of Year (1–12):", 1, 12, 10)

    with col_input2:
        st.markdown("### 🌦️ Weather Parameters")
        weather_categories = ["Clear", "Clouds", "Rain", "Drizzle", "Snow", "Mist", "Haze", "Fog", "Thunderstorm", "Squall", "Smoke"]
        weather_val = st.selectbox("Main Weather Category:", weather_categories, index=1)

        # Temperature in Celsius with Kelvin conversion display
        temp_celsius = st.slider("Temperature (°C):", -30, 40, 15)
        temp_kelvin = round(temp_celsius + 273.15, 2)
        st.caption(f"Equivalent Kelvin: **{temp_kelvin} K**")

        clouds_val = st.slider("Cloud Coverage (%):", 0, 100, 40)

    with col_input3:
        st.markdown("### 🌧️ Precipitation & Calendar")
        rain_val = st.number_input("Rainfall in past 1h (mm):", min_value=0.0, max_value=80.0, value=0.0, step=0.5)
        snow_val = st.number_input("Snowfall in past 1h (mm):", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
        
        holiday_list = [
            "None", "Columbus Day", "Veterans Day", "Thanksgiving Day", "Christmas Day",
            "New Years Day", "Martin Luther King Jr Day", "Washingtons Birthday",
            "Memorial Day", "Independence Day", "State Fair", "Labor Day"
        ]
        holiday_val = st.selectbox("Holiday Designation:", holiday_list, index=0)

    st.markdown("---")
    
    if st.button("Generate Traffic Prediction", type="primary", use_container_width=True):
        with st.spinner("Executing inference via Spark MLlib Pipeline..."):
            spark, model = get_spark_and_model()
            if model is None:
                st.error("Model artifact not found at output/models/rf_traffic_pipeline. Please run src/05_train_model.py first.")
            else:
                input_row = [{
                    "hour": int(hour_val),
                    "day_of_week": int(day_of_week_val),
                    "month": int(month_val),
                    "is_weekend": int(is_weekend_val),
                    "temp": float(temp_kelvin),
                    "rain_1h": float(rain_val),
                    "snow_1h": float(snow_val),
                    "clouds_all": int(clouds_val),
                    "weather_main": str(weather_val),
                    "holiday": str(holiday_val)
                }]
                
                input_spark_df = spark.createDataFrame(input_row)
                pred_spark_df = model.transform(input_spark_df)
                predicted_volume = pred_spark_df.select("prediction").collect()[0][0]
                pred_int = int(round(predicted_volume))

                # Categorize congestion level
                if pred_int < 1500:
                    status = "Light Flow"
                    color = "#10B981"
                    desc = "Freeway operating near free-flow speeds. Minimal delays expected."
                elif pred_int < 3500:
                    status = "Moderate Traffic"
                    color = "#3B82F6"
                    desc = "Normal interstate volume. Minor slowdowns near interchanges."
                elif pred_int < 5000:
                    status = "Heavy Traffic"
                    color = "#F59E0B"
                    desc = "Peak commute volume. Significant congestion at merge points."
                else:
                    status = "Severe Congestion"
                    color = "#EF4444"
                    desc = "Near road capacity. Stop-and-go conditions likely."

                st.markdown(f"""
                <div style="background-color: {color}15; border: 2px solid {color}; border-radius: 12px; padding: 24px; text-align: center; margin-top: 15px;">
                    <div style="font-size: 1.1rem; color: #4B5563; font-weight: 600;">ESTIMATED TRAFFIC VOLUME</div>
                    <div style="font-size: 3.2rem; font-weight: 800; color: {color}; margin: 8px 0;">{pred_int:,} <span style="font-size: 1.4rem;">vehicles / hour</span></div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: {color};">{status}</div>
                    <div style="font-size: 0.95rem; color: #374151; margin-top: 6px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 5: Data Dictionary & Limitations
# -----------------------------------------------------------------------------
elif nav_choice == "Data Dictionary & Limitations":
    st.markdown('<div class="main-header">Data Dictionary, Assumptions & Limitations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Methodological Details, Feature Descriptions, and Operational Boundaries</div>', unsafe_allow_html=True)

    st.subheader("Data Dictionary")
    data_dict = [
        {"Feature": "holiday", "Type": "Categorical (String)", "Unit": "None / Name", "Description": "US national and Minnesota state holiday name, or literal 'None' for regular days."},
        {"Feature": "temp", "Type": "Continuous (Float)", "Unit": "Kelvin (K)", "Description": "Average hourly ambient temperature. Values at 0.0 K were treated as missing sensor faults."},
        {"Feature": "rain_1h", "Type": "Continuous (Float)", "Unit": "Millimeters (mm)", "Description": "Amount of rain in mm that occurred in the hour. Values > 100 mm treated as sensor glitches."},
        {"Feature": "snow_1h", "Type": "Continuous (Float)", "Unit": "Millimeters (mm)", "Description": "Amount of snow in mm that occurred in the hour. 48,124 observations are 0.0 mm."},
        {"Feature": "clouds_all", "Type": "Discrete (Integer)", "Unit": "Percentage (%)", "Description": "Percentage of cloud cover from 0% (clear) to 100% (fully overcast)."},
        {"Feature": "weather_main", "Type": "Categorical (String)", "Unit": "Category", "Description": "Short text summary of weather (e.g., Clear, Clouds, Rain, Snow, Mist)."},
        {"Feature": "weather_description", "Type": "Categorical (String)", "Unit": "Category", "Description": "Granular description of weather condition."},
        {"Feature": "date_time", "Type": "Timestamp", "Unit": "YYYY-MM-DD HH:MM:SS", "Description": "Hourly observation timestamp in Central Standard Time (CST)."},
        {"Feature": "traffic_volume (Target)", "Type": "Discrete (Integer)", "Unit": "Vehicles / Hour", "Description": "Hourly westbound Interstate 94 traffic volume at sensor station."}
    ]
    st.table(pd.DataFrame(data_dict))

    st.markdown("---")
    st.subheader("Operational Assumptions & Critical Model Limitations")
    st.markdown("""
    1. **Target Interpretation (Volume vs. Speed):**
       - The target variable `traffic_volume` measures **hourly vehicle throughput count** (vehicles per hour), **NOT** travel speed (mph) or delay duration (minutes).
       - In severe gridlock (traffic jam breakdown), vehicle counts may paradoxically drop because vehicles are stopped.
    2. **Causation vs. Association:**
       - Statistical associations identified in exploratory analysis (e.g., higher traffic under "Clouds" weather) do not imply that clouds cause higher driving volumes; rather, both correlate with daytime commute hours.
    3. **Forecasting Scope & Limitations:**
       - The trained models estimate volume conditioned on hour, day, month, and contemporaneous weather. They do not forecast future multi-day traffic without future weather forecasts and scheduled roadwork data.
    4. **Extrapolation Caution:**
       - Model predictions should not be extrapolated to different interstate corridors, eastbound traffic, or catastrophic road closure events not represented in the historical data.
    """)

# Footer
st.markdown("---")
st.caption("Traffic Congestion Analysis and Prediction Project • Built with PySpark, Spark SQL, Spark MLlib, and Streamlit • 2026")
