"""
Data Processing Module for Electricity Consumption Prediction System.
Handles dataset loading, validation, cleaning, missing-value imputation,
duplicate removal, and time-based feature engineering.
"""

import os
import pandas as pd
import numpy as np

def find_matching_column(columns, candidates):
    """Helper to find column by case-insensitive candidates."""
    cols_lower = {col.strip().lower(): col for col in columns}
    for candidate in candidates:
        if candidate.lower() in cols_lower:
            return cols_lower[candidate.lower()]
    # Substring search
    for candidate in candidates:
        for col_lower, original in cols_lower.items():
            if candidate.lower() in col_lower:
                return original
    return None

def load_and_validate_dataset(filepath_or_buffer):
    """
    Loads, validates, and cleans the electricity consumption dataset.
    
    Required logical columns:
    - datetime: string or timestamp
    - consumption_kwh: numeric value in kWh
    
    Returns:
        tuple: (cleaned_df, summary_dict, error_message)
    """
    try:
        # Check if file exists or read buffer
        if isinstance(filepath_or_buffer, str):
            if not os.path.exists(filepath_or_buffer):
                return None, None, f"Dataset file not found: {filepath_or_buffer}"
            # Read first few lines to check delimiter
            with open(filepath_or_buffer, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                sep = ';' if ';' in first_line and ',' not in first_line else ','
            df = pd.read_csv(filepath_or_buffer, sep=sep, encoding='utf-8')
        else:
            df = pd.read_csv(filepath_or_buffer)
            
        raw_rows = len(df)
        if raw_rows == 0:
            return None, None, "The uploaded CSV file is empty."
            
        # Column mapping
        datetime_col = find_matching_column(df.columns, [
            'datetime', 'date_time', 'timestamp', 'date', 'time', 'date/time'
        ])
        consumption_col = find_matching_column(df.columns, [
            'consumption_kwh', 'consumption', 'kwh', 'usage', 'usage_kwh', 
            'energy', 'power_kwh', 'units', 'meter_reading', 'load'
        ])
        
        missing_cols = []
        if not datetime_col:
            missing_cols.append("datetime (or timestamp/date)")
        if not consumption_col:
            missing_cols.append("consumption_kwh (or usage/kwh/units)")
            
        if missing_cols:
            return None, None, (
                f"Missing required columns: {', '.join(missing_cols)}. "
                f"Found columns: {list(df.columns)}. "
                f"Please ensure columns 'datetime' and 'consumption_kwh' are present."
            )
            
        # Rename to standardized columns
        df = df.rename(columns={datetime_col: 'datetime', consumption_col: 'consumption_kwh'})
        
        # Keep only required columns initially
        df = df[['datetime', 'consumption_kwh']].copy()
        
        # 1. Datetime conversion
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        nat_count = int(df['datetime'].isna().sum())
        df = df.dropna(subset=['datetime'])
        
        if len(df) == 0:
            return None, None, "Failed to parse any valid datetime values from the 'datetime' column."
            
        # 2. Consumption numeric conversion
        df['consumption_kwh'] = pd.to_numeric(df['consumption_kwh'], errors='coerce')
        nan_consumption_count = int(df['consumption_kwh'].isna().sum())
        
        # Sort chronologically
        df = df.sort_values(by='datetime').reset_index(drop=True)
        
        # 3. Duplicate handling
        duplicates_count = int(df.duplicated(subset=['datetime']).sum())
        if duplicates_count > 0:
            # Group by datetime and take mean for duplicates
            df = df.groupby('datetime', as_index=False)['consumption_kwh'].mean()
            df = df.sort_values(by='datetime').reset_index(drop=True)
            
        # 4. Missing value imputation for consumption
        # For time-series, linear interpolation with forward/backward fill is best practice
        if df['consumption_kwh'].isna().sum() > 0:
            df['consumption_kwh'] = df['consumption_kwh'].interpolate(method='linear', limit_direction='both')
            df['consumption_kwh'] = df['consumption_kwh'].bfill().ffill()
            
        # Check for negative values (anomalies / invalid sensors)
        negative_count = int((df['consumption_kwh'] < 0).sum())
        if negative_count > 0:
            df['consumption_kwh'] = df['consumption_kwh'].clip(lower=0.0)
            
        cleaned_rows = len(df)
        if cleaned_rows < 24:
            return None, None, f"Dataset contains only {cleaned_rows} valid records. At least 24 hourly records are required for meaningful time-series analysis and prediction."
            
        # Extract calendar and time features
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        df['month_name'] = df['datetime'].dt.strftime('%b')
        df['day'] = df['datetime'].dt.day
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_of_week  # 0=Monday, 6=Sunday
        df['day_name'] = df['datetime'].dt.strftime('%A')
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['date'] = df['datetime'].dt.date
        
        # Summary metadata
        summary = {
            'total_raw_rows': raw_rows,
            'cleaned_rows': cleaned_rows,
            'invalid_dates_dropped': nat_count,
            'missing_values_handled': nan_consumption_count,
            'duplicates_removed': duplicates_count,
            'negative_values_clipped': negative_count,
            'start_date': str(df['datetime'].min()),
            'end_date': str(df['datetime'].max()),
            'total_days': round((df['datetime'].max() - df['datetime'].min()).total_seconds() / 86400, 1),
            'min_consumption': round(float(df['consumption_kwh'].min()), 3),
            'max_consumption': round(float(df['consumption_kwh'].max()), 3),
            'mean_consumption': round(float(df['consumption_kwh'].mean()), 3),
            'median_consumption': round(float(df['consumption_kwh'].median()), 3),
            'total_kwh': round(float(df['consumption_kwh'].sum()), 2)
        }
        
        return df, summary, None
        
    except Exception as e:
        return None, None, f"Error processing dataset: {str(e)}"

def get_preview_data(df, limit=15):
    """Returns top rows formatted for UI preview table."""
    preview_df = df[['datetime', 'consumption_kwh', 'hour', 'day_name', 'month_name']].head(limit).copy()
    preview_df['datetime'] = preview_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
    return preview_df.to_dict(orient='records')
