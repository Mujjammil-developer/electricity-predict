"""
Electricity Consumption Prediction and Smart Energy Analysis System
Full-Stack Flask Application
"""

import os
import io
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session,
    send_file, jsonify, Response
)
from werkzeug.utils import secure_filename

from modules.data_processing import load_and_validate_dataset, get_preview_data
from modules.analysis import (
    compute_overview_metrics, compute_hourly_analysis, compute_daily_analysis,
    compute_monthly_analysis, compute_peak_analysis, compute_distribution_analysis
)
from modules.prediction import (
    train_and_evaluate_model, forecast_next_24_hours, get_cached_prediction_results
)
from modules.recommendations import generate_smart_recommendations
from modules.bill_calculator import calculate_electricity_bill
from modules.report_generator import (
    generate_pdf_report, generate_predictions_csv, generate_analyzed_data_csv
)

app = Flask(__name__)
app.secret_key = "ecopredict-smart-energy-secret-key-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATASET_PATH = os.path.join(BASE_DIR, "dataset", "sample_electricity_consumption.csv")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload

# In-memory application state cache
APP_STATE = {
    'current_filepath': SAMPLE_DATASET_PATH,
    'is_simulated': True,
    'df': None,
    'summary': None,
    'overview': None,
    'hourly': None,
    'daily': None,
    'monthly': None,
    'peak': None,
    'distribution': None,
    'model_metrics': None,
    'test_chart': None,
    'future_pred': None,
    'feat_imp': None,
    'tariff_rate': 7.50
}

def initialize_or_refresh_state(force_reload=False):
    """Loads dataset, trains model, and caches all analytical components."""
    if APP_STATE['df'] is not None and not force_reload:
        return True, None
        
    filepath = APP_STATE['current_filepath']
    if not os.path.exists(filepath):
        from generate_sample_data import generate_sample_dataset
        generate_sample_dataset(SAMPLE_DATASET_PATH)
        filepath = SAMPLE_DATASET_PATH
        APP_STATE['current_filepath'] = SAMPLE_DATASET_PATH
        APP_STATE['is_simulated'] = True

    df, summary, err = load_and_validate_dataset(filepath)
    if err:
        return False, err
        
    try:
        # 1. Statistical Analysis
        overview = compute_overview_metrics(df)
        hourly = compute_hourly_analysis(df)
        daily = compute_daily_analysis(df)
        monthly = compute_monthly_analysis(df)
        peak = compute_peak_analysis(df)
        distribution = compute_distribution_analysis(df)
        
        # 2. Machine Learning Model Training & Evaluation
        model_metrics, test_chart, future_pred, feat_imp = train_and_evaluate_model(
            df, n_estimators=100, max_depth=14
        )
        
        # Store in state
        APP_STATE['df'] = df
        APP_STATE['summary'] = summary
        APP_STATE['overview'] = overview
        APP_STATE['hourly'] = hourly
        APP_STATE['daily'] = daily
        APP_STATE['monthly'] = monthly
        APP_STATE['peak'] = peak
        APP_STATE['distribution'] = distribution
        APP_STATE['model_metrics'] = model_metrics
        APP_STATE['test_chart'] = test_chart
        APP_STATE['future_pred'] = future_pred
        APP_STATE['feat_imp'] = feat_imp
        
        return True, None
    except Exception as e:
        return False, f"Analytics processing error: {str(e)}"

# Ensure state is initialized at startup
initialize_or_refresh_state()

@app.before_request
def ensure_session_vars():
    session['is_simulated'] = APP_STATE.get('is_simulated', True)
    session['total_rows'] = f"{APP_STATE['overview']['total_records']:,}" if APP_STATE.get('overview') else "8,784"
    if 'tariff_rate' not in session:
        session['tariff_rate'] = APP_STATE.get('tariff_rate', 7.50)

# ==============================================================================
# ROUTE 1: Main Dashboard
# ==============================================================================
@app.route('/')
@app.route('/dashboard')
def dashboard():
    success, err = initialize_or_refresh_state()
    if not success:
        flash(f"Error loading system state: {err}", "danger")
        
    tariff = session.get('tariff_rate', 7.50)
    bill = calculate_electricity_bill(
        APP_STATE['overview']['avg_daily_consumption_kwh'],
        APP_STATE['future_pred']['total_predicted_next_day_kwh'],
        flat_tariff_rate=tariff
    )
    recommendations = generate_smart_recommendations(
        APP_STATE['df'],
        APP_STATE['overview'],
        APP_STATE['future_pred'],
        tariff_per_kwh=tariff
    )
    
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        is_simulated=APP_STATE['is_simulated'],
        overview=APP_STATE['overview'],
        daily=APP_STATE['daily'],
        monthly=APP_STATE['monthly'],
        hourly=APP_STATE['hourly'],
        dist=APP_STATE['distribution'],
        test_chart=APP_STATE['test_chart'],
        model_metrics=APP_STATE['model_metrics'],
        future_pred=APP_STATE['future_pred'],
        bill=bill,
        recommendations=recommendations
    )

