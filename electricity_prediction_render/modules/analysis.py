"""
Data Analysis Module for Electricity Consumption Prediction System.
Computes comprehensive statistical, hourly, daily, weekly, monthly,
peak-load, and distribution analyses using Pandas and NumPy.
"""

import pandas as pd
import numpy as np

def compute_overview_metrics(df):
    """
    Computes top-level dashboard KPI statistics:
    - Total Electricity Consumption (kWh)
    - Average Daily Consumption (kWh)
    - Highest Consumption (kWh)
    - Lowest Consumption (kWh)
    - Peak Electricity Usage Hour
    - Average Hourly Consumption (kWh)
    - Standard Deviation (kWh)
    """
    total_kwh = float(df['consumption_kwh'].sum())
    
    # Daily aggregation
    daily_totals = df.groupby('date')['consumption_kwh'].sum()
    avg_daily_kwh = float(daily_totals.mean()) if len(daily_totals) > 0 else 0.0
    highest_daily_kwh = float(daily_totals.max()) if len(daily_totals) > 0 else 0.0
    
    # Highest single reading
    max_idx = df['consumption_kwh'].idxmax()
    max_record = df.loc[max_idx]
    max_kwh = float(max_record['consumption_kwh'])
    max_time_str = str(max_record['datetime'].strftime('%d %b %Y, %I:%M %p'))
    
    # Lowest single reading
    min_kwh = float(df['consumption_kwh'].min())
    
    # Peak usage hour based on historical mean
    hourly_means = df.groupby('hour')['consumption_kwh'].mean()
    peak_hour = int(hourly_means.idxmax())
    peak_hour_val = float(hourly_means.max())
    
    # Format peak hour string
    peak_period_obj = pd.to_datetime(f"{peak_hour}:00", format="%H:%M")
    peak_hour_formatted = peak_period_obj.strftime("%I:%M %p").lstrip("0")
    
    # Off-peak trough hour
    trough_hour = int(hourly_means.idxmin())
    trough_hour_obj = pd.to_datetime(f"{trough_hour}:00", format="%H:%M")
    trough_hour_formatted = trough_hour_obj.strftime("%I:%M %p").lstrip("0")
    
    avg_hourly = float(df['consumption_kwh'].mean())
    std_dev = float(df['consumption_kwh'].std())
    
    return {
        'total_consumption_kwh': round(total_kwh, 2),
        'avg_daily_consumption_kwh': round(avg_daily_kwh, 2),
        'highest_daily_consumption_kwh': round(highest_daily_kwh, 2),
        'highest_consumption_kwh': round(max_kwh, 2),
        'highest_consumption_timestamp': max_time_str,
        'lowest_consumption_kwh': round(min_kwh, 2),
        'peak_hour': peak_hour,
        'peak_hour_formatted': f"{peak_hour_formatted} ({peak_hour:02d}:00)",
        'peak_hour_avg_kwh': round(peak_hour_val, 2),
        'trough_hour': trough_hour,
        'trough_hour_formatted': f"{trough_hour_formatted} ({trough_hour:02d}:00)",
        'trough_hour_avg_kwh': round(float(hourly_means.min()), 2),
        'avg_hourly_kwh': round(avg_hourly, 2),
        'std_dev_kwh': round(std_dev, 2),
        'total_records': len(df),
        'total_days': len(daily_totals)
    }

def compute_hourly_analysis(df):
    """Computes consumption breakdown across all 24 hours of the day."""
    hourly_grp = df.groupby('hour')['consumption_kwh'].agg(['mean', 'min', 'max', 'std', 'count']).reset_index()
    
    labels = []
    means = []
    mins = []
    maxs = []
    
    records = []
    for _, row in hourly_grp.iterrows():
        h = int(row['hour'])
        time_label = pd.to_datetime(f"{h}:00", format="%H:%M").strftime("%I %p").lstrip("0")
        m = round(float(row['mean']), 2)
        mi = round(float(row['min']), 2)
        ma = round(float(row['max']), 2)
        s = round(float(row['std']) if not pd.isna(row['std']) else 0.0, 2)
        
        labels.append(time_label)
        means.append(m)
        mins.append(mi)
        maxs.append(ma)
        
        # Categorize load zone
        if m >= np.quantile(means if len(means) > 1 else [m], 0.75):
            zone = "Peak Load"
        elif m <= np.quantile(means if len(means) > 1 else [m], 0.25):
            zone = "Off-Peak"
        else:
            zone = "Moderate Load"
            
        records.append({
            'hour': h,
            'time_label': time_label,
            'mean_kwh': m,
            'min_kwh': mi,
            'max_kwh': ma,
            'std_kwh': s,
            'zone': zone
        })
        
    return {
        'labels': labels,
        'means': means,
        'mins': mins,
        'maxs': maxs,
        'table': records
    }

