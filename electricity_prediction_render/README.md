# Electricity Consumption Prediction and Smart Energy Analysis System

A modern, responsive, full-stack Data Science and Machine Learning web application designed for academic research, energy audits, and smart grid optimization. Built with **Python Flask**, **Scikit-Learn (Random Forest Regressor)**, **Pandas**, **NumPy**, **Bootstrap 5**, and **Chart.js**.

---

## 🌟 Key Highlights & Project Capabilities

- **Ensemble Machine Learning:** Employs an autoregressive **Random Forest Regressor** trained on chronological time-series splits to prevent look-ahead bias and data leakage ($R^2 \approx 0.95$, $\text{MAE} \approx 0.29 \text{ kWh}$).
- **Recursive Multi-Step 24-Hour Forecasting:** Implements true recursive forecasting where predictions are dynamically appended as lag inputs when future ground-truth data is unavailable.
- **Smart Energy Recommendations:** Dynamically identifies peak operational windows, tracks statistical surges ($> 2.2\sigma$), recommends appliance load-shifting, and quantifies monthly financial savings in Indian Rupees (₹).
- **Interactive Electricity Bill Calculator:** Supports both flat-rate tariffs (₹/kWh) and Indian State DISCOM tiered slab structures (Slabs 1–4) with an interactive conservation simulator.
- **Academic Evaluation & Reports:** Instant PDF project report generation via ReportLab, plus downloadable 24-hour predictions CSV and preprocessed historical datasets.
- **Modern Responsive UI:** Dark navy blue (`#0f172a`) and electric green (`#00e676`) aesthetic with clean white dashboard cards, interactive Chart.js visualizations, and mobile sidebar navigation.

---

## 🏗️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend Framework** | Python 3.10+, Flask 3.1 |
| **Data Science & ML** | Pandas 2.2+, NumPy 1.26+, Scikit-Learn 1.4+, SciPy |
| **Document Generation** | ReportLab 5.1 (Automated PDF Report Generator) |
| **Model Persistence** | Joblib |

---

## 📁 Project Structure

```text
electricity_prediction/
├── app.py                      # Core Flask application, routing, and session management
├── requirements.txt            # Python dependencies
├── generate_sample_data.py     # 8,784-hour realistic smart meter dataset generator
├── test_pipeline.py            # End-to-end analytical pipeline verification script
├── test_routes.py              # Automated test suite for Flask web endpoints
├── test_upload.py              # File upload validation & edge case test script
├── dataset/
│   └── sample_electricity_consumption.csv  # 1 full year (8,784 hours) of smart meter data
├── models/
│   └── random_forest_model.joblib          # Serialized Random Forest model artifact
├── modules/
│   ├── __init__.py
│   ├── data_processing.py      # CSV validation, missing value imputation, feature extraction
│   ├── analysis.py             # Diurnal, daily, weekly, monthly, peak, & distribution statistics
│   ├── prediction.py           # Feature matrix construction, RF training, recursive 24h forecasting
│   ├── recommendations.py      # Dynamic load-shifting, anomaly tracking, & energy advice
│   ├── bill_calculator.py      # Indian DISCOM slab calculations & efficiency simulator
│   └── report_generator.py     # PDF project report generation (ReportLab) & CSV exports
├── static/
│   ├── css/
│   │   └── style.css           # Custom dark navy & electric green styles and responsive layout
│   └── js/
│       ├── charts.js           # Reusable Chart.js initialization and styling helpers
│       └── main.js             # Client-side sidebar toggle, drag-and-drop, and live calculators
├── templates/
│   ├── base.html               # Master layout containing navigation sidebar & sticky header
│   ├── index.html              # Alias for dashboard view
│   ├── dashboard.html          # Main overview with 6 KPIs and 5 interactive charts
│   ├── upload.html             # Drag-and-drop CSV upload, validation report, and table preview
│   ├── analysis.html           # In-depth temporal breakdown, peak zones, & quartiles
│   ├── prediction.html         # ML metrics (MAE, RMSE, R²), actual vs predicted, & 24h schedule
│   ├── recommendations.html    # AI energy advisories, anomaly surges, & appliance shifting matrix
│   ├── bill_calculator.html    # Interactive tariff calculator & DISCOM tiered slab breakdowns
│   └── reports.html            # Download center for PDF report and CSV exports
└── uploads/                    # Temporary storage for user-uploaded CSV files
```