# ==============================================================================
# ROUTE 2: Dataset Upload & Preprocessing
# ==============================================================================
@app.route('/upload', methods=['GET'])
def upload_page():
    initialize_or_refresh_state()
    preview = get_preview_data(APP_STATE['df'], limit=15)
    return render_template(
        'upload.html',
        active_page='upload',
        is_simulated=APP_STATE['is_simulated'],
        summary=APP_STATE['summary'],
        preview=preview
    )

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        flash("No file part detected in request.", "danger")
        return redirect(url_for('upload_page'))
        
    file = request.files['file']
    if file.filename == '':
        flash("No file was selected. Please choose a CSV file.", "warning")
        return redirect(url_for('upload_page'))
        
    if not file.filename.lower().endswith('.csv'):
        flash("Invalid file format. Please upload a standard CSV (.csv) file.", "danger")
        return redirect(url_for('upload_page'))
        
    filename = secure_filename(file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(saved_path)
    
    # Validate and clean uploaded file
    df_new, summary_new, err_msg = load_and_validate_dataset(saved_path)
    if err_msg:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        flash(f"Dataset Validation Error: {err_msg}", "danger")
        return redirect(url_for('upload_page'))
        
    # Successfully parsed! Update application state
    APP_STATE['current_filepath'] = saved_path
    APP_STATE['is_simulated'] = False
    success, process_err = initialize_or_refresh_state(force_reload=True)
    
    if not success:
        flash(f"Error training model on uploaded dataset: {process_err}", "danger")
        return redirect(url_for('upload_page'))
        
    flash(
        f"Dataset successfully uploaded and validated! Processed {summary_new['cleaned_rows']:,} records. "
        f"Handled {summary_new['missing_values_handled']} missing values and removed {summary_new['duplicates_removed']} duplicate timestamps.",
        "success"
    )
    return redirect(url_for('dashboard'))

@app.route('/download-sample-dataset')
def download_sample_dataset():
    if not os.path.exists(SAMPLE_DATASET_PATH):
        from generate_sample_data import generate_sample_dataset
        generate_sample_dataset(SAMPLE_DATASET_PATH)
    return send_file(
        SAMPLE_DATASET_PATH,
        as_attachment=True,
        download_name="sample_electricity_consumption.csv",
        mimetype="text/csv"
    )

@app.route('/reset-dataset')
def reset_dataset():
    APP_STATE['current_filepath'] = SAMPLE_DATASET_PATH
    APP_STATE['is_simulated'] = True
    initialize_or_refresh_state(force_reload=True)
    flash("Active dataset reset to default benchmark simulated smart meter data (8,784 records).", "info")
    return redirect(url_for('dashboard'))

# ==============================================================================
# ROUTE 3: Data Analysis Page
# ==============================================================================
@app.route('/analysis')
def analysis_page():
    initialize_or_refresh_state()
    return render_template(
        'analysis.html',
        active_page='analysis',
        overview=APP_STATE['overview'],
        hourly=APP_STATE['hourly'],
        daily=APP_STATE['daily'],
        monthly=APP_STATE['monthly'],
        peak=APP_STATE['peak'],
        dist=APP_STATE['distribution']
    )

# ==============================================================================
# ROUTE 4: Machine Learning Prediction Page
# ==============================================================================
@app.route('/prediction')
def prediction_page():
    initialize_or_refresh_state()
    return render_template(
        'prediction.html',
        active_page='prediction',
        model_metrics=APP_STATE['model_metrics'],
        test_chart=APP_STATE['test_chart'],
        future_pred=APP_STATE['future_pred'],
        feat_imp=APP_STATE['feat_imp']
    )

@app.route('/retrain-model', methods=['POST'])
def retrain_model():
    try:
        n_estimators = int(request.form.get('n_estimators', 100))
        max_depth = int(request.form.get('max_depth', 14))
        
        n_estimators = max(20, min(300, n_estimators))
        max_depth = max(4, min(30, max_depth))
        
        model_metrics, test_chart, future_pred, feat_imp = train_and_evaluate_model(
            APP_STATE['df'], n_estimators=n_estimators, max_depth=max_depth
        )
        
        APP_STATE['model_metrics'] = model_metrics
        APP_STATE['test_chart'] = test_chart
        APP_STATE['future_pred'] = future_pred
        APP_STATE['feat_imp'] = feat_imp
        
        flash(
            f"Random Forest model retrained with {n_estimators} trees and max_depth={max_depth}! "
            f"New R²: {model_metrics['r2']}, MAE: {model_metrics['mae']} kWh.",
            "success"
        )
    except Exception as e:
        flash(f"Error retraining model: {str(e)}", "danger")
        
    return redirect(url_for('prediction_page'))

# ==============================================================================
# ROUTE 5: Smart Recommendations Page
# ==============================================================================
@app.route('/recommendations')
def recommendations_page():
    initialize_or_refresh_state()
    tariff = session.get('tariff_rate', 7.50)
    recommendations = generate_smart_recommendations(
        APP_STATE['df'],
        APP_STATE['overview'],
        APP_STATE['future_pred'],
        tariff_per_kwh=tariff
    )
    return render_template(
        'recommendations.html',
        active_page='recommendations',
        recommendations=recommendations,
        overview=APP_STATE['overview']
    )

# ==============================================================================
# ROUTE 6: Electricity Bill Calculator Page
# ==============================================================================
@app.route('/bill-calculator')
def bill_calculator_page():
    initialize_or_refresh_state()
    tariff = session.get('tariff_rate', 7.50)
    bill = calculate_electricity_bill(
        APP_STATE['overview']['avg_daily_consumption_kwh'],
        APP_STATE['future_pred']['total_predicted_next_day_kwh'],
        flat_tariff_rate=tariff
    )
    return render_template(
        'bill_calculator.html',
        active_page='bill',
        bill=bill
    )

@app.route('/update-tariff', methods=['POST'])
def update_tariff():
    try:
        new_rate = float(request.form.get('tariff_rate', 7.50))
        if new_rate <= 0:
            new_rate = 7.50
        session['tariff_rate'] = round(new_rate, 2)
        APP_STATE['tariff_rate'] = round(new_rate, 2)
        flash(f"Tariff rate updated to ₹{new_rate:.2f} per kWh.", "success")
    except ValueError:
        flash("Invalid tariff rate entered. Using default ₹7.50/kWh.", "warning")
        
    return redirect(url_for('bill_calculator_page'))

# ==============================================================================
# ROUTE 7: Reports Page & Export Handlers
# ==============================================================================
@app.route('/reports')
def reports_page():
    initialize_or_refresh_state()
    tariff = session.get('tariff_rate', 7.50)
    bill = calculate_electricity_bill(
        APP_STATE['overview']['avg_daily_consumption_kwh'],
        APP_STATE['future_pred']['total_predicted_next_day_kwh'],
        flat_tariff_rate=tariff
    )
    recommendations = generate_smart_recommendations(
        APP_STATE['df'],
        APP_STATE['overview'],
        APP_STATE['future_pred'],
        tariff_per_kwh=tariff
    )
    return render_template(
        'reports.html',
        active_page='reports',
        overview=APP_STATE['overview'],
        model_metrics=APP_STATE['model_metrics'],
        recommendations=recommendations,
        future_pred=APP_STATE['future_pred'],
        bill=bill
    )

@app.route('/download/predictions-csv')
def download_predictions_csv():
    initialize_or_refresh_state()
    csv_bytes = generate_predictions_csv(APP_STATE['future_pred']['forecast_records'])
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=future_24h_electricity_predictions.csv"}
    )

