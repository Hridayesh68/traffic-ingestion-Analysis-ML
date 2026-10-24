#!/usr/bin/env python3
"""
Generate comprehensive Project Report in both DOCX and PDF formats for INT315.
Incorporates all figures from 'docs/images pdf' and 'output/figures', with formal
academic project report headings, titles, student metadata, data tables, and captions.
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
IMAGES_PDF_DIR = os.path.join(DOCS_DIR, "images pdf")
FIGURES_DIR = os.path.join(PROJECT_DIR, "output", "figures")
LOGO_PATH = os.path.join(DOCS_DIR, "lpu_logo-removebg-preview.png")

OUTPUT_DOCX_PATH = os.path.join(DOCS_DIR, "Traffic_Congestion_Analysis_Report.docx")
OUTPUT_PDF_PATH = os.path.join(DOCS_DIR, "Traffic_Congestion_Analysis_Report.pdf")

# Images from 'docs/images pdf'
IMG_CODE1 = os.path.join(IMAGES_PDF_DIR, "code1.png")
IMG_CODE2 = os.path.join(IMAGES_PDF_DIR, "code 2.png")
IMG_CODE3 = os.path.join(IMAGES_PDF_DIR, "code 3 (2).png")
IMG_OVERVIEW = os.path.join(IMAGES_PDF_DIR, "img1 overview.png")
IMG_EDA = os.path.join(IMAGES_PDF_DIR, "img2 EDA.png")
IMG_PREDICT = os.path.join(IMAGES_PDF_DIR, "img3 prediction .png")

# Analytical figures from 'output/figures'
FIG_HOURLY = os.path.join(FIGURES_DIR, "01_hourly_traffic_profile.png")
FIG_WEEKDAY = os.path.join(FIGURES_DIR, "02_weekday_vs_weekend_comparison.png")
FIG_MONTHLY = os.path.join(FIGURES_DIR, "03_monthly_traffic_trends.png")
FIG_WEATHER = os.path.join(FIGURES_DIR, "04_weather_impact_on_traffic.png")
FIG_HOLIDAY = os.path.join(FIGURES_DIR, "05_holiday_traffic_comparison.png")
FIG_ACT_PRED = os.path.join(FIGURES_DIR, "06_actual_vs_predicted_traffic.png")


# ==============================================================================
# 1. DOCX GENERATOR
# ==============================================================================

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_styled_table(doc, data, col_widths, is_header=True):
    table = doc.add_table(rows=len(data), cols=len(col_widths))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for i, row_data in enumerate(data):
        row = table.rows[i]
        for j, text in enumerate(row_data):
            cell = row.cells[j]
            cell.width = col_widths[j]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(text)
            run.font.name = 'Times New Roman'

            if i == 0 and is_header:
                set_cell_background(cell, "1E3A8A")
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                else:
                    set_cell_background(cell, "FFFFFF")
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(30, 41, 59)
                
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="94A3B8"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    return table

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p

def add_body_p(doc, text, bold_prefix=None, space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
        
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_bullet_p(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
        
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_image_with_caption(doc, img_path, caption_text, width_inches=6.0):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(3)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = False
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(100, 116, 139)

def generate_docx():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # COVER PAGE
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(5)
    p_logo.paragraph_format.space_after = Pt(10)
    if os.path.exists(LOGO_PATH):
        r_logo = p_logo.add_run()
        r_logo.add_picture(LOGO_PATH, width=Inches(1.6))

    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_after = Pt(2)
    r_uni = p_uni.add_run("LOVELY PROFESSIONAL UNIVERSITY")
    r_uni.font.name = 'Times New Roman'
    r_uni.font.size = Pt(16)
    r_uni.font.bold = True
    r_uni.font.color.rgb = RGBColor(15, 23, 42)

    p_sch = doc.add_paragraph()
    p_sch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sch.paragraph_format.space_after = Pt(18)
    r_sch = p_sch.add_run("School of Computer Science and Engineering\nDiscipline of Computer Science & Engineering")
    r_sch.font.name = 'Times New Roman'
    r_sch.font.size = Pt(11.5)
    r_sch.font.color.rgb = RGBColor(71, 85, 105)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("ACADEMIC TASK: CA-PROJECT REPORT")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(194, 65, 12)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("TRAFFIC CONGESTION ANALYSIS AND PREDICTION USING APACHE PYSPARK")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.paragraph_format.space_after = Pt(28)
    r_desc = p_desc.add_run("An End-to-End Distributed Big Data Analytics Pipeline & Interactive Prediction System")
    r_desc.font.name = 'Times New Roman'
    r_desc.font.size = Pt(11)
    r_desc.font.italic = True
    r_desc.font.color.rgb = RGBColor(100, 116, 139)

    meta_data = [
        ["Submitted By:", "Hridayesh Debsarma"],
        ["Registration No:", "12316520"],
        ["Course Code:", "INT315"],
        ["Course Title:", "Cluster Computing"],
        ["Academic Task:", "CA-Project (Max Marks: 30)"],
        ["Target Outcomes:", "CO4, CO5, CO6 (Bloom's Level L6: Create)"],
        ["Semester / Session:", "6th Semester / 2026-27"],
        ["Date of Submission:", "October 2026"]
    ]
    t_meta = doc.add_table(rows=len(meta_data), cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (label, val) in enumerate(meta_data):
        row = t_meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(3.8)
        set_cell_margins(c0, 50, 50, 80, 80)
        set_cell_margins(c1, 50, 50, 80, 80)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.font.name = 'Times New Roman'
        r0.font.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(30, 41, 59)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()

    # DECLARATION & CERTIFICATE
    add_heading_1(doc, "DECLARATION")
    add_body_p(doc, 
        "I hereby declare that the project work entitled \"Traffic Congestion Analysis and Prediction Using Apache PySpark\" "
        "submitted to Lovely Professional University, Punjab, is an authentic record of original work done by me under the course "
        "INT315 (Cluster Computing). The project demonstrates distributed data engineering, exploratory data analysis using "
        "Spark SQL, machine learning modeling with Spark MLlib, and interactive dashboard deployment using Streamlit.",
        space_after=14
    )
    add_body_p(doc, 
        "I further declare that this report has not been submitted previously in part or full to any other university or "
        "institution for the award of any academic degree, diploma, or certificate.",
        space_after=28
    )

    t_dec = doc.add_table(rows=2, cols=2)
    t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dec.rows[0].cells[0].paragraphs[0].add_run("Date: 22 October 2026\nPlace: Phagwara, Punjab").font.size = Pt(10)
    t_dec.rows[0].cells[1].paragraphs[0].add_run("Hridayesh Debsarma\nRegistration No: 12316520\nSchool of CSE, LPU").font.size = Pt(10)
    t_dec.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    doc.add_paragraph().paragraph_format.space_before = Pt(20)

    add_heading_1(doc, "CERTIFICATE")
    add_body_p(doc, 
        "This is to certify that Hridayesh Debsarma bearing Registration No. 12316520 has successfully completed the "
        "course project titled \"Traffic Congestion Analysis and Prediction Using Apache PySpark\" for INT315 (Cluster Computing) "
        "under my guidance and supervision. To the best of my knowledge, the present work is the result of his intensive original development, "
        "effort, and study.",
        space_after=32
    )

    t_cert = doc.add_table(rows=2, cols=2)
    t_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cert.rows[0].cells[0].paragraphs[0].add_run("Faculty Coordinator / Supervisor\nDiscipline of CSE/IT\nLovely Professional University").font.size = Pt(10)
    t_cert.rows[0].cells[1].paragraphs[0].add_run("Head of Department\nSchool of Computer Science & Engineering\nLovely Professional University").font.size = Pt(10)
    t_cert.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # ACKNOWLEDGEMENT & TOC
    add_heading_1(doc, "ACKNOWLEDGEMENT")
    add_body_p(doc, 
        "I express my deepest gratitude to Lovely Professional University and the School of Computer Science and Engineering "
        "for offering the academic curriculum and technical infrastructure that made this project possible. I am sincerely "
        "thankful to my course instructor and mentor for INT315 (Cluster Computing) for their invaluable guidance, encouragement, "
        "and continuous constructive feedback throughout the course of this project.",
        space_after=10
    )
    add_body_p(doc, 
        "I also thank the open-source community behind Apache Spark, Python, and Streamlit, as well as the UCI Machine Learning "
        "Repository for publishing the Metro Interstate 94 Traffic Volume dataset.",
        space_after=20
    )

    add_heading_1(doc, "TABLE OF CONTENTS")
    toc_data = [
        ("1. Executive Summary & Project Overview", "4"),
        ("2. Introduction & Problem Statement", "4"),
        ("3. Scope and Objectives of the Analysis", "5"),
        ("4. Existing Systems vs. Distributed PySpark Architecture", "5"),
        ("5. Dataset Description & Technical Data Dictionary", "6"),
        ("6. Tools and Technologies Stack", "6"),
        ("7. Data Cleaning, Sanitization & Preprocessing Pipeline", "7"),
        ("    7.1 Data Quality Checks & Sensor Anomaly Resolution", "7"),
        ("    7.2 Code Implementation: Ingestion & Validation (Figure 1)", "7"),
        ("8. Exploratory Data Analysis with Spark SQL", "8"),
        ("    8.1 Code Implementation: Spark SQL Queries (Figure 2)", "8"),
        ("    8.2 Hourly Rush Hour Dynamics (Figure 3)", "8"),
        ("    8.3 Weekday vs. Weekend Commute Profiles (Figure 4)", "9"),
        ("    8.4 Seasonal & Monthly Trends (Figure 5)", "9"),
        ("    8.5 Meteorological & Weather Impact (Figure 6)", "10"),
        ("    8.6 Holiday Volume Suppression (Figure 7)", "10"),
        ("9. Machine Learning Modeling & PySpark MLlib Pipeline", "11"),
        ("    9.1 Code Implementation: Spark MLlib Pipeline (Figure 8)", "11"),
        ("    9.2 Chronological Split & Feature Engineering Rationale", "11"),
        ("    9.3 Model Performance Comparison (Table 3 & Figure 9)", "12"),
        ("10. Interactive Streamlit Web Dashboard Application", "13"),
        ("    10.1 Executive Overview & KPIs (Figure 10)", "13"),
        ("    10.2 Interactive Exploratory Trends (Figure 11)", "13"),
        ("    10.3 Real-Time Traffic Volume Predictor (Figure 12)", "14"),
        ("11. Results and Discussion", "14"),
        ("12. Limitations and Future Scope", "15"),
        ("13. Conclusion", "15"),
        ("14. References", "15")
    ]
    t_toc = doc.add_table(rows=len(toc_data), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (title_str, p_str) in enumerate(toc_data):
        r = t_toc.rows[i]
        c0, c1 = r.cells[0], r.cells[1]
        c0.width = Inches(5.2)
        c1.width = Inches(0.8)
        set_cell_margins(c0, 15, 15, 30, 30)
        set_cell_margins(c1, 15, 15, 30, 30)
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run0 = p0.add_run(title_str)
        run0.font.name = 'Times New Roman'
        run0.font.size = Pt(9.5)
        if not title_str.startswith("    "):
            run0.font.bold = True
        run1 = p1.add_run(p_str)
        run1.font.name = 'Times New Roman'
        run1.font.size = Pt(9.5)

    doc.add_page_break()

    # 1. & 2.
    add_heading_1(doc, "1. Executive Summary & Project Overview")
    add_body_p(doc, 
        "Rapid urbanization and exponential vehicular density have turned metropolitan traffic congestion into a major "
        "economic, ecological, and civil infrastructure challenge. Traditional single-machine analytics systems face significant "
        "bottlenecks when handling longitudinal, high-frequency sensor streams. This project develops an end-to-end distributed "
        "big data analytics pipeline and predictive machine learning system utilizing Apache PySpark 3.5.9 and Python 3.10."
    )
    add_body_p(doc, 
        "Using 48,204 hourly records spanning 2012 to 2018 from the Metro Interstate 94 corridor (Minneapolis to St. Paul, Minnesota), "
        "we perform distributed data quality audits, sensor fault sanitization (0 K temperature, 9831 mm extreme rainfall), "
        "high-speed aggregation using Spark SQL, feature engineering via Spark MLlib pipelines, and regression modeling. "
        "Our Random Forest Regressor achieves an R² score of 0.9120 (Mean Absolute Error of 382.8 vehicles/hour), radically outperforming "
        "the Linear Regression baseline (R² = 0.2000). The pipeline is coupled to an interactive Streamlit web application providing "
        "real-time congestion forecasting and decision-support dashboards."
    )

    add_heading_1(doc, "2. Introduction & Problem Statement")
    add_body_p(doc, 
        "Modern intelligent transportation systems (ITS) depend heavily on loop detectors, environmental sensors, and telemetry gateways. "
        "Congestion on major interstate arterials leads to thousands of hours of commuter delays, elevated greenhouse gas emissions, "
        "and increased accident risks. Accurate traffic flow prediction allows municipal authorities to proactively optimize variable "
        "speed limits, dispatch emergency response units, and schedule infrastructure maintenance."
    )
    add_body_p(doc, 
        "However, raw traffic sensor feeds exhibit sensor dropouts, transmission duplicates, and extreme environmental fluctuations. "
        "Distributed computing frameworks like Apache Spark offer fault-tolerant resilient distributed datasets (RDDs), Catalyst query "
        "optimization, and native machine learning libraries (MLlib) to process these workloads reliably at scale."
    )

    doc.add_page_break()

    # 3. & 4.
    add_heading_1(doc, "3. Scope and Objectives of the Analysis")
    add_body_p(doc, "The primary objectives of this study, mapped to Bloom's Taxonomy Level L6 (Create) and INT315 Course Outcomes (CO4, CO5, CO6), are:")
    add_bullet_p(doc, "Design and implement a distributed data sanitization pipeline to identify and rectify physical sensor anomalies (0 K temperatures, telemetry gauge faults) and duplicate records.", "1. Distributed Data Engineering: ")
    add_bullet_p(doc, "Execute high-performance analytical queries using Spark SQL to uncover diurnal rush-hour dynamics, weekend commute shifts, meteorological correlations, and holiday volume suppression.", "2. Distributed Exploratory Analytics: ")
    add_bullet_p(doc, "Construct a leak-free PySpark MLlib Pipeline combining StringIndexer, OneHotEncoder, VectorAssembler, and Random Forest Regressor under a rigorous chronological 80/20 train-test split.", "3. Machine Learning at Scale: ")
    add_bullet_p(doc, "Deploy an interactive Streamlit web dashboard presenting executive KPIs, interactive charts, and a real-time traffic inference engine.", "4. Interactive Visualization & Delivery: ")

    add_heading_1(doc, "4. Existing Systems vs. Distributed PySpark Architecture")
    add_body_p(doc, 
        "Traditional transportation management architectures rely predominantly on standalone relational databases (e.g., MySQL, PostgreSQL) "
        "and single-threaded analytics libraries (standard Pandas, Scikit-Learn). While adequate for retrospective batch reports on small samples, "
        "existing systems suffer from critical limitations:"
    )
    add_bullet_p(doc, "Single-machine memory bounds cause out-of-memory (OOM) failures when scaling to millions of streaming detector pings.", "Memory Bottlenecks: ")
    add_bullet_p(doc, "Single-threaded execution cannot exploit multi-core cluster worker nodes or parallel partition executors.", "Scalability Limits: ")
    add_bullet_p(doc, "Rigid database schemas make ad-hoc feature extraction and pipeline serialization computationally expensive.", "Pipeline Fragmentation: ")
    add_body_p(doc, 
        "The proposed PySpark architecture resolves these barriers by distributing partitioned DataFrames across worker nodes, "
        "utilizing lazy evaluation and Catalyst query optimization, and storing intermediate artifacts in columnar Snappy-compressed "
        "Parquet formats, ensuring high throughput and fault tolerance."
    )

    doc.add_page_break()

    # 5. & 6.
    add_heading_1(doc, "5. Dataset Description & Technical Data Dictionary")
    add_body_p(doc, 
        "The dataset used is the Metro Interstate Traffic Volume dataset from the UCI Machine Learning Repository, "
        "collected by the Minnesota Department of Transportation (MnDOT). It contains 48,204 hourly observations of westbound "
        "traffic on Interstate 94 between Minneapolis and St. Paul, Minnesota, spanning October 2012 to September 2018."
    )
    dict_table_data = [
        ["Field Name", "Data Type", "Range / Distinct", "Description & Physical Unit"],
        ["holiday", "String", "12 categories", "US national holiday name or 'None'"],
        ["temp", "Double", "0.0 to 310.07 K", "Ambient air temperature in Kelvin (0 K anomalous)"],
        ["rain_1h", "Double", "0.0 to 9831.3 mm", "Rainfall depth accumulated in the prior hour"],
        ["snow_1h", "Double", "0.0 to 0.51 mm", "Snowfall depth accumulated in the prior hour"],
        ["clouds_all", "Integer", "0% to 100%", "Percentage of cloud coverage from sky cameras"],
        ["weather_main", "String", "11 categories", "Primary meteorological category (Clear, Rain, Snow, etc.)"],
        ["weather_description", "String", "38 categories", "Granular meteorological description"],
        ["date_time", "Timestamp", "2012-10-02 to 2018-09-30", "Hourly observation timestamp (UTC)"],
        ["traffic_volume", "Integer", "0 to 7,280 vph", "Westbound hourly vehicle count (Target variable)"]
    ]
    create_styled_table(doc, dict_table_data, [Inches(1.5), Inches(0.9), Inches(1.4), Inches(2.4)])
    
    p_dict_cap = doc.add_paragraph()
    p_dict_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dict_cap.paragraph_format.space_before = Pt(3)
    p_dict_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_dict_cap.add_run("Table 1: Metro Interstate Traffic Volume Dataset Technical Data Dictionary")
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(9)
    r_cap.font.italic = True
    r_cap.font.color.rgb = RGBColor(100, 116, 139)

    add_heading_1(doc, "6. Tools and Technologies Stack")
    tools_data = [
        ["Technology / Library", "Version", "Functional Role in Project"],
        ["Apache Spark / PySpark", "3.5.9", "Distributed in-memory big data processing engine & DataFrame API"],
        ["Spark SQL", "3.5.9", "Optimized distributed relational queries with Catalyst optimizer"],
        ["Spark MLlib", "3.5.9", "Scalable machine learning pipelines, feature transformation & estimators"],
        ["Python", "3.10.12", "Core programming runtime and scripting environment"],
        ["Streamlit", "1.30+", "Web application framework for real-time dashboarding & inference UI"],
        ["Matplotlib / Seaborn", "3.8+", "Publication-quality exploratory visualizations & analytical charts"],
        ["Pandas & NumPy", "2.1+", "Local matrix conversion and auxiliary tabular data manipulation"],
        ["Apache Parquet / Snappy", "1.0", "Columnar, high-compression persistent storage format"]
    ]
    create_styled_table(doc, tools_data, [Inches(1.8), Inches(0.9), Inches(3.5)])
    
    p_tools_cap = doc.add_paragraph()
    p_tools_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tools_cap.paragraph_format.space_before = Pt(3)
    p_tools_cap.paragraph_format.space_after = Pt(12)
    r_tcap = p_tools_cap.add_run("Table 2: Software Ecosystem and Technical Stack")
    r_tcap.font.name = 'Times New Roman'
    r_tcap.font.size = Pt(9)
    r_tcap.font.italic = True
    r_tcap.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

    # 7. CLEANING & CODE 1
    add_heading_1(doc, "7. Data Cleaning, Sanitization & Preprocessing Pipeline")
    add_heading_2(doc, "7.1 Data Quality Checks & Sensor Anomaly Resolution")
    add_body_p(doc, 
        "Prior to model training, a rigorous data quality audit was conducted using PySpark functions. "
        "The investigation revealed three critical data quality phenomena:"
    )
    add_bullet_p(doc, "Exactly 17 duplicate records had identical values across all 9 columns. These represented telemetry replay artifacts and were pruned using dropDuplicates(). Records sharing identical timestamps but exhibiting distinct meteorological descriptions were preserved as valid multi-condition events.", "Deduplication: ")
    add_bullet_p(doc, "Exactly 10 records recorded temp = 0.0 K (-273.15°C), representing telemetry communication loss. These were set to NULL and later imputed via median value substitution in the MLlib pipeline.", "Temperature Zero Anomaly: ")
    add_bullet_p(doc, "On 2016-07-11 17:00:00, rain_1h was recorded as 9831.3 mm (nearly 10 meters of rain in 60 minutes). This physically unviable value was converted to NULL to prevent outlier distortion.", "Extreme Precipitation Fault: ")
    add_bullet_p(doc, "Extracted hour (0-23), day_of_week (1-7), month (1-12), and a binary is_weekend indicator from date_time.", "Temporal Feature Engineering: ")
    add_body_p(doc, "The cleaned dataset contains 48,187 high-fidelity records and was saved into columnar Parquet format.")

    add_heading_2(doc, "7.2 Code Implementation: PySpark Ingestion & Validation")
    add_body_p(doc, 
        "Figure 1 illustrates the actual code executed in the Jupyter Notebook environment, highlighting the initialization "
        "of the SparkSession with 4 shuffle partitions and 4 GB driver memory, schema inference, and column-wise null checking."
    )
    add_image_with_caption(doc, IMG_CODE1, "Figure 1: PySpark Environment Setup, SparkSession Ingestion, and Missing Value Analysis (code1.png)", width_inches=6.0)

    doc.add_page_break()

    # 8. EDA
    add_heading_1(doc, "8. Exploratory Data Analysis with Spark SQL")
    add_heading_2(doc, "8.1 Code Implementation: Spark SQL Analytical Queries")
    add_body_p(doc, 
        "PySpark's Catalyst optimizer was leveraged by registering the cleaned DataFrame as a temporary SQL view ('traffic'). "
        "Complex aggregation queries were executed to compute hourly volume distributions, weekday versus weekend variances, "
        "monthly seasonal trajectories, and meteorological cross-tabulations."
    )
    add_image_with_caption(doc, IMG_CODE2, "Figure 2: Spark SQL Analytical Queries for Distributed Traffic Aggregations (code 2.png)", width_inches=6.0)

    add_heading_2(doc, "8.2 Hourly Rush Hour Dynamics")
    add_body_p(doc, 
        "Weekday traffic exhibits a pronounced bimodal commute pattern. A sharp morning rush hour occurs between 07:00 and 08:00 (~4,750 vph), "
        "followed by an even heavier evening rush hour between 16:00 and 17:00 peaking at ~4,850 vph. Off-peak nighttime flow drops below 700 vph at 03:00."
    )
    add_image_with_caption(doc, FIG_HOURLY, "Figure 3: Mean Hourly Traffic Volume Profile with ±0.5 Standard Deviation Band", width_inches=5.4)

    doc.add_page_break()

    add_heading_2(doc, "8.3 Weekday vs. Weekend Commute Profiles")
    add_body_p(doc, 
        "Figure 4 reveals a fundamental behavioral contrast. Weekday traffic is driven by work commutes with two distinct peaks. "
        "In contrast, weekend traffic displays a unimodal leisure plateau: traffic builds gradually through the late morning and plateaus "
        "between 12:00 and 17:00 at ~4,300 vph without sharp morning or evening spikes."
    )
    add_image_with_caption(doc, FIG_WEEKDAY, "Figure 4: Commute Dynamics: Weekday (Bimodal) vs. Weekend (Unimodal) Hourly Curves", width_inches=5.4)

    add_heading_2(doc, "8.4 Seasonal & Monthly Trends")
    add_body_p(doc, 
        "Monthly volume trends reflect Minnesota's continental climate. Peak vehicular throughput occurs in summer and early autumn "
        "(June to October, averaging ~3,500 vph), driven by favorable weather, tourism, and road construction detours. Severe winter conditions "
        "in December and January depress traffic volumes to ~3,000 vph."
    )
    add_image_with_caption(doc, FIG_MONTHLY, "Figure 5: Monthly Traffic Volume Seasonal Trajectory", width_inches=5.4)

    doc.add_page_break()

    add_heading_2(doc, "8.5 Meteorological & Weather Impact")
    add_body_p(doc, 
        "While adverse weather conditions such as fog, thunderstorms, and heavy snow reduce highway speeds and vehicular counts, "
        "baseline volume during clear and overcast skies remains high because commuters must travel regardless of ambient clouds."
    )
    add_image_with_caption(doc, FIG_WEATHER, "Figure 6: Mean Traffic Volume Across Primary Meteorological Categories", width_inches=5.4)

    add_heading_2(doc, "8.6 Holiday Volume Suppression")
    add_body_p(doc, 
        "US federal holidays cause an extraordinary 73.5% drop in average hourly volume, falling from 3,263 vph on regular days to "
        "just 865 vph on holidays, emphasizing the necessity of including holiday indicator flags in predictive models."
    )
    add_image_with_caption(doc, FIG_HOLIDAY, "Figure 7: Holiday Volume Suppression vs. Non-Holiday Baseline", width_inches=5.0)

    doc.add_page_break()

    # 9. ML
    add_heading_1(doc, "9. Machine Learning Modeling & PySpark MLlib Pipeline")
    add_heading_2(doc, "9.1 Code Implementation: Spark MLlib Pipeline Architecture")
    add_body_p(doc, 
        "To ensure production scalability and zero data leakage, all preprocessing transformations were encapsulated within a unified "
        "PySpark Pipeline. The pipeline stages include: Imputer (median strategy for temperature and rain), StringIndexer for weather and holiday, "
        "OneHotEncoder for categorical features, VectorAssembler for dense feature vector composition, and regression estimators."
    )
    add_image_with_caption(doc, IMG_CODE3, "Figure 8: Spark MLlib Feature Engineering Pipeline, Chronological Split, and Regression Training (code 3 (2).png)", width_inches=6.0)

    add_heading_2(doc, "9.2 Chronological Split & Feature Engineering Rationale")
    add_body_p(doc, 
        "Standard random cross-validation leaks temporal autocorrelation in time-series data. We implemented an exact chronological 80/20 split: "
        "the first 80% of data (October 2012 to November 2017; 38,549 records) was allocated for training, while the final 20% (November 2017 to "
        "September 2018; 9,638 records) was held out strictly for out-of-time evaluation."
    )

    doc.add_page_break()

    add_heading_2(doc, "9.3 Model Performance Comparison")
    add_body_p(doc, 
        "We compared a baseline Linear Regression model against a distributed Random Forest Regressor (numTrees=60, maxDepth=12, seed=42). "
        "Evaluations were performed using PySpark's RegressionEvaluator across R², Mean Absolute Error (MAE), and Root Mean Squared Error (RMSE)."
    )

    perf_data = [
        ["Model Architecture", "R² Score", "MAE (vph)", "RMSE (vph)", "Performance Assessment"],
        ["Linear Regression (Baseline)", "0.2000", "1,540.8", "1,759.5", "Poor; fails to capture non-linear diurnal rush peaks"],
        ["Random Forest Regressor", "0.9120", "382.8", "583.5", "Superior; explains 91.2% of variance with low error"]
    ]
    create_styled_table(doc, perf_data, [Inches(1.8), Inches(0.9), Inches(1.0), Inches(1.0), Inches(1.5)])
    
    p_perf_cap = doc.add_paragraph()
    p_perf_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_perf_cap.paragraph_format.space_before = Pt(3)
    p_perf_cap.paragraph_format.space_after = Pt(10)
    r_pcap = p_perf_cap.add_run("Table 3: Out-of-Time Model Performance Metrics on 20% Held-Out Test Set")
    r_pcap.font.name = 'Times New Roman'
    r_pcap.font.size = Pt(9)
    r_pcap.font.italic = True
    r_pcap.font.color.rgb = RGBColor(100, 116, 139)

    add_image_with_caption(doc, FIG_ACT_PRED, "Figure 9: Actual vs. Predicted Traffic Volume on Held-Out Test Set (Random Forest Regressor)", width_inches=5.4)

    doc.add_page_break()

    # 10. STREAMLIT
    add_heading_1(doc, "10. Interactive Streamlit Web Dashboard Application")
    add_body_p(doc, 
        "To deliver actionable insights to transportation planners and operators, a web dashboard was built using Streamlit. "
        "The application provides a seamless 4-tier navigation structure: Executive Overview, Exploratory Data Analysis, Model Performance, "
        "and Real-Time Traffic Prediction."
    )

    add_heading_2(doc, "10.1 Executive Overview & Real-Time KPIs")
    add_body_p(doc, 
        "The Overview page (Figure 10) displays key system KPIs: Total Cleaned Records (48,187), Average Highway Traffic (3,260 vph), "
        "Peak Recorded Volume (6,190 vph), and ML Model Accuracy (R² = 0.9120), alongside a visual overview of the end-to-end data pipeline."
    )
    add_image_with_caption(doc, IMG_OVERVIEW, "Figure 10: Streamlit Dashboard - Executive Overview and Key Performance Indicators (img1 overview.png)", width_inches=6.0)

    add_heading_2(doc, "10.2 Interactive Exploratory Trends")
    add_body_p(doc, 
        "The EDA module (Figure 11) allows users to explore interactive diurnal traffic patterns across tabs (Hourly Trends, Monthly Trends, "
        "Weather Impact, and Holidays), dynamically rendering weekday versus weekend commute profiles."
    )
    add_image_with_caption(doc, IMG_EDA, "Figure 11: Streamlit Dashboard - Interactive Exploratory Data Analysis Interface (img2 EDA.png)", width_inches=6.0)

    doc.add_page_break()

    add_heading_2(doc, "10.3 Real-Time Traffic Volume Predictor")
    add_body_p(doc, 
        "The Predictor interface (Figure 12) empowers traffic managers to simulate conditions by adjusting Hour of Day, Day of Week, "
        "Month, Weather Category, Ambient Temperature (°C), Cloud Cover (%), Rainfall (mm), and Holiday Status. The underlying PySpark "
        "model pipeline instantly generates an estimated hourly volume (e.g., 5,608 vph) accompanied by an operational congestion tier classification."
    )
    add_image_with_caption(doc, IMG_PREDICT, "Figure 12: Streamlit Dashboard - Real-Time Traffic Volume Predictor & Congestion Classifier (img3 prediction .png)", width_inches=6.0)

    # 11, 12, 13, 14
    add_heading_1(doc, "11. Results and Discussion")
    add_body_p(doc, 
        "The analytical findings demonstrate that diurnal time-of-day features dominate traffic volume variation. The Random Forest model "
        "captures subtle non-linear interactions between hour of day and weekday/weekend indicators that linear regression completely misses. "
        "Furthermore, federal holidays induce substantial traffic drops (-73.5%), while adverse weather causes moderate slowdowns. "
        "The PySpark distributed architecture achieved linear scaling during data cleaning and sub-minute ML training times."
    )

    add_heading_1(doc, "12. Limitations and Future Scope")
    add_bullet_p(doc, "The current model is calibrated specifically to Interstate 94 westbound between Minneapolis and St. Paul; cross-corridor generalization requires multi-station sensor calibration.", "Geographic Specificity: ")
    add_bullet_p(doc, "Current predictions utilize contemporaneous weather observations. Integrating numerical weather prediction (NWP) API feeds would enable 24-48 hour proactive traffic forecasting.", "Forecasting Horizon: ")
    add_bullet_p(doc, "Future architectures can ingest live telemetry via Apache Kafka and process sliding windows using Spark Structured Streaming.", "Streaming Integration: ")

    add_heading_1(doc, "13. Conclusion")
    add_body_p(doc, 
        "This project successfully engineered and deployed a distributed big data analytics and machine learning pipeline for highway "
        "traffic congestion forecasting using Apache PySpark and Streamlit. By effectively resolving raw sensor anomalies, applying Spark SQL "
        "for scalable aggregations, and fitting a high-accuracy Random Forest MLlib pipeline (R² = 0.9120), the project validates the immense "
        "power of distributed computing for modern intelligent transportation systems."
    )

    add_heading_1(doc, "14. References")
    refs = [
        "1. UCI Machine Learning Repository: Metro Interstate Traffic Volume Dataset (MnDOT, 2018).",
        "2. Zaharia, M. et al. 'Apache Spark: A Unified Engine for Big Data Processing.' Communications of the ACM, 2016.",
        "3. Meng, X. et al. 'MLlib: Machine Learning in Apache Spark.' Journal of Machine Learning Research (JMLR), 2016.",
        "4. Streamlit Documentation: Fast, Interactive Web Applications for Machine Learning (https://docs.streamlit.io).",
        "5. Hunter, J. D. 'Matplotlib: A 2D Graphics Environment.' Computing in Science & Engineering, 2007.",
        "6. Lovely Professional University: INT315 Cluster Computing Laboratory Guidelines & Academic Curriculum, 2026."
    ]
    for r in refs:
        add_bullet_p(doc, r)

    doc.save(OUTPUT_DOCX_PATH)
    print(f"[SUCCESS] DOCX report generated at: {OUTPUT_DOCX_PATH}")


# ==============================================================================
# 2. PDF GENERATOR (REPORTLAB)
# ==============================================================================

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Running header
            self.drawString(54, 802, "Lovely Professional University | INT315 Cluster Computing | Traffic Congestion Analysis")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 796, 541, 796)
            
            # Running footer
            self.line(54, 42, 541, 42)
            self.drawString(54, 32, "Hridayesh Debsarma (Reg: 12316520)")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(541, 32, page_text)
            self.restoreState()


def generate_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF_PATH,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    sub_title_style = ParagraphStyle(
        'CoverSubTitle', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=10.5, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=12.5, leading=15,
        spaceBefore=10, spaceAfter=4, keepWithNext=True,
        textColor=colors.HexColor("#1E3A8A")
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13,
        spaceBefore=8, spaceAfter=3, keepWithNext=True,
        textColor=colors.HexColor("#0F172A")
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12.5,
        alignment=TA_JUSTIFY, spaceAfter=4,
        textColor=colors.HexColor("#1E293B")
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style,
        leftIndent=12, firstLineIndent=-8, spaceAfter=2.5
    )
    caption_style = ParagraphStyle(
        'Cap', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=10,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=8,
        textColor=colors.HexColor("#64748B")
    )
    center_style = ParagraphStyle(
        'Center', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=12.5,
        alignment=TA_CENTER, textColor=colors.HexColor("#334155")
    )

    elements = []

    # PAGE 1: COVER
    elements.append(Spacer(1, 10))
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=1.5*inch, height=1.5*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 10))

    elements.append(Paragraph("LOVELY PROFESSIONAL UNIVERSITY", ParagraphStyle(
        'Uni', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=15, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#0F172A")
    )))
    elements.append(Paragraph("School of Computer Science and Engineering<br/>Discipline of Computer Science & Engineering", center_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("ACADEMIC TASK: CA-PROJECT REPORT", ParagraphStyle(
        'Task', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#C2410C")
    )))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("TRAFFIC CONGESTION ANALYSIS AND PREDICTION<br/>USING APACHE PYSPARK", title_style))
    elements.append(Paragraph("An End-to-End Distributed Big Data Analytics Pipeline & Interactive Prediction System", sub_title_style))
    elements.append(Spacer(1, 10))

    meta_rows = [
        [Paragraph("<b>Submitted By:</b>", body_style), Paragraph("Hridayesh Debsarma", body_style)],
        [Paragraph("<b>Registration No:</b>", body_style), Paragraph("12316520", body_style)],
        [Paragraph("<b>Course Code:</b>", body_style), Paragraph("INT315", body_style)],
        [Paragraph("<b>Course Title:</b>", body_style), Paragraph("Cluster Computing", body_style)],
        [Paragraph("<b>Academic Task:</b>", body_style), Paragraph("CA-Project (Max Marks: 30)", body_style)],
        [Paragraph("<b>Target Outcomes:</b>", body_style), Paragraph("CO4, CO5, CO6 (Bloom's Level L6: Create)", body_style)],
        [Paragraph("<b>Semester:</b>", body_style), Paragraph("6th Semester", body_style)],
        [Paragraph("<b>Date of Submission:</b>", body_style), Paragraph("October 2026", body_style)]
    ]
    t_cover = Table(meta_rows, colWidths=[2.0*inch, 3.5*inch])
    t_cover.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    t_cover.hAlign = 'CENTER'
    elements.append(t_cover)

    elements.append(PageBreak())

    # PAGE 2: DECLARATION & CERTIFICATE
    elements.append(Paragraph("DECLARATION", h1_style))
    elements.append(Paragraph(
        "I hereby declare that the project work entitled <b>\"Traffic Congestion Analysis and Prediction Using Apache PySpark\"</b> "
        "submitted to Lovely Professional University, Punjab, is an authentic record of original work done by me under the course "
        "INT315 (Cluster Computing). The project demonstrates distributed data engineering, exploratory data analysis using "
        "Spark SQL, machine learning modeling with Spark MLlib, and interactive dashboard deployment using Streamlit.",
        body_style
    ))
    elements.append(Paragraph(
        "I further declare that this report has not been submitted previously in part or full to any other university or "
        "institution for the award of any academic degree, diploma, or certificate.",
        body_style
    ))
    elements.append(Spacer(1, 14))

    dec_tbl = Table([
        [Paragraph("<b>Date:</b> 22 October 2026<br/><b>Place:</b> Phagwara, Punjab", body_style),
         Paragraph("<b>Hridayesh Debsarma</b><br/>Registration No: 12316520<br/>School of CSE, LPU", ParagraphStyle('R', parent=body_style, alignment=TA_RIGHT))]
    ], colWidths=[2.8*inch, 3.0*inch])
    dec_tbl.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(dec_tbl)

    elements.append(Spacer(1, 18))
    elements.append(Paragraph("CERTIFICATE", h1_style))
    elements.append(Paragraph(
        "This is to certify that <b>Hridayesh Debsarma</b> bearing Registration No. <b>12316520</b> has successfully completed "
        "the course project titled <b>\"Traffic Congestion Analysis and Prediction Using Apache PySpark\"</b> for INT315 (Cluster Computing) "
        "under my guidance and supervision. To the best of my knowledge, the present work is the result of his intensive original development, "
        "effort, and study.",
        body_style
    ))
    elements.append(Spacer(1, 18))

    cert_tbl = Table([
        [Paragraph("<b>Faculty Coordinator / Supervisor</b><br/>Discipline of CSE/IT<br/>Lovely Professional University", body_style),
         Paragraph("<b>Head of Department</b><br/>School of Computer Science & Engineering<br/>Lovely Professional University", ParagraphStyle('R2', parent=body_style, alignment=TA_RIGHT))]
    ], colWidths=[2.8*inch, 3.0*inch])
    cert_tbl.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(cert_tbl)

    elements.append(PageBreak())

    # PAGE 3: ACKNOWLEDGEMENT & TOC
    elements.append(Paragraph("ACKNOWLEDGEMENT", h1_style))
    elements.append(Paragraph(
        "I express my deepest gratitude to Lovely Professional University and the School of Computer Science and Engineering "
        "for offering the academic curriculum and technical infrastructure that made this project possible. I am sincerely "
        "thankful to my course instructor and mentor for INT315 (Cluster Computing) for their invaluable guidance, encouragement, "
        "and continuous constructive feedback throughout the course of this project.",
        body_style
    ))
    elements.append(Paragraph(
        "I also thank the open-source community behind Apache Spark, Python, and Streamlit, as well as the UCI Machine Learning "
        "Repository for publishing the Metro Interstate 94 Traffic Volume dataset.",
        body_style
    ))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("TABLE OF CONTENTS", h1_style))
    toc_p_data = [
        ["1. Executive Summary & Project Overview", "4"],
        ["2. Introduction & Problem Statement", "4"],
        ["3. Scope and Objectives of the Analysis", "5"],
        ["4. Existing Systems vs. Distributed PySpark Architecture", "5"],
        ["5. Dataset Description & Technical Data Dictionary", "6"],
        ["6. Tools and Technologies Stack", "6"],
        ["7. Data Cleaning, Sanitization & Preprocessing Pipeline", "7"],
        ["    7.1 Data Quality Checks & Sensor Anomaly Resolution", "7"],
        ["    7.2 Code Implementation: Ingestion & Validation (Figure 1)", "7"],
        ["8. Exploratory Data Analysis with Spark SQL", "8"],
        ["    8.1 Code Implementation: Spark SQL Queries (Figure 2)", "8"],
        ["    8.2 Hourly Rush Hour Dynamics (Figure 3)", "8"],
        ["    8.3 Weekday vs. Weekend Commute Profiles (Figure 4)", "9"],
        ["    8.4 Seasonal & Monthly Trends (Figure 5)", "9"],
        ["    8.5 Meteorological & Weather Impact (Figure 6)", "10"],
        ["    8.6 Holiday Volume Suppression (Figure 7)", "10"],
        ["9. Machine Learning Modeling & PySpark MLlib Pipeline", "11"],
        ["    9.1 Code Implementation: Spark MLlib Pipeline (Figure 8)", "11"],
        ["    9.2 Chronological Split & Feature Engineering Rationale", "11"],
        ["    9.3 Model Performance Comparison (Table 3 & Figure 9)", "12"],
        ["10. Interactive Streamlit Web Dashboard Application", "13"],
        ["    10.1 Executive Overview & KPIs (Figure 10)", "13"],
        ["    10.2 Interactive Exploratory Trends (Figure 11)", "13"],
        ["    10.3 Real-Time Traffic Volume Predictor (Figure 12)", "14"],
        ["11. Results and Discussion", "14"],
        ["12. Limitations and Future Scope", "15"],
        ["13. Conclusion", "15"],
        ["14. References", "15"]
    ]
    t_toc_pdf = Table([[Paragraph(f"<b>{t}</b>" if not t.startswith("    ") else t, body_style),
                        Paragraph(p, ParagraphStyle('TR', parent=body_style, alignment=TA_RIGHT))]
                       for t, p in toc_p_data], colWidths=[4.8*inch, 0.8*inch])
    t_toc_pdf.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8),
        ('TOPPADDING', (0, 0), (-1, -1), 0.8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.2, colors.HexColor("#F1F5F9"))
    ]))
    elements.append(t_toc_pdf)

    elements.append(PageBreak())

    # PAGE 4: 1. EXECUTIVE SUMMARY & 2. INTRODUCTION
    elements.append(Paragraph("1. Executive Summary & Project Overview", h1_style))
    elements.append(Paragraph(
        "Rapid urbanization and exponential vehicular density have turned metropolitan traffic congestion into a major "
        "economic, ecological, and civil infrastructure challenge. Traditional single-machine analytics systems face significant "
        "bottlenecks when handling longitudinal, high-frequency sensor streams. This project develops an end-to-end distributed "
        "big data analytics pipeline and predictive machine learning system utilizing Apache PySpark 3.5.9 and Python 3.10.",
        body_style
    ))
    elements.append(Paragraph(
        "Using 48,204 hourly records spanning 2012 to 2018 from the Metro Interstate 94 corridor (Minneapolis to St. Paul, Minnesota), "
        "we perform distributed data quality audits, sensor fault sanitization (0 K temperature, 9831 mm extreme rainfall), "
        "high-speed aggregation using Spark SQL, feature engineering via Spark MLlib pipelines, and regression modeling. "
        "Our Random Forest Regressor achieves an R² score of 0.9120 (Mean Absolute Error of 382.8 vehicles/hour), radically outperforming "
        "the Linear Regression baseline (R² = 0.2000). The pipeline is coupled to an interactive Streamlit web application providing "
        "real-time congestion forecasting and decision-support dashboards.",
        body_style
    ))

    elements.append(Paragraph("2. Introduction & Problem Statement", h1_style))
    elements.append(Paragraph(
        "Modern intelligent transportation systems (ITS) depend heavily on loop detectors, environmental sensors, and telemetry gateways. "
        "Congestion on major interstate arterials leads to thousands of hours of commuter delays, elevated greenhouse gas emissions, "
        "and increased accident risks. Accurate traffic flow prediction allows municipal authorities to proactively optimize variable "
        "speed limits, dispatch emergency response units, and schedule infrastructure maintenance.",
        body_style
    ))
    elements.append(Paragraph(
        "However, raw traffic sensor feeds exhibit sensor dropouts, transmission duplicates, and extreme environmental fluctuations. "
        "Distributed computing frameworks like Apache Spark offer fault-tolerant resilient distributed datasets (RDDs), Catalyst query "
        "optimization, and native machine learning libraries (MLlib) to process these workloads reliably at scale.",
        body_style
    ))

    elements.append(PageBreak())

    # PAGE 5: 3. SCOPE & 4. EXISTING SYSTEMS
    elements.append(Paragraph("3. Scope and Objectives of the Analysis", h1_style))
    elements.append(Paragraph("The primary objectives of this study, mapped to Bloom's Taxonomy Level L6 (Create) and INT315 Course Outcomes (CO4, CO5, CO6), are:", body_style))
    elements.append(Paragraph("• <b>Distributed Data Engineering:</b> Design and implement a distributed data sanitization pipeline to identify and rectify physical sensor anomalies (0 K temperatures, telemetry gauge faults) and duplicate records.", bullet_style))
    elements.append(Paragraph("• <b>Distributed Exploratory Analytics:</b> Execute high-performance analytical queries using Spark SQL to uncover diurnal rush-hour dynamics, weekend commute shifts, meteorological correlations, and holiday volume suppression.", bullet_style))
    elements.append(Paragraph("• <b>Machine Learning at Scale:</b> Construct a leak-free PySpark MLlib Pipeline combining StringIndexer, OneHotEncoder, VectorAssembler, and Random Forest Regressor under a rigorous chronological 80/20 train-test split.", bullet_style))
    elements.append(Paragraph("• <b>Interactive Visualization & Delivery:</b> Deploy an interactive Streamlit web dashboard presenting executive KPIs, interactive charts, and a real-time traffic inference engine.", bullet_style))

    elements.append(Paragraph("4. Existing Systems vs. Distributed PySpark Architecture", h1_style))
    elements.append(Paragraph(
        "Traditional transportation management architectures rely predominantly on standalone relational databases (e.g., MySQL, PostgreSQL) "
        "and single-threaded analytics libraries (standard Pandas, Scikit-Learn). While adequate for retrospective batch reports on small samples, "
        "existing systems suffer from critical limitations:",
        body_style
    ))
    elements.append(Paragraph("• <b>Memory Bottlenecks:</b> Single-machine memory bounds cause out-of-memory (OOM) failures when scaling to millions of streaming detector pings.", bullet_style))
    elements.append(Paragraph("• <b>Scalability Limits:</b> Single-threaded execution cannot exploit multi-core cluster worker nodes or parallel partition executors.", bullet_style))
    elements.append(Paragraph("• <b>Pipeline Fragmentation:</b> Rigid database schemas make ad-hoc feature extraction and pipeline serialization computationally expensive.", bullet_style))
    elements.append(Paragraph(
        "The proposed PySpark architecture resolves these barriers by distributing partitioned DataFrames across worker nodes, "
        "utilizing lazy evaluation and Catalyst query optimization, and storing intermediate artifacts in columnar Snappy-compressed "
        "Parquet formats, ensuring high throughput and fault tolerance.",
        body_style
    ))

    elements.append(PageBreak())

    # PAGE 6: 5. DATASET & 6. TOOLS
    elements.append(Paragraph("5. Dataset Description & Technical Data Dictionary", h1_style))
    elements.append(Paragraph(
        "The dataset used is the Metro Interstate Traffic Volume dataset from the UCI Machine Learning Repository, "
        "collected by the Minnesota Department of Transportation (MnDOT). It contains 48,204 hourly observations of westbound "
        "traffic on Interstate 94 between Minneapolis and St. Paul, Minnesota, spanning October 2012 to September 2018.",
        body_style
    ))

    dict_rows_pdf = [
        ["Field Name", "Data Type", "Range / Distinct", "Description & Physical Unit"],
        ["holiday", "String", "12 categories", "US national holiday name or 'None'"],
        ["temp", "Double", "0.0 to 310.07 K", "Ambient air temperature in Kelvin (0 K anomalous)"],
        ["rain_1h", "Double", "0.0 to 9831.3 mm", "Rainfall depth accumulated in the prior hour"],
        ["snow_1h", "Double", "0.0 to 0.51 mm", "Snowfall depth accumulated in the prior hour"],
        ["clouds_all", "Integer", "0% to 100%", "Percentage of cloud coverage from sky cameras"],
        ["weather_main", "String", "11 categories", "Primary meteorological category (Clear, Rain, Snow, etc.)"],
        ["weather_description", "String", "38 categories", "Granular meteorological description"],
        ["date_time", "Timestamp", "2012-10-02 to 2018-09-30", "Hourly observation timestamp (UTC)"],
        ["traffic_volume", "Integer", "0 to 7,280 vph", "Westbound hourly vehicle count (Target variable)"]
    ]
    t_dict_pdf = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else c, body_style) for c in row] for i, row in enumerate(dict_rows_pdf)],
                       colWidths=[1.3*inch, 0.8*inch, 1.3*inch, 2.2*inch])
    t_dict_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t_dict_pdf)
    elements.append(Paragraph("Table 1: Metro Interstate Traffic Volume Dataset Technical Data Dictionary", caption_style))

    elements.append(Paragraph("6. Tools and Technologies Stack", h1_style))
    tools_rows_pdf = [
        ["Technology / Library", "Version", "Functional Role in Project"],
        ["Apache Spark / PySpark", "3.5.9", "Distributed in-memory big data processing engine & DataFrame API"],
        ["Spark SQL", "3.5.9", "Optimized distributed relational queries with Catalyst optimizer"],
        ["Spark MLlib", "3.5.9", "Scalable machine learning pipelines, feature transformation & estimators"],
        ["Python", "3.10.12", "Core programming runtime and scripting environment"],
        ["Streamlit", "1.30+", "Web application framework for real-time dashboarding & inference UI"],
        ["Matplotlib / Seaborn", "3.8+", "Publication-quality exploratory visualizations & analytical charts"],
        ["Pandas & NumPy", "2.1+", "Local matrix conversion and auxiliary tabular data manipulation"],
        ["Apache Parquet / Snappy", "1.0", "Columnar, high-compression persistent storage format"]
    ]
    t_tools_pdf = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else c, body_style) for c in row] for i, row in enumerate(tools_rows_pdf)],
                        colWidths=[1.7*inch, 0.8*inch, 3.1*inch])
    t_tools_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t_tools_pdf)
    elements.append(Paragraph("Table 2: Software Ecosystem and Technical Stack", caption_style))

    elements.append(PageBreak())

    # PAGE 7: 7. DATA CLEANING & CODE 1
    elements.append(Paragraph("7. Data Cleaning, Sanitization & Preprocessing Pipeline", h1_style))
    elements.append(Paragraph("7.1 Data Quality Checks & Sensor Anomaly Resolution", h2_style))
    elements.append(Paragraph(
        "Prior to model training, a rigorous data quality audit was conducted using PySpark functions. "
        "The investigation revealed three critical data quality phenomena:", body_style
    ))
    elements.append(Paragraph("• <b>Deduplication:</b> Exactly 17 duplicate records had identical values across all 9 columns. These represented telemetry replay artifacts and were pruned using dropDuplicates(). Records sharing identical timestamps but exhibiting distinct meteorological descriptions were preserved as valid multi-condition events.", bullet_style))
    elements.append(Paragraph("• <b>Temperature Zero Anomaly:</b> Exactly 10 records recorded temp = 0.0 K (-273.15°C), representing telemetry communication loss. These were set to NULL and later imputed via median value substitution in the MLlib pipeline.", bullet_style))
    elements.append(Paragraph("• <b>Extreme Precipitation Fault:</b> On 2016-07-11 17:00:00, rain_1h was recorded as 9831.3 mm (nearly 10 meters of rain in 60 minutes). This physically unviable value was converted to NULL to prevent outlier distortion.", bullet_style))
    elements.append(Paragraph("• <b>Temporal Feature Engineering:</b> Extracted hour (0-23), day_of_week (1-7), month (1-12), and a binary is_weekend indicator from date_time.", bullet_style))
    elements.append(Paragraph("The cleaned dataset contains 48,187 high-fidelity records and was saved into columnar Parquet format.", body_style))

    elements.append(Paragraph("7.2 Code Implementation: PySpark Ingestion & Validation", h2_style))
    elements.append(Paragraph(
        "Figure 1 illustrates the actual code executed in the Jupyter Notebook environment, highlighting the initialization "
        "of the SparkSession with 4 shuffle partitions and 4 GB driver memory, schema inference, and column-wise null checking.",
        body_style
    ))
    if os.path.exists(IMG_CODE1):
        img_c1 = Image(IMG_CODE1, width=5.6*inch, height=2.65*inch)
        img_c1.hAlign = 'CENTER'
        elements.append(img_c1)
        elements.append(Paragraph("Figure 1: PySpark Environment Setup, SparkSession Ingestion, and Missing Value Analysis (code1.png)", caption_style))

    elements.append(PageBreak())

    # PAGE 8: 8.1 & 8.2 (CODE 2 & FIG 3)
    elements.append(Paragraph("8. Exploratory Data Analysis with Spark SQL", h1_style))
    elements.append(Paragraph("8.1 Code Implementation: Spark SQL Analytical Queries", h2_style))
    elements.append(Paragraph(
        "PySpark's Catalyst optimizer was leveraged by registering the cleaned DataFrame as a temporary SQL view ('traffic'). "
        "Complex aggregation queries were executed to compute hourly volume distributions, weekday versus weekend variances, "
        "monthly seasonal trajectories, and meteorological cross-tabulations.",
        body_style
    ))
    if os.path.exists(IMG_CODE2):
        img_c2 = Image(IMG_CODE2, width=5.6*inch, height=2.65*inch)
        img_c2.hAlign = 'CENTER'
        elements.append(img_c2)
        elements.append(Paragraph("Figure 2: Spark SQL Analytical Queries for Distributed Traffic Aggregations (code 2.png)", caption_style))

    elements.append(Paragraph("8.2 Hourly Rush Hour Dynamics", h2_style))
    elements.append(Paragraph(
        "Weekday traffic exhibits a pronounced bimodal commute pattern. A sharp morning rush hour occurs between 07:00 and 08:00 (~4,750 vph), "
        "followed by an even heavier evening rush hour between 16:00 and 17:00 peaking at ~4,850 vph. Off-peak nighttime flow drops below 700 vph at 03:00.",
        body_style
    ))
    if os.path.exists(FIG_HOURLY):
        img_h = Image(FIG_HOURLY, width=5.0*inch, height=2.3*inch)
        img_h.hAlign = 'CENTER'
        elements.append(img_h)
        elements.append(Paragraph("Figure 3: Mean Hourly Traffic Volume Profile with ±0.5 Standard Deviation Band", caption_style))

    elements.append(PageBreak())

    # PAGE 9: 8.3 & 8.4 (FIG 4 & FIG 5)
    elements.append(Paragraph("8.3 Weekday vs. Weekend Commute Profiles", h2_style))
    elements.append(Paragraph(
        "Figure 4 reveals a fundamental behavioral contrast. Weekday traffic is driven by work commutes with two distinct peaks. "
        "In contrast, weekend traffic displays a unimodal leisure plateau: traffic builds gradually through the late morning and plateaus "
        "between 12:00 and 17:00 at ~4,300 vph without sharp morning or evening spikes.",
        body_style
    ))
    if os.path.exists(FIG_WEEKDAY):
        img_w = Image(FIG_WEEKDAY, width=5.0*inch, height=2.45*inch)
        img_w.hAlign = 'CENTER'
        elements.append(img_w)
        elements.append(Paragraph("Figure 4: Commute Dynamics: Weekday (Bimodal) vs. Weekend (Unimodal) Hourly Curves", caption_style))

    elements.append(Paragraph("8.4 Seasonal & Monthly Trends", h2_style))
    elements.append(Paragraph(
        "Monthly volume trends reflect Minnesota's continental climate. Peak vehicular throughput occurs in summer and early autumn "
        "(June to October, averaging ~3,500 vph), driven by favorable weather, tourism, and road construction detours. Severe winter conditions "
        "in December and January depress traffic volumes to ~3,000 vph.",
        body_style
    ))
    if os.path.exists(FIG_MONTHLY):
        img_m = Image(FIG_MONTHLY, width=5.0*inch, height=2.45*inch)
        img_m.hAlign = 'CENTER'
        elements.append(img_m)
        elements.append(Paragraph("Figure 5: Monthly Traffic Volume Seasonal Trajectory", caption_style))

    elements.append(PageBreak())

    # PAGE 10: 8.5 & 8.6 (FIG 6 & FIG 7)
    elements.append(Paragraph("8.5 Meteorological & Weather Impact", h2_style))
    elements.append(Paragraph(
        "While adverse weather conditions such as fog, thunderstorms, and heavy snow reduce highway speeds and vehicular counts, "
        "baseline volume during clear and overcast skies remains high because commuters must travel regardless of ambient clouds.",
        body_style
    ))
    if os.path.exists(FIG_WEATHER):
        img_we = Image(FIG_WEATHER, width=5.0*inch, height=2.45*inch)
        img_we.hAlign = 'CENTER'
        elements.append(img_we)
        elements.append(Paragraph("Figure 6: Mean Traffic Volume Across Primary Meteorological Categories", caption_style))

    elements.append(Paragraph("8.6 Holiday Volume Suppression", h2_style))
    elements.append(Paragraph(
        "US federal holidays cause an extraordinary 73.5% drop in average hourly volume, falling from 3,263 vph on regular days to "
        "just 865 vph on holidays, emphasizing the necessity of including holiday indicator flags in predictive models.",
        body_style
    ))
    if os.path.exists(FIG_HOLIDAY):
        img_ho = Image(FIG_HOLIDAY, width=4.6*inch, height=2.3*inch)
        img_ho.hAlign = 'CENTER'
        elements.append(img_ho)
        elements.append(Paragraph("Figure 7: Holiday Volume Suppression vs. Non-Holiday Baseline", caption_style))

    elements.append(PageBreak())

    # PAGE 11: 9. ML & CODE 3
    elements.append(Paragraph("9. Machine Learning Modeling & PySpark MLlib Pipeline", h1_style))
    elements.append(Paragraph("9.1 Code Implementation: Spark MLlib Pipeline Architecture", h2_style))
    elements.append(Paragraph(
        "To ensure production scalability and zero data leakage, all preprocessing transformations were encapsulated within a unified "
        "PySpark Pipeline. The pipeline stages include: Imputer (median strategy for temperature and rain), StringIndexer for weather and holiday, "
        "OneHotEncoder for categorical features, VectorAssembler for dense feature vector composition, and regression estimators.",
        body_style
    ))
    if os.path.exists(IMG_CODE3):
        img_c3 = Image(IMG_CODE3, width=5.6*inch, height=2.65*inch)
        img_c3.hAlign = 'CENTER'
        elements.append(img_c3)
        elements.append(Paragraph("Figure 8: Spark MLlib Feature Engineering Pipeline, Chronological Split, and Regression Training (code 3 (2).png)", caption_style))

    elements.append(Paragraph("9.2 Chronological Split & Feature Engineering Rationale", h2_style))
    elements.append(Paragraph(
        "Standard random cross-validation leaks temporal autocorrelation in time-series data. We implemented an exact chronological 80/20 split: "
        "the first 80% of data (October 2012 to November 2017; 38,549 records) was allocated for training, while the final 20% (November 2017 to "
        "September 2018; 9,638 records) was held out strictly for out-of-time evaluation.",
        body_style
    ))

    elements.append(PageBreak())

    # PAGE 12: 9.3 MODEL PERFORMANCE & FIG 9
    elements.append(Paragraph("9.3 Model Performance Comparison", h2_style))
    elements.append(Paragraph(
        "We compared a baseline Linear Regression model against a distributed Random Forest Regressor (numTrees=60, maxDepth=12, seed=42). "
        "Evaluations were performed using PySpark's RegressionEvaluator across R², Mean Absolute Error (MAE), and Root Mean Squared Error (RMSE).",
        body_style
    ))

    perf_rows_pdf = [
        ["Model Architecture", "R² Score", "MAE (vph)", "RMSE (vph)", "Performance Assessment"],
        ["Linear Regression (Baseline)", "0.2000", "1,540.8", "1,759.5", "Poor; fails to capture diurnal rush peaks"],
        ["Random Forest Regressor", "0.9120", "382.8", "583.5", "Superior; explains 91.2% of variance"]
    ]
    t_perf_pdf = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else c, body_style) for c in row] for i, row in enumerate(perf_rows_pdf)],
                       colWidths=[1.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 1.2*inch])
    t_perf_pdf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_perf_pdf)
    elements.append(Paragraph("Table 3: Out-of-Time Model Performance Metrics on 20% Held-Out Test Set", caption_style))

    if os.path.exists(FIG_ACT_PRED):
        img_ap = Image(FIG_ACT_PRED, width=5.2*inch, height=2.6*inch)
        img_ap.hAlign = 'CENTER'
        elements.append(img_ap)
        elements.append(Paragraph("Figure 9: Actual vs. Predicted Traffic Volume on Held-Out Test Set (Random Forest Regressor)", caption_style))

    elements.append(PageBreak())

    # PAGE 13: 10. STREAMLIT OVERVIEW & EDA (IMG 1 & IMG 2)
    elements.append(Paragraph("10. Interactive Streamlit Web Dashboard Application", h1_style))
    elements.append(Paragraph(
        "To deliver actionable insights to transportation planners and operators, a web dashboard was built using Streamlit. "
        "The application provides a seamless 4-tier navigation structure: Executive Overview, Exploratory Data Analysis, Model Performance, "
        "and Real-Time Traffic Prediction.",
        body_style
    ))

    elements.append(Paragraph("10.1 Executive Overview & Real-Time KPIs", h2_style))
    elements.append(Paragraph(
        "The Overview page (Figure 10) displays key system KPIs: Total Cleaned Records (48,187), Average Highway Traffic (3,260 vph), "
        "Peak Recorded Volume (6,190 vph), and ML Model Accuracy (R² = 0.9120), alongside a visual overview of the end-to-end data pipeline.",
        body_style
    ))
    if os.path.exists(IMG_OVERVIEW):
        img_ov = Image(IMG_OVERVIEW, width=5.6*inch, height=2.5*inch)
        img_ov.hAlign = 'CENTER'
        elements.append(img_ov)
        elements.append(Paragraph("Figure 10: Streamlit Dashboard - Executive Overview and Key Performance Indicators (img1 overview.png)", caption_style))

    elements.append(Paragraph("10.2 Interactive Exploratory Trends", h2_style))
    elements.append(Paragraph(
        "The EDA module (Figure 11) allows users to explore interactive diurnal traffic patterns across tabs (Hourly Trends, Monthly Trends, "
        "Weather Impact, and Holidays), dynamically rendering weekday versus weekend commute profiles.",
        body_style
    ))
    if os.path.exists(IMG_EDA):
        img_ed = Image(IMG_EDA, width=5.6*inch, height=2.5*inch)
        img_ed.hAlign = 'CENTER'
        elements.append(img_ed)
        elements.append(Paragraph("Figure 11: Streamlit Dashboard - Interactive Exploratory Data Analysis Interface (img2 EDA.png)", caption_style))

    elements.append(PageBreak())

    # PAGE 14: 10.3 PREDICTOR (IMG 3) & 11. RESULTS
    elements.append(Paragraph("10.3 Real-Time Traffic Volume Predictor", h2_style))
    elements.append(Paragraph(
        "The Predictor interface (Figure 12) empowers traffic managers to simulate conditions by adjusting Hour of Day, Day of Week, "
        "Month, Weather Category, Ambient Temperature (°C), Cloud Cover (%), Rainfall (mm), and Holiday Status. The underlying PySpark "
        "model pipeline instantly generates an estimated hourly volume (e.g., 5,608 vph) accompanied by an operational congestion tier classification.",
        body_style
    ))
    if os.path.exists(IMG_PREDICT):
        img_pr = Image(IMG_PREDICT, width=5.6*inch, height=2.5*inch)
        img_pr.hAlign = 'CENTER'
        elements.append(img_pr)
        elements.append(Paragraph("Figure 12: Streamlit Dashboard - Real-Time Traffic Volume Predictor & Congestion Classifier (img3 prediction .png)", caption_style))

    elements.append(Paragraph("11. Results and Discussion", h1_style))
    elements.append(Paragraph(
        "The analytical findings demonstrate that diurnal time-of-day features dominate traffic volume variation. The Random Forest model "
        "captures subtle non-linear interactions between hour of day and weekday/weekend indicators that linear regression completely misses. "
        "Furthermore, federal holidays induce substantial traffic drops (-73.5%), while adverse weather causes moderate slowdowns. "
        "The PySpark distributed architecture achieved linear scaling during data cleaning and sub-minute ML training times.",
        body_style
    ))

    elements.append(PageBreak())

    # PAGE 15: 12. LIMITATIONS, 13. CONCLUSION, 14. REFERENCES
    elements.append(Paragraph("12. Limitations and Future Scope", h1_style))
    elements.append(Paragraph("• <b>Geographic Specificity:</b> The current model is calibrated specifically to Interstate 94 westbound between Minneapolis and St. Paul; cross-corridor generalization requires multi-station sensor calibration.", bullet_style))
    elements.append(Paragraph("• <b>Forecasting Horizon:</b> Current predictions utilize contemporaneous weather observations. Integrating numerical weather prediction (NWP) API feeds would enable 24-48 hour proactive traffic forecasting.", bullet_style))
    elements.append(Paragraph("• <b>Streaming Integration:</b> Future architectures can ingest live telemetry via Apache Kafka and process sliding windows using Spark Structured Streaming.", bullet_style))

    elements.append(Paragraph("13. Conclusion", h1_style))
    elements.append(Paragraph(
        "This project successfully engineered and deployed a distributed big data analytics and machine learning pipeline for highway "
        "traffic congestion forecasting using Apache PySpark and Streamlit. By effectively resolving raw sensor anomalies, applying Spark SQL "
        "for scalable aggregations, and fitting a high-accuracy Random Forest MLlib pipeline (R² = 0.9120), the project validates the immense "
        "power of distributed computing for modern intelligent transportation systems.",
        body_style
    ))

    elements.append(Paragraph("14. References", h1_style))
    refs = [
        "1. UCI Machine Learning Repository: Metro Interstate Traffic Volume Dataset (MnDOT, 2018).",
        "2. Zaharia, M. et al. 'Apache Spark: A Unified Engine for Big Data Processing.' Communications of the ACM, 2016.",
        "3. Meng, X. et al. 'MLlib: Machine Learning in Apache Spark.' Journal of Machine Learning Research (JMLR), 2016.",
        "4. Streamlit Documentation: Fast, Interactive Web Applications for Machine Learning (https://docs.streamlit.io).",
        "5. Hunter, J. D. 'Matplotlib: A 2D Graphics Environment.' Computing in Science & Engineering, 2007.",
        "6. Lovely Professional University: INT315 Cluster Computing Laboratory Guidelines & Academic Curriculum, 2026."
    ]
    for r in refs:
        elements.append(Paragraph(r, bullet_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF report generated at: {OUTPUT_PDF_PATH}")


if __name__ == "__main__":
    print("Generating DOCX Report...")
    generate_docx()
    print("Generating PDF Report...")
    generate_pdf()
    print("All reports generated successfully!")
