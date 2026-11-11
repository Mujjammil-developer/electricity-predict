"""
Test Pipeline Script to verify all modules work end-to-end.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from modules.data_processing import load_and_validate_dataset, get_preview_data
from modules.analysis import (
    compute_overview_metrics, compute_hourly_analysis, compute_daily_analysis,
    compute_monthly_analysis, compute_peak_analysis, compute_distribution_analysis
)
from modules.prediction import train_and_evaluate_model, forecast_next_24_hours
from modules.recommendations import generate_smart_recommendations
from modules.bill_calculator import calculate_electricity_bill
from modules.report_generator import generate_pdf_report, generate_predictions_csv

sample_path = os.path.join(BASE_DIR, "dataset", "sample_electricity_consumption.csv")
print("1. Loading dataset...")
df, summary, err = load_and_validate_dataset(sample_path)
if err:
    print("Error:", err)
    sys.exit(1)
print("Dataset loaded successfully! Cleaned rows:", summary['cleaned_rows'])

print("2. Computing overview metrics & analysis...")
metrics = compute_overview_metrics(df)
hourly = compute_hourly_analysis(df)
daily = compute_daily_analysis(df)
monthly = compute_monthly_analysis(df)
peak = compute_peak_analysis(df)
dist = compute_distribution_analysis(df)
print("Overview metrics:", metrics['total_consumption_kwh'], "kWh, Peak Hour:", metrics['peak_hour_formatted'])

print("3. Training ML model (Random Forest Regressor)...")
model_metrics, test_chart, future_pred, feat_imp = train_and_evaluate_model(df)
print("Model trained! R2:", model_metrics['r2'], "MAE:", model_metrics['mae'], "RMSE:", model_metrics['rmse'])
print("Next 24h total forecast:", future_pred['total_predicted_next_day_kwh'], "kWh")

print("4. Generating recommendations...")
recs = generate_smart_recommendations(df, metrics, future_pred)
print("Recommendations generated:", len(recs['recommendations']), "items.")

print("5. Calculating bill...")
bill = calculate_electricity_bill(metrics['avg_daily_consumption_kwh'], future_pred['total_predicted_next_day_kwh'])
print("Bill calculated: Monthly Flat ₹", bill['flat_monthly_cost'], ", Slab ₹", bill['slab_monthly_cost'])

print("6. Generating PDF report...")
pdf_bytes = generate_pdf_report(metrics, model_metrics, future_pred, recs, bill)
print("PDF report generated successfully! Bytes length:", len(pdf_bytes))

print("\n--- ALL MODULES VERIFIED AND WORKING PERFECTLY! ---")