---

## ⚙️ Installation & Local Setup (macOS / Linux / Windows)

### 1. Prerequisites
Ensure you have **Python 3.10 or higher** installed. Verify via:
```bash
python3 --version
```

### 2. Navigate to Project Directory
```bash
cd /Users/faizalhameed/.gemini/antigravity/scratch/electricity_prediction
```

### 3. Create & Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS / Linux:
source venv/bin/activate

# Activate on Windows (Command Prompt):
# venv\Scripts\activate.bat
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Generate Benchmark Sample Dataset (Optional - Generated Automatically on Boot)
```bash
python3 generate_sample_data.py
```

### 6. Run Automated Verification Tests
```bash
# Verify end-to-end ML & analytical pipeline:
python3 test_pipeline.py

# Verify all Flask web routes and exports:
python3 test_routes.py
```

### 7. Launch Web Server
```bash
python3 app.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5001
```

---

## 🔬 In-Depth Module Explanations

### 1. Data Processing Module (`modules/data_processing.py`)
- **Schema Validation:** Verifies the presence of `datetime` and `consumption_kwh` columns (supporting flexible header variants such as `timestamp`, `date`, `kwh`, `units`, `usage`).
- **Temporal Cleaning:** Parses string timestamps with error handling, removes duplicate timestamps, and clips unphysical negative readings.
- **Missing Value Imputation:** Applies linear interpolation with forward/backward fill for time-series continuity.
- **Feature Extraction:** Derives `hour`, `day`, `month`, `day_of_week`, `is_weekend`, `sin_hour`, `cos_hour`, `sin_month`, `cos_month`.

### 2. Statistical Analysis Module (`modules/analysis.py`)
- **Top KPIs:** Computes total energy (kWh), average daily consumption, highest consumption spike, lowest standby consumption, and peak load hour.
- **Temporal Breakdown:** Generates 24-hour diurnal load profiles, day-of-week averages, weekday vs. weekend shifts, and monthly consumption trends.
- **Peak Identification:** Ranks the top 10 historical consumption surges and calculates the total proportion of energy consumed during peak hours (Morning: 7–10 AM; Evening: 6–10 PM).
- **Distribution Metrics:** Constructs 10-bin histograms and computes quantiles ($Q_1$, Median, $Q_3$, 90th percentile, 95th percentile).

### 3. Machine Learning Prediction Module (`modules/prediction.py`)
- **Algorithm:** Scikit-Learn `RandomForestRegressor(n_estimators=100, max_depth=14, min_samples_split=4, random_state=42)`.
- **Feature Engineering:**
  - Short-term autoregressive lags: $t-1$, $t-2$, $t-3$.
  - Seasonal lags: $t-24$ (yesterday same hour), $t-48$ (2 days prior), $t-168$ (same hour last week).
  - Rolling windows: 6-hour and 24-hour moving averages.
- **Chronological Split:** Preserves time-series continuity (80% training, 20% test) without shuffling to avoid data leakage.
- **Evaluation Metrics:**
  - **MAE (Mean Absolute Error):** $\approx 0.29 \text{ kWh}$
  - **RMSE (Root Mean Squared Error):** $\approx 0.44 \text{ kWh}$
  - **$R^2$ Score (Coefficient of Determination):** $\approx 0.95$
  - **MAPE (Mean Absolute Percentage Error):** $\approx 7.5\%$
- **Recursive Multi-Step Forecasting:** Projects 24 consecutive future hours. When actual future values are unavailable, predictions are fed back iteratively into lag features.

### 4. Smart Energy Recommendations Module (`modules/recommendations.py`)
- **Peak Period Alert:** Dynamically detects high-load hours (e.g., 6:00 PM – 10:00 PM) where usage exceeds the 75th percentile and quantifies excess load.
- **Anomaly Detection:** Flags hours where consumption exceeds $\mu + 2.2\sigma$, identifying potential equipment cycling issues or short circuits.
- **Appliance Load Shifting:** Quantifies the financial savings of migrating 25% of flexible appliance loads (EV charging, washing machines, pumps) to off-peak periods.
- **Predictive Advisory:** Compares the ML model's next 24-hour forecast against the 30-day historical daily average to provide proactive alerts.
- **Carbon Footprint Tracking:** Translates energy reductions into avoided greenhouse gas emissions using the Indian grid factor ($0.82 \text{ kg CO}_2\text{/kWh}$).