def compute_daily_analysis(df):
    """Computes daily consumption trends and day-of-week breakdown."""
    # Daily aggregation
    daily = df.groupby('date')['consumption_kwh'].agg(['sum', 'mean', 'max', 'count']).reset_index()
    daily['date_str'] = daily['date'].astype(str)
    
    # Subsample if dataset is very large (e.g., > 120 days) for clean line chart rendering
    chart_daily = daily if len(daily) <= 90 else daily.iloc[::max(1, len(daily) // 90)]
    
    daily_labels = [d.strftime('%b %d, %Y') if hasattr(d, 'strftime') else str(d) for d in chart_daily['date']]
    daily_sums = [round(float(s), 2) for s in chart_daily['sum']]
    
    # Day of week breakdown (0=Monday, 6=Sunday)
    dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_grp = df.groupby('day_of_week')['consumption_kwh'].agg(['mean', 'sum']).reindex(range(7)).reset_index()
    
    dow_labels = [dow_names[i] for i in range(7)]
    dow_means = [round(float(dow_grp.loc[dow_grp['day_of_week'] == i, 'mean'].values[0]), 2) if i in dow_grp['day_of_week'].values else 0.0 for i in range(7)]
    
    # Weekday vs Weekend
    weekday_mean = float(df[df['is_weekend'] == 0]['consumption_kwh'].mean()) if (df['is_weekend'] == 0).sum() > 0 else 0.0
    weekend_mean = float(df[df['is_weekend'] == 1]['consumption_kwh'].mean()) if (df['is_weekend'] == 1).sum() > 0 else 0.0
    
    return {
        'daily_chart': {
            'labels': daily_labels,
            'data': daily_sums,
            'values': daily_sums
        },
        'dow_chart': {
            'labels': dow_labels,
            'data': dow_means,
            'values': dow_means
        },
        'weekday_avg': round(weekday_mean, 2),
        'weekend_avg': round(weekend_mean, 2),
        'weekend_variation_pct': round(((weekend_mean - weekday_mean) / weekday_mean * 100), 1) if weekday_mean > 0 else 0.0
    }

def compute_monthly_analysis(df):
    """Computes monthly totals and daily averages."""
    month_names_abbr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly = df.groupby('month')['consumption_kwh'].agg(['sum', 'mean', 'max', 'count']).reset_index()
    
    labels = []
    totals = []
    means = []
    
    records = []
    for _, row in monthly.iterrows():
        m_num = int(row['month'])
        m_label = month_names_abbr[m_num - 1]
        t = round(float(row['sum']), 2)
        m = round(float(row['mean']), 2)
        ma = round(float(row['max']), 2)
        
        labels.append(m_label)
        totals.append(t)
        means.append(m)
        
        records.append({
            'month_num': m_num,
            'month_label': m_label,
            'total_kwh': t,
            'mean_kwh': m,
            'max_kwh': ma,
            'record_count': int(row['count'])
        })
        
    return {
        'labels': labels,
        'totals': totals,
        'means': means,
        'table': records
    }

def compute_peak_analysis(df):
    """Identifies top peak consumption timestamps and peak operational windows."""
    # Top 10 highest consumption records
    top_peaks = df.nlargest(10, 'consumption_kwh')[['datetime', 'consumption_kwh', 'hour', 'day_name', 'month_name']].copy()
    top_peaks_list = []
    for _, r in top_peaks.iterrows():
        top_peaks_list.append({
            'datetime': r['datetime'].strftime('%Y-%m-%d %H:%M'),
            'consumption_kwh': round(float(r['consumption_kwh']), 2),
            'hour': f"{int(r['hour']):02d}:00",
            'day': str(r['day_name']),
            'month': str(r['month_name'])
        })
        
    # Standard peak window: 18:00 - 22:00 (Evening) and 07:00 - 10:00 (Morning)
    peak_mask = df['hour'].isin([18, 19, 20, 21, 22, 7, 8, 9])
    peak_total = float(df[peak_mask]['consumption_kwh'].sum())
    total_all = float(df['consumption_kwh'].sum())
    peak_pct = round((peak_total / total_all * 100), 1) if total_all > 0 else 0.0
    
    return {
        'top_peak_records': top_peaks_list,
        'peak_window_total_kwh': round(peak_total, 2),
        'peak_window_percentage': peak_pct,
        'off_peak_window_percentage': round(100.0 - peak_pct, 1)
    }

def compute_distribution_analysis(df):
    """Calculates histogram frequency bins and quartiles."""
    values = df['consumption_kwh'].values
    
    # 10 histogram bins
    counts, bin_edges = np.histogram(values, bins=10)
    bin_labels = [f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}" for i in range(len(counts))]
    
    # Percentiles
    p25 = float(np.percentile(values, 25))
    p50 = float(np.percentile(values, 50))  # Median
    p75 = float(np.percentile(values, 75))
    p90 = float(np.percentile(values, 90))
    p95 = float(np.percentile(values, 95))
    
    return {
        'labels': bin_labels,
        'counts': [int(c) for c in counts],
        'quartiles': {
            'q1_p25': round(p25, 2),
            'median_p50': round(p50, 2),
            'q3_p75': round(p75, 2),
            'p90': round(p90, 2),
            'p95': round(p95, 2)
        }
    }