@app.route('/download/analyzed-csv')
def download_analyzed_csv():
    initialize_or_refresh_state()
    csv_bytes = generate_analyzed_data_csv(APP_STATE['df'])
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=analyzed_electricity_dataset.csv"}
    )

@app.route('/download/report-pdf')
def download_report_pdf():
    initialize_or_refresh_state()
    tariff = session.get('tariff_rate', 7.50)
    bill = calculate_electricity_bill(
        APP_STATE['overview']['avg_daily_consumption_kwh'],
        APP_STATE['future_pred']['total_predicted_next_day_kwh'],
        flat_tariff_rate=tariff
    )
    recommendations = generate_smart_recommendations(
        APP_STATE['df'],
        APP_STATE['overview'],
        APP_STATE['future_pred'],
        tariff_per_kwh=tariff
    )
    
    pdf_bytes = generate_pdf_report(
        APP_STATE['overview'],
        APP_STATE['model_metrics'],
        APP_STATE['future_pred'],
        recommendations,
        bill
    )
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-disposition": "attachment; filename=Electricity_Prediction_Report.pdf"}
    )

if __name__ == '__main__':
    # Running locally
    port = int(os.environ.get('PORT', 5001))
    print(f"\n========================================================")
    print(f" EcoPredict Web Application Started Successfully!")
    print(f" Access locally at: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host='127.0.0.1', port=port, debug=False)
