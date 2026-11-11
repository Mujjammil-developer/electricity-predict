"""
Report Generator Module.
Generates comprehensive PDF reports using ReportLab, and exports
prediction data and analyzed datasets to CSV format.
"""

import os
import io
import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_predictions_csv(future_records):
    """Converts 24-hour predictions list to downloadable CSV bytes."""
    df = pd.DataFrame(future_records)
    cols = ['step', 'datetime', 'predicted_kwh', 'status', 'estimated_cost_inr']
    existing_cols = [c for c in cols if c in df.columns]
    output = io.StringIO()
    df[existing_cols].to_csv(output, index=False)
    return output.getvalue().encode('utf-8')

def generate_analyzed_data_csv(df):
    """Exports processed and feature-enriched dataset to CSV bytes."""
    cols = ['datetime', 'consumption_kwh', 'hour', 'day_name', 'month_name', 'is_weekend']
    existing_cols = [c for c in cols if c in df.columns]
    output = io.StringIO()
    df[existing_cols].to_csv(output, index=False)
    return output.getvalue().encode('utf-8')

def generate_pdf_report(overview_metrics, model_metrics, future_records, recommendations, bill_info, filename=None):
    """
    Generates a formal, professional PDF Project Report.
    Returns bytes buffer or writes to filename.
    """
    buffer = io.BytesIO() if filename is None else filename
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom palette matching Dark Navy & Electric Green theme
    navy_color = colors.HexColor("#0f172a")
    green_color = colors.HexColor("#10b981")
    slate_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#475569")
    light_bg = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#cbd5e1")
    
    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy_color,
        alignment=0,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=green_color,
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=navy_color,
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=slate_dark
    )
    body_bold = ParagraphStyle(
        'ReportBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=navy_color
    )
    small_muted = ParagraphStyle(
        'SmallMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=text_muted
    )
    
    story = []
    
    # Header Banner
    story.append(Paragraph("Electricity Consumption Prediction & Smart Energy Analysis System", title_style))
    story.append(Paragraph("B.Tech Artificial Intelligence and Data Science | Project Evaluation Report", subtitle_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | Machine Learning Framework: Random Forest Regressor", small_muted))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=green_color, spaceAfter=12))
    
    # 1. Executive Summary & KPIs
    story.append(Paragraph("1. Executive Summary & Consumption Statistics", section_heading))
    summary_text = (
        f"This report presents an empirical analysis of electricity consumption patterns. "
        f"The system processed <b>{overview_metrics.get('total_records', 'N/A'):,}</b> hourly recordings "
        f"across <b>{overview_metrics.get('total_days', 'N/A')}</b> operational days, with a cumulative power demand of "
        f"<b>{overview_metrics.get('total_consumption_kwh', 'N/A'):,} kWh</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))
    
    kpi_data = [
        [
            Paragraph("Total Energy Consumed", body_bold),
            Paragraph(f"{overview_metrics.get('total_consumption_kwh', 0):,} kWh", body_style),
            Paragraph("Average Daily Usage", body_bold),
            Paragraph(f"{overview_metrics.get('avg_daily_consumption_kwh', 0)} kWh/day", body_style)
        ],
        [
            Paragraph("Peak Load Hour", body_bold),
            Paragraph(f"{overview_metrics.get('peak_hour_formatted', 'N/A')}", body_style),
            Paragraph("Off-Peak Trough Hour", body_bold),
            Paragraph(f"{overview_metrics.get('trough_hour_formatted', 'N/A')}", body_style)
        ],
        [
            Paragraph("Highest Single Surge", body_bold),
            Paragraph(f"{overview_metrics.get('highest_consumption_kwh', 0)} kWh", body_style),
            Paragraph("Standard Deviation", body_bold),
            Paragraph(f"{overview_metrics.get('std_dev_kwh', 0)} kWh", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 140, 130, 140])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))
    
    # 2. Machine Learning Model Performance
    story.append(Paragraph("2. Machine Learning Model Performance (Random Forest Regressor)", section_heading))
    ml_intro = (
        "The predictive engine leverages an ensemble Random Forest Regressor trained on chronological "
        "time-series splits to prevent look-ahead bias and data leakage. Core lag features (lag_1, lag_24, lag_48, lag_168) "
        "and cyclical temporal encodings were utilized."
    )
    story.append(Paragraph(ml_intro, body_style))
    story.append(Spacer(1, 6))
    
    mae = model_metrics.get('mae', 'N/A') if model_metrics else 'N/A'
    rmse = model_metrics.get('rmse', 'N/A') if model_metrics else 'N/A'
    r2 = model_metrics.get('r2', 'N/A') if model_metrics else 'N/A'
    mape = model_metrics.get('mape', 'N/A') if model_metrics else 'N/A'
    
    ml_data = [
        [Paragraph("Metric", body_bold), Paragraph("Observed Value", body_bold), Paragraph("Interpretation & Significance", body_bold)],
        [
            Paragraph("R² Score (Determination)", body_bold),
            Paragraph(f"<b>{r2}</b>", body_style),
            Paragraph("Explains the proportion of variance in power load captured by the ensemble model.", small_muted)
        ],
        [
            Paragraph("Mean Absolute Error (MAE)", body_bold),
            Paragraph(f"<b>{mae} kWh</b>", body_style),
            Paragraph("Average absolute error magnitude per forecast hour across the testing dataset.", small_muted)
        ],
        [
            Paragraph("Root Mean Squared Error (RMSE)", body_bold),
            Paragraph(f"<b>{rmse} kWh</b>", body_style),
            Paragraph("Penalizes large outlier forecast errors; vital for grid peak planning.", small_muted)
        ],
        [
            Paragraph("Mean Abs Percentage Error (MAPE)", body_bold),
            Paragraph(f"<b>{mape}%</b>", body_style),
            Paragraph("Relative accuracy percentage indicating excellent fit for non-linear load curves.", small_muted)
        ]
    ]
    ml_table = Table(ml_data, colWidths=[160, 110, 270])
    ml_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ml_table)
    story.append(Spacer(1, 10))
    
    # 3. Next 24-Hour Predictive Forecast Table
    story.append(Paragraph("3. Next 24-Hour Autonomous Multi-Step Forecast", section_heading))
    forecast_text = (
        f"Forecast generated via autoregressive recursive forecasting. Total anticipated energy requirement: "
        f"<b>{future_records.get('total_predicted_next_day_kwh', 'N/A')} kWh</b> | "
        f"Estimated energy expense: <b>₹{future_records.get('estimated_total_cost_inr', 'N/A'):,}</b>."
    )
    story.append(Paragraph(forecast_text, body_style))
    story.append(Spacer(1, 6))
    
    # Sample every 2-3 hours for clean table display in PDF
    recs = future_records.get('forecast_records', [])
    sample_recs = recs[::2] if len(recs) > 12 else recs
    
    forecast_rows = [
        [
            Paragraph("Hour / Time", body_bold),
            Paragraph("Predicted Load (kWh)", body_bold),
            Paragraph("Grid Status", body_bold),
            Paragraph("Estimated Cost (₹)", body_bold)
        ]
    ]
    for r in sample_recs:
        forecast_rows.append([
            Paragraph(f"{r.get('time', 'N/A')} ({r.get('hour', 0):02d}:00)", body_style),
            Paragraph(f"{r.get('predicted_kwh', 0):.2f} kWh", body_style),
            Paragraph(f"{r.get('status', 'Normal')}", body_style),
            Paragraph(f"₹{r.get('estimated_cost_inr', 0):.2f}", body_style)
        ])
        
    fc_table = Table(forecast_rows, colWidths=[140, 130, 130, 140])
    fc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(fc_table)
    story.append(Spacer(1, 10))
    
    # 4. Smart Energy Recommendations
    story.append(Paragraph("4. Smart Energy Recommendations & Load Shifting Strategy", section_heading))
    recs_list = recommendations.get('recommendations', []) if recommendations else []
    for idx, rec in enumerate(recs_list[:3], 1):
        story.append(Paragraph(f"<b>4.{idx} [{rec.get('badge', 'Advisory')}] {rec.get('title', '')}</b>", body_bold))
        story.append(Paragraph(rec.get('description', ''), body_style))
        story.append(Paragraph(f"<b>Recommended Action:</b> {rec.get('action', '')}", small_muted))
        story.append(Paragraph(f"<b>Quantified Impact:</b> {rec.get('potential_impact', '')}", small_muted))
        story.append(Spacer(1, 4))
        
    # 5. Tariff & Billing Estimates
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Electricity Bill Estimation & Cost Breakdown", section_heading))
    b_data = [
        [
            Paragraph("Tariff Basis", body_bold),
            Paragraph(f"₹{bill_info.get('flat_tariff_rate', 7.50)} per kWh", body_style),
            Paragraph("Estimated Daily Cost", body_bold),
            Paragraph(f"₹{bill_info.get('flat_daily_cost', 0):,.2f}", body_style)
        ],
        [
            Paragraph("Estimated Monthly Bill", body_bold),
            Paragraph(f"₹{bill_info.get('flat_monthly_cost', 0):,.2f}", body_style),
            Paragraph("Predicted 24h Bill", body_bold),
            Paragraph(f"₹{bill_info.get('predicted_daily_cost', 0):,.2f}", body_style)
        ]
    ]
    b_table = Table(b_data, colWidths=[130, 140, 130, 140])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(b_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(bill_info.get('disclaimer', ''), small_muted))
    
    # Build Document
    doc.build(story)
    
    if filename is None:
        buffer.seek(0)
        return buffer.getvalue()
    return None
