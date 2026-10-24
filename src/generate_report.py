"""
Generate simplified project report PDF for INT315 submission.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_PATH = os.path.join(PROJECT_DIR, "docs", "Traffic_Congestion_Analysis_Report.pdf")
LOGO_PATH = os.path.join(PROJECT_DIR, "docs", "lpu_logo-removebg-preview.png")
FIGURES_DIR = os.path.join(PROJECT_DIR, "output", "figures")

# Page dimensions
PAGE_W, PAGE_H = A4

def build_report():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, leading=26, alignment=TA_CENTER,
        spaceAfter=6
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading1'],
        fontSize=14, leading=18, spaceAfter=8, spaceBefore=14
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading', parent=styles['Heading2'],
        fontSize=12, leading=15, spaceAfter=6, spaceBefore=10
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=11, leading=15, alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    caption_style = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontSize=9, leading=12, alignment=TA_CENTER,
        spaceAfter=10, textColor=colors.grey
    )
    center_style = ParagraphStyle(
        'Center', parent=styles['Normal'],
        fontSize=11, leading=14, alignment=TA_CENTER
    )

    elements = []

    # ============================
    # COVER PAGE
    # ============================
    elements.append(Spacer(1, 0.5*inch))
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=1.8*inch, height=1.8*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("LOVELY PROFESSIONAL UNIVERSITY", ParagraphStyle(
        'Uni', parent=styles['Title'], fontSize=16, leading=20, alignment=TA_CENTER
    )))
    elements.append(Paragraph("School of Computer Science and Engineering", center_style))
    elements.append(Spacer(1, 0.4*inch))

    elements.append(Paragraph(
        "Traffic Congestion Analysis and Prediction<br/>Using PySpark",
        title_style
    ))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("INT315 — Cluster Computing", ParagraphStyle(
        'Course', parent=styles['Normal'], fontSize=13, alignment=TA_CENTER,
        leading=16, spaceAfter=4
    )))
    elements.append(Spacer(1, 0.5*inch))

    # Student details table
    details = [
        ["Submitted By:", "Hridayesh Debsarma"],
        ["Registration No:", "12316520"],
        ["Course Code:", "INT315"],
        ["Course Title:", "Cluster Computing"],
        ["Semester:", "6th"],
    ]
    detail_table = Table(details, colWidths=[2.2*inch, 3*inch])
    detail_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    detail_table.hAlign = 'CENTER'
    elements.append(detail_table)
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("October 2026", center_style))

    elements.append(PageBreak())

    # ============================
    # TABLE OF CONTENTS
    # ============================
    elements.append(Paragraph("Table of Contents", heading_style))
    toc_items = [
        "1. Introduction",
        "2. Objective",
        "3. Dataset Description",
        "4. Tools and Technologies Used",
        "5. Data Cleaning and Preprocessing",
        "6. Exploratory Data Analysis",
        "7. Machine Learning Model",
        "8. Streamlit Dashboard",
        "9. Results and Discussion",
        "10. Conclusion",
        "11. References",
    ]
    for item in toc_items:
        elements.append(Paragraph(item, body_style))
    elements.append(PageBreak())

    # ============================
    # 1. INTRODUCTION
    # ============================
    elements.append(Paragraph("1. Introduction", heading_style))
    elements.append(Paragraph(
        "Traffic congestion is a major problem in urban areas. It leads to wasted time, "
        "increased fuel consumption, and more pollution. Understanding traffic patterns can "
        "help in planning better roads and managing traffic signals. In this project, we analyse "
        "the Metro Interstate Traffic Volume dataset, which contains hourly traffic counts along "
        "with weather data for Interstate 94 highway in Minnesota, USA.",
        body_style
    ))
    elements.append(Paragraph(
        "We use Apache PySpark for processing the data because it can handle large datasets "
        "efficiently using distributed computing. PySpark provides tools like Spark SQL for "
        "querying data and Spark MLlib for building machine learning models.",
        body_style
    ))

    # ============================
    # 2. OBJECTIVE
    # ============================
    elements.append(Paragraph("2. Objective", heading_style))
    elements.append(Paragraph(
        "The main objectives of this project are:", body_style
    ))
    objectives = [
        "• Clean and preprocess the raw traffic dataset using PySpark",
        "• Perform exploratory data analysis to find patterns in traffic flow",
        "• Build a machine learning model to predict traffic volume based on weather and time features",
        "• Create a simple web dashboard using Streamlit to display the results",
    ]
    for obj in objectives:
        elements.append(Paragraph(obj, body_style))

    # ============================
    # 3. DATASET DESCRIPTION
    # ============================
    elements.append(Paragraph("3. Dataset Description", heading_style))
    elements.append(Paragraph(
        "The dataset is from the UCI Machine Learning Repository. It contains 48,204 hourly "
        "observations of westbound traffic on Interstate 94 between Minneapolis and St. Paul, "
        "collected from 2012 to 2018. Each row has a timestamp, weather information, and the "
        "traffic volume (number of vehicles per hour).",
        body_style
    ))
    elements.append(Spacer(1, 0.1*inch))

    # Data dictionary table
    data_dict = [
        ["Column", "Type", "Description"],
        ["holiday", "String", "Name of holiday or 'None'"],
        ["temp", "Float", "Temperature in Kelvin"],
        ["rain_1h", "Float", "Rainfall in last 1 hour (mm)"],
        ["snow_1h", "Float", "Snowfall in last 1 hour (mm)"],
        ["clouds_all", "Integer", "Cloud cover percentage (0-100%)"],
        ["weather_main", "String", "Weather category (Clear, Clouds, Rain, etc.)"],
        ["date_time", "Timestamp", "Date and time of observation"],
        ["traffic_volume", "Integer", "Number of vehicles per hour (target)"],
    ]
    dict_table = Table(data_dict, colWidths=[1.3*inch, 0.9*inch, 3.3*inch])
    dict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    dict_table.hAlign = 'CENTER'
    elements.append(dict_table)
    elements.append(Paragraph("Table 1: Dataset Column Descriptions", caption_style))

    # ============================
    # 4. TOOLS AND TECHNOLOGIES
    # ============================
    elements.append(Paragraph("4. Tools and Technologies Used", heading_style))
    tools = [
        ["Tool", "Purpose"],
        ["Python 3.10", "Main programming language"],
        ["Apache Spark / PySpark", "Distributed data processing"],
        ["Spark SQL", "SQL queries on dataframes"],
        ["Spark MLlib", "Machine learning library"],
        ["Streamlit", "Web dashboard framework"],
        ["Matplotlib", "Creating charts and plots"],
        ["Pandas", "Data manipulation"],
    ]
    tools_table = Table(tools, colWidths=[2.2*inch, 3.3*inch])
    tools_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    tools_table.hAlign = 'CENTER'
    elements.append(tools_table)
    elements.append(Paragraph("Table 2: Tools and Technologies", caption_style))

    elements.append(PageBreak())

    # ============================
    # 5. DATA CLEANING
    # ============================
    elements.append(Paragraph("5. Data Cleaning and Preprocessing", heading_style))
    elements.append(Paragraph(
        "Before analysing the data, we need to clean it. The raw dataset had some problems "
        "that we fixed:", body_style
    ))
    cleaning_steps = [
        "• <b>Duplicate rows:</b> We found and removed duplicate records so that the same "
        "observation is not counted twice.",
        "• <b>Temperature errors:</b> Some rows had temperature as 0 Kelvin (which is -273°C "
        "and physically impossible). We treated these as missing values.",
        "• <b>Extreme rain values:</b> A few rows showed rainfall above 100mm in one hour, "
        "which looked like sensor errors. We capped these values.",
        "• <b>Feature engineering:</b> We extracted useful time features from the timestamp — "
        "hour of the day, day of the week, month, and whether it is a weekend or not.",
        "• <b>Output format:</b> The cleaned data was saved as Parquet format, which is more "
        "efficient than CSV for big data processing.",
    ]
    for step in cleaning_steps:
        elements.append(Paragraph(step, body_style))

    elements.append(Paragraph(
        "After cleaning, we had 48,187 usable records.", body_style
    ))

    # ============================
    # 6. EDA
    # ============================
    elements.append(PageBreak())
    elements.append(Paragraph("6. Exploratory Data Analysis", heading_style))
    elements.append(Paragraph(
        "We used Spark SQL and PySpark to group and aggregate the data to find interesting "
        "patterns. Here are the main findings:", body_style
    ))

    # 6.1 Hourly
    elements.append(Paragraph("6.1 Hourly Traffic Pattern", subheading_style))
    elements.append(Paragraph(
        "Traffic follows a clear daily pattern. On weekdays, there are two peaks — one in the "
        "morning around 7-8 AM (people going to work) and another in the evening around 4-5 PM "
        "(people coming back). The evening peak is slightly higher at about 6,190 vehicles per hour. "
        "On weekends, traffic builds slowly and reaches a single broad peak in the afternoon.",
        body_style
    ))
    fig1 = os.path.join(FIGURES_DIR, "01_hourly_traffic_profile.png")
    if os.path.exists(fig1):
        img = Image(fig1, width=5.5*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 1: Hourly Traffic Profile", caption_style))

    # 6.2 Weekday vs Weekend
    elements.append(Paragraph("6.2 Weekday vs Weekend", subheading_style))
    fig2 = os.path.join(FIGURES_DIR, "02_weekday_vs_weekend_comparison.png")
    if os.path.exists(fig2):
        img = Image(fig2, width=5.5*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 2: Weekday vs Weekend Traffic Comparison", caption_style))

    elements.append(Paragraph(
        "The weekday curve is bimodal (two humps) while the weekend curve is unimodal (one hump). "
        "This makes sense because people have regular commute times on working days but travel "
        "more freely on weekends.",
        body_style
    ))

    # 6.3 Monthly
    elements.append(PageBreak())
    elements.append(Paragraph("6.3 Monthly Trends", subheading_style))
    elements.append(Paragraph(
        "Summer months like June and August have higher traffic volumes, probably because of "
        "better weather and tourism. Winter months, especially December and January, show lower "
        "traffic due to cold temperatures and snowfall.",
        body_style
    ))
    fig3 = os.path.join(FIGURES_DIR, "03_monthly_traffic_trends.png")
    if os.path.exists(fig3):
        img = Image(fig3, width=5.5*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 3: Monthly Traffic Averages", caption_style))

    # 6.4 Weather
    elements.append(Paragraph("6.4 Weather Impact", subheading_style))
    elements.append(Paragraph(
        "We grouped traffic by weather type. Clear and cloudy weather shows higher average traffic, "
        "but this is mainly because these weather types are common during peak commute hours. "
        "Bad weather like thunderstorms and fog shows lower traffic because fewer people drive "
        "in such conditions.",
        body_style
    ))
    fig4 = os.path.join(FIGURES_DIR, "04_weather_impact_on_traffic.png")
    if os.path.exists(fig4):
        img = Image(fig4, width=5.5*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 4: Traffic by Weather Type", caption_style))

    # 6.5 Holiday
    elements.append(Paragraph("6.5 Holiday Effect", subheading_style))
    elements.append(Paragraph(
        "On holidays, traffic drops significantly — about 73% less than regular days. The "
        "average traffic on regular days is around 3,263 vehicles/hour, while on holidays it "
        "drops to about 865 vehicles/hour.",
        body_style
    ))
    fig5 = os.path.join(FIGURES_DIR, "05_holiday_traffic_comparison.png")
    if os.path.exists(fig5):
        img = Image(fig5, width=5*inch, height=3*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 5: Holiday vs Regular Day Traffic", caption_style))

    # ============================
    # 7. MACHINE LEARNING
    # ============================
    elements.append(PageBreak())
    elements.append(Paragraph("7. Machine Learning Model", heading_style))
    elements.append(Paragraph(
        "We used Spark MLlib to train a machine learning model that predicts traffic volume "
        "based on the time and weather features.", body_style
    ))

    elements.append(Paragraph("7.1 Feature Selection", subheading_style))
    elements.append(Paragraph(
        "The input features we used are: hour, day_of_week, month, is_weekend, temp, rain_1h, "
        "snow_1h, clouds_all, weather_main, and holiday. The target variable is traffic_volume.",
        body_style
    ))

    elements.append(Paragraph("7.2 Train-Test Split", subheading_style))
    elements.append(Paragraph(
        "We split the data chronologically — first 80% for training (Oct 2012 to Nov 2017) and "
        "last 20% for testing (Nov 2017 to Sep 2018). We did this instead of random splitting "
        "because traffic data is time-based, and using future data to predict past data would "
        "not be realistic.",
        body_style
    ))

    elements.append(Paragraph("7.3 Models Trained", subheading_style))
    elements.append(Paragraph(
        "We trained two models and compared them:", body_style
    ))

    model_results = [
        ["Model", "R² Score", "MAE", "RMSE"],
        ["Linear Regression", "0.2000", "1,540.8", "1,759.5"],
        ["Random Forest", "0.9120", "382.8", "583.5"],
    ]
    model_table = Table(model_results, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    model_table.hAlign = 'CENTER'
    elements.append(model_table)
    elements.append(Paragraph("Table 3: Model Performance Comparison", caption_style))

    elements.append(Paragraph(
        "The Random Forest model is much better with an R² score of 0.912, which means it "
        "explains about 91% of the variation in traffic volume. The MAE of 382.8 means that "
        "on average, the prediction is off by about 383 vehicles per hour.",
        body_style
    ))

    fig6 = os.path.join(FIGURES_DIR, "06_actual_vs_predicted_traffic.png")
    if os.path.exists(fig6):
        img = Image(fig6, width=5.5*inch, height=3.2*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Paragraph("Figure 6: Actual vs Predicted Traffic Volume", caption_style))

    # ============================
    # 8. STREAMLIT DASHBOARD
    # ============================
    elements.append(PageBreak())
    elements.append(Paragraph("8. Streamlit Dashboard", heading_style))
    elements.append(Paragraph(
        "We built a simple web dashboard using Streamlit to display the analysis results "
        "and allow users to make traffic predictions. The dashboard has four pages:",
        body_style
    ))
    pages = [
        "• <b>Overview:</b> Shows a summary of the project and key numbers",
        "• <b>EDA:</b> Displays charts for hourly trends, monthly patterns, weather impact, and holiday comparison",
        "• <b>Model Results:</b> Shows the model performance metrics and actual vs predicted plot",
        "• <b>Predict Traffic:</b> Users can enter time and weather details to get a traffic volume prediction",
    ]
    for p in pages:
        elements.append(Paragraph(p, body_style))

    elements.append(Paragraph(
        "The dashboard runs locally using the command: streamlit run app.py",
        body_style
    ))

    # ============================
    # 9. RESULTS AND DISCUSSION
    # ============================
    elements.append(Paragraph("9. Results and Discussion", heading_style))
    elements.append(Paragraph(
        "The key findings from this project are:", body_style
    ))
    findings = [
        "• Traffic follows a predictable daily pattern with morning and evening rush hours on weekdays.",
        "• Weekends have a different pattern with a single afternoon peak.",
        "• Summer months have higher traffic than winter months.",
        "• Holidays cause a big drop in traffic volume (about 73% less).",
        "• The Random Forest model predicts traffic volume quite well with R² = 0.912.",
        "• Time features (hour, day, month) are more important than weather features for prediction.",
    ]
    for f in findings:
        elements.append(Paragraph(f, body_style))

    elements.append(Paragraph(
        "One limitation is that this model only works for this specific highway. It cannot be "
        "directly used for other roads or cities. Also, the model uses current weather, so it "
        "cannot forecast traffic for future days unless we also have weather forecasts.",
        body_style
    ))

    # ============================
    # 10. CONCLUSION
    # ============================
    elements.append(Paragraph("10. Conclusion", heading_style))
    elements.append(Paragraph(
        "In this project, we successfully used PySpark to process and analyse a large traffic "
        "dataset. We cleaned the data, performed exploratory analysis, and trained a Random "
        "Forest model that can predict hourly traffic volume with good accuracy (R² = 0.912). "
        "We also built a Streamlit dashboard to present the results in an interactive way. "
        "This project shows how distributed computing tools like Apache Spark can be used for "
        "real-world data analysis tasks.",
        body_style
    ))

    # ============================
    # 11. REFERENCES
    # ============================
    elements.append(Paragraph("11. References", heading_style))
    refs = [
        "1. UCI Machine Learning Repository — Metro Interstate Traffic Volume Dataset",
        "2. Apache Spark Documentation — https://spark.apache.org/docs/latest/",
        "3. PySpark MLlib Guide — https://spark.apache.org/docs/latest/ml-guide.html",
        "4. Streamlit Documentation — https://docs.streamlit.io/",
        "5. Matplotlib Documentation — https://matplotlib.org/stable/",
    ]
    for r in refs:
        elements.append(Paragraph(r, body_style))

    # Build PDF
    doc.build(elements)
    print(f"Report saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_report()