### 5. Electricity Bill Calculator Module (`modules/bill_calculator.py`)
- **Configurable Tariff:** Allows custom flat rates in Indian Rupees (default ₹7.50/kWh).
- **Indian DISCOM Tiered Slabs:**
  - Slab 1 (0–100 kWh): ₹4.50/kWh
  - Slab 2 (101–300 kWh): ₹7.00/kWh
  - Slab 3 (301–500 kWh): ₹9.50/kWh
  - Slab 4 (>500 kWh): ₹11.00/kWh
- **Efficiency Scenarios:** Simulates cost savings at 5%, 10%, 15%, and 20% consumption reduction.

### 6. Report Generator Module (`modules/report_generator.py`)
- **PDF Report Generation:** Uses ReportLab to generate a publication-ready academic project evaluation report with tables, metrics, and recommendations.
- **CSV Data Exports:** Exports future 24-hour predictions and preprocessed historical datasets.

---

## 🖥️ Web Application Pages Walkthrough

1. **Dashboard (`/` or `/dashboard`):**
   - 6 KPI Statistics Cards: Total Consumption, Daily Average, Highest Surge, Next 24h Prediction, Estimated Monthly Bill, Peak Hour.
   - 5 Interactive Charts: Daily Consumption Trend, Monthly Bar Chart, Diurnal Hourly Curve, Actual vs. Predicted (Test Set), and Distribution Histogram.
2. **Dataset Upload (`/upload`):**
   - Drag-and-drop CSV upload zone with file size & format validation.
   - Active dataset statistics (cleaned rows, duplicates dropped, missing values filled, date range).
   - Interactive preview of the first 15 cleaned records.
   - Sample CSV download and session reset options.
3. **Data Analysis (`/analysis`):**
   - 24-hour hourly profile with load zone classifications (Peak, Moderate, Off-Peak).
   - Day-of-week breakdown and weekday vs. weekend variation comparisons.
   - Monthly energy seasonality table and charts.
   - Top 10 peak surge events ranking.
4. **ML Prediction (`/prediction`):**
   - Random Forest model metrics with educationalViva explanations for $R^2$, MAE, RMSE, and MAPE.
   - Hyperparameter tuning modal (adjust estimators & max depth with live retraining).
   - Unseen test split Actual vs. Predicted line chart.
   - Top predictive feature importance ranking.
   - Next 24-hour recursive forecast line chart and hourly schedule table.
5. **Smart Recommendations (`/recommendations`):**
   - Actionable energy-saving advisory cards with priority badges.
   - Appliance load-shifting matrix (EV chargers, HVAC, water pumps, washing machines, geysers).
6. **Bill Calculator (`/bill-calculator`):**
   - Interactive tariff adjustment in Indian Rupees (₹) with real-time recalculations.
   - Monthly tiered slab breakdown.
   - Targeted efficiency reduction simulator (5% to 20%).
7. **Reports & Exports (`/reports`):**
   - Download formal project PDF report.
   - Download next 24-hour prediction CSV.
   - Download cleaned historical dataset CSV.

---

## 🎓 Viva & Presentation Talking Points (For B.Tech Presentation)

1. **Why Random Forest over Simple Linear Regression?**
   - Electricity consumption exhibits strong non-linear relationships, sharp threshold transitions (e.g., HVAC kicking in above certain temperatures), and diurnal cyclicality. Random Forest captures complex feature interactions and non-linear boundaries without requiring scaling.
2. **How is Data Leakage Prevented in Time Series?**
   - Unlike standard tabular machine learning where `train_test_split(shuffle=True)` is common, time series models must be split **chronologically**. Training on past data (first 80%) and testing on future data (last 20%) ensures the model never peeks ahead. Lag and rolling features are shifted strictly forward ($t-1$, $t-24$).
3. **What is Recursive Forecasting?**
   - When predicting multiple future hours without actual meter readings, the model generates $\hat{y}_{t+1}$, uses it as the $lag_1$ input to predict $\hat{y}_{t+2}$, and continues iteratively across all 24 future intervals.
4. **Why is RMSE Higher than MAE?**
   - RMSE squares errors before averaging, penalizing larger prediction spikes. For electric utilities, underestimating peak spikes carries high operational risk, making RMSE an essential metric alongside MAE.

---

## 📜 License
Developed for educational, research, and academic evaluation purposes.
