"""
Machine Learning Prediction Module for Electricity Consumption.
Implements Random Forest Regressor with time-series feature engineering,
chronological train-test splitting, recursive 24-hour forecasting,
and model performance evaluation metrics (MAE, RMSE, R², MAPE).
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "random_forest_model.joblib")

# Global cache for trained model and latest prediction results
_MODEL_CACHE = {
    'model': None,
    'metrics': None,
    'test_chart': None,
    'future_predictions': None,
    'feature_importances': None,
    'dataset_hash': None
}

def create_time_features(df):
    """Generates temporal and cyclical features."""
    df = df.copy()
    hour = df['datetime'].dt.hour
    day = df['datetime'].dt.day
    month = df['datetime'].dt.month
    day_of_week = df['datetime'].dt.day_of_week
    
    df['hour'] = hour
    df['day'] = day
    df['month'] = month
    df['day_of_week'] = day_of_week
    df['is_weekend'] = day_of_week.isin([5, 6]).astype(int)
    
    # Cyclical encoding
    df['sin_hour'] = np.sin(2 * np.pi * hour / 24.0)
    df['cos_hour'] = np.cos(2 * np.pi * hour / 24.0)
    df['sin_month'] = np.sin(2 * np.pi * month / 12.0)
    df['cos_month'] = np.cos(2 * np.pi * month / 12.0)
    
    return df

def prepare_feature_matrix(df, include_long_lags=True):
    """
    Constructs feature matrix with adaptive lag features and rolling statistics.
    Prevents data leakage by computing lags strictly forward in time.
    """
    df = create_time_features(df)
    n = len(df)
    
    # Core short-term lag features
    df['lag_1'] = df['consumption_kwh'].shift(1)
    df['lag_2'] = df['consumption_kwh'].shift(2)
    df['lag_3'] = df['consumption_kwh'].shift(3)
    
    feature_cols = [
        'hour', 'day', 'month', 'day_of_week', 'is_weekend',
        'sin_hour', 'cos_hour', 'sin_month', 'cos_month',
        'lag_1', 'lag_2', 'lag_3'
    ]
    
    if n >= 48:
        df['lag_24'] = df['consumption_kwh'].shift(24)
        feature_cols.append('lag_24')
        df['rolling_mean_6'] = df['consumption_kwh'].shift(1).rolling(window=6, min_periods=1).mean()
        df['rolling_mean_24'] = df['consumption_kwh'].shift(1).rolling(window=24, min_periods=1).mean()
        feature_cols.extend(['rolling_mean_6', 'rolling_mean_24'])
    else:
        df['rolling_mean_6'] = df['consumption_kwh'].shift(1).rolling(window=3, min_periods=1).mean()
        feature_cols.append('rolling_mean_6')
        
    if n >= 80:
        df['lag_48'] = df['consumption_kwh'].shift(48)
        feature_cols.append('lag_48')
        
    if n >= 300 and include_long_lags:
        df['lag_168'] = df['consumption_kwh'].shift(168)
        feature_cols.append('lag_168')
        
    # Drop rows containing NaNs introduced by the longest active lag
    df_clean = df.dropna().reset_index(drop=True)
    return df_clean, feature_cols

def train_and_evaluate_model(df, n_estimators=100, max_depth=14):
    """
    Trains the Random Forest Regressor on chronological train/test split.
    Evaluates MAE, RMSE, R², MAPE and caches results.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Feature preparation
    clean_df, feature_cols = prepare_feature_matrix(df)
    
    if len(clean_df) < 15:
        raise ValueError(f"Insufficient records ({len(clean_df)}) after feature engineering to train machine learning model. At least 36-48 hourly records recommended.")
        
    # Chronological Split: 80% train, 20% test (at least 5 samples in test)
    split_idx = int(len(clean_df) * 0.80)
    if len(clean_df) - split_idx < 5:
        split_idx = max(5, len(clean_df) - 5)
        
    train_df = clean_df.iloc[:split_idx]
    test_df = clean_df.iloc[split_idx:]
    
    X_train = train_df[feature_cols]
    y_train = train_df['consumption_kwh']
    
    X_test = test_df[feature_cols]
    y_test = test_df['consumption_kwh']
    
    # Train Random Forest Regressor
    rf = RandomForestRegressor(
        n_estimators=int(n_estimators),
        max_depth=int(max_depth),
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    # Predictions on test set
    y_pred = rf.predict(X_test)
    
    # Evaluation Metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    # MAPE calculation (safe handling of near-zero division)
    mask = y_test > 0.05
    if mask.sum() > 0:
        mape = float(np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100.0)
    else:
        mape = 0.0
        
    # Feature Importances
    importances = rf.feature_importances_
    feat_imp = sorted(
        [{'feature': f, 'importance': round(float(imp * 100), 2)} for f, imp in zip(feature_cols, importances)],
        key=lambda x: x['importance'],
        reverse=True
    )
    
    # Actual vs Predicted sample for visualization (last 120 hours of test set for clarity)
    vis_count = min(120, len(test_df))
    vis_test = test_df.tail(vis_count).copy()
    vis_pred = y_pred[-vis_count:]
    
    test_chart = {
        'timestamps': [dt.strftime('%b %d, %H:%M') for dt in vis_test['datetime']],
        'actual': [round(float(v), 2) for v in vis_test['consumption_kwh'].values],
        'predicted': [round(float(v), 2) for v in vis_pred]
    }
    
    # Save model to disk
    joblib.dump({
        'model': rf,
        'feature_cols': feature_cols
    }, MODEL_PATH)
    
    metrics = {
        'mae': round(float(mae), 3),
        'rmse': round(float(rmse), 3),
        'r2': round(float(r2), 4),
        'mape': round(float(mape), 2),
        'train_samples': len(train_df),
        'test_samples': len(test_df),
        'total_features': len(feature_cols)
    }
    
    # Run 24-hour future forecast
    future_predictions = forecast_next_24_hours(df, rf, feature_cols)
    
    # Cache in memory
    _MODEL_CACHE['model'] = rf
    _MODEL_CACHE['feature_cols'] = feature_cols
    _MODEL_CACHE['metrics'] = metrics
    _MODEL_CACHE['test_chart'] = test_chart
    _MODEL_CACHE['future_predictions'] = future_predictions
    _MODEL_CACHE['feature_importances'] = feat_imp
    
    return metrics, test_chart, future_predictions, feat_imp

def forecast_next_24_hours(df, model=None, feature_cols=None, tariff_per_kwh=7.50):
    """
    Performs multi-step recursive forecasting for the next 24 consecutive hours.
    Uses model predictions as inputs for subsequent lag features.
    """
    if model is None or feature_cols is None:
        if os.path.exists(MODEL_PATH):
            data = joblib.load(MODEL_PATH)
            model = data['model']
            feature_cols = data['feature_cols']
        else:
            raise ValueError("Model is not trained yet. Please train the model first.")
            
    # Prepare historical time series sequence
    sorted_df = df.sort_values(by='datetime').reset_index(drop=True)
    last_dt = sorted_df['datetime'].iloc[-1]
    
    # Working consumption history list to append recursive predictions
    # We need at least the last 200 hours of actuals to compute lags up to lag_168
    history_consumption = list(sorted_df['consumption_kwh'].values)
    
    predictions = []
    accumulated_kwh = 0.0
    
    for step in range(1, 25):
        future_dt = last_dt + pd.Timedelta(hours=step)
        hour = future_dt.hour
        day = future_dt.day
        month = future_dt.month
        day_of_week = future_dt.day_of_week
        is_weekend = 1 if day_of_week in [5, 6] else 0
        
        sin_hour = np.sin(2 * np.pi * hour / 24.0)
        cos_hour = np.cos(2 * np.pi * hour / 24.0)
        sin_month = np.sin(2 * np.pi * month / 12.0)
        cos_month = np.cos(2 * np.pi * month / 12.0)
        
        # Lag values pulled from dynamic history (including prior predictions)
        lag_1 = history_consumption[-1]
        lag_2 = history_consumption[-2] if len(history_consumption) >= 2 else lag_1
        lag_3 = history_consumption[-3] if len(history_consumption) >= 3 else lag_2
        lag_24 = history_consumption[-24] if len(history_consumption) >= 24 else lag_1
        lag_48 = history_consumption[-48] if len(history_consumption) >= 48 else lag_24
        
        rolling_mean_6 = np.mean(history_consumption[-min(len(history_consumption), 6):])
        rolling_mean_24 = np.mean(history_consumption[-min(len(history_consumption), 24):])
        
        feature_dict = {
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'sin_hour': sin_hour,
            'cos_hour': cos_hour,
            'sin_month': sin_month,
            'cos_month': cos_month,
            'lag_1': lag_1,
            'lag_2': lag_2,
            'lag_3': lag_3,
            'lag_24': lag_24,
            'lag_48': lag_48,
            'rolling_mean_6': rolling_mean_6,
            'rolling_mean_24': rolling_mean_24
        }
        
        if 'lag_168' in feature_cols:
            lag_168 = history_consumption[-168] if len(history_consumption) >= 168 else lag_24
            feature_dict['lag_168'] = lag_168
            
        # Create single row DataFrame
        input_row = pd.DataFrame([feature_dict])[feature_cols]
        
        # Predict
        predicted_val = float(model.predict(input_row)[0])
        predicted_val = max(0.2, round(predicted_val, 2))  # Physically bounded
        
        # Append to history for next recursive steps!
        history_consumption.append(predicted_val)
        accumulated_kwh += predicted_val
        
        # Peak status determination
        if hour in [18, 19, 20, 21, 22] or predicted_val > 5.5:
            status = 'Peak Load'
            status_class = 'badge-peak'
        elif hour in [1, 2, 3, 4, 5] or predicted_val < 2.0:
            status = 'Off-Peak'
            status_class = 'badge-offpeak'
        else:
            status = 'Normal'
            status_class = 'badge-normal'
            
        est_cost = round(predicted_val * tariff_per_kwh, 2)
        
        predictions.append({
            'step': step,
            'datetime': future_dt.strftime('%Y-%m-%d %H:%M'),
            'date': future_dt.strftime('%b %d, %Y'),
            'time': future_dt.strftime('%I:%M %p').lstrip("0"),
            'hour': hour,
            'predicted_kwh': predicted_val,
            'status': status,
            'status_class': status_class,
            'estimated_cost_inr': est_cost
        })
        
    return {
        'forecast_records': predictions,
        'total_predicted_next_day_kwh': round(accumulated_kwh, 2),
        'avg_hourly_predicted_kwh': round(accumulated_kwh / 24.0, 2),
        'peak_forecast_kwh': max([p['predicted_kwh'] for p in predictions]),
        'min_forecast_kwh': min([p['predicted_kwh'] for p in predictions]),
        'estimated_total_cost_inr': round(accumulated_kwh * tariff_per_kwh, 2),
        'chart': {
            'labels': [p['time'] for p in predictions],
            'data': [p['predicted_kwh'] for p in predictions],
            'values': [p['predicted_kwh'] for p in predictions],
            'costs': [p['estimated_cost_inr'] for p in predictions]
        }
    }

def get_cached_prediction_results():
    """Returns stored prediction artifacts if available."""
    if _MODEL_CACHE['metrics'] is not None:
        return _MODEL_CACHE
    return None
