"""
Smart Energy Recommendations Module.
Generates dynamic, data-driven energy-saving recommendations,
peak-load shifting strategies, anomaly detection, and predictive comparisons.
"""

import numpy as np
import pandas as pd

def generate_smart_recommendations(df, overview_metrics, prediction_data=None, tariff_per_kwh=7.50):
    """
    Analyzes historical data and machine learning predictions to formulate
    actionable, mathematically grounded energy-saving recommendations.
    """
    recommendations = []
    
    # Baseline statistics
    mean_val = float(df['consumption_kwh'].mean())
    std_val = float(df['consumption_kwh'].std())
    total_kwh = float(df['consumption_kwh'].sum())
    avg_daily_kwh = overview_metrics.get('avg_daily_consumption_kwh', mean_val * 24.0)
    
    # 1. Peak Consumption Window Analysis
    hourly_means = df.groupby('hour')['consumption_kwh'].mean()
    peak_threshold = float(np.percentile(hourly_means.values, 75))
    peak_hours = hourly_means[hourly_means >= peak_threshold].index.tolist()
    
    peak_hours_str = ", ".join([f"{h:02d}:00" for h in sorted(peak_hours)])
    avg_peak_kwh = float(hourly_means[peak_hours].mean()) if len(peak_hours) > 0 else mean_val
    
    # Off-peak hours
    trough_threshold = float(np.percentile(hourly_means.values, 25))
    offpeak_hours = hourly_means[hourly_means <= trough_threshold].index.tolist()
    offpeak_hours_str = ", ".join([f"{h:02d}:00" for h in sorted(offpeak_hours)])
    avg_offpeak_kwh = float(hourly_means[offpeak_hours].mean()) if len(offpeak_hours) > 0 else mean_val
    
    peak_excess_pct = round(((avg_peak_kwh - avg_offpeak_kwh) / avg_offpeak_kwh * 100), 1) if avg_offpeak_kwh > 0 else 0.0
    
    recommendations.append({
        'category': 'Peak Usage Alert',
        'badge': 'High Priority',
        'badge_class': 'badge-danger',
        'icon': 'bi-lightning-charge-fill',
        'title': f'Critical Peak Demand Window: {peak_hours_str}',
        'description': (
            f"Historical analytics reveal your facility consumes an average of {round(avg_peak_kwh, 2)} kWh "
            f"during peak intervals ({peak_hours_str}), which is {peak_excess_pct}% higher than "
            f"your baseline off-peak hours ({round(avg_offpeak_kwh, 2)} kWh)."
        ),
        'action': 'Schedule automated appliance timers or reduce non-critical HVAC and heavy machinery between these peak hours.',
        'potential_impact': f'Reduces peak thermal stress and avoids higher Time-of-Day (ToD) tariff penalties.'
    })
    
    # 2. Anomaly & Surge Detection
    surge_threshold = mean_val + (2.2 * std_val)
    anomalies = df[df['consumption_kwh'] > surge_threshold]
    anomaly_count = len(anomalies)
    
    if anomaly_count > 0:
        max_surge = anomalies.loc[anomalies['consumption_kwh'].idxmax()]
        surge_time = max_surge['datetime'].strftime('%b %d, %Y at %I:%M %p')
        surge_kwh = round(float(max_surge['consumption_kwh']), 2)
        
        recommendations.append({
            'category': 'Anomaly Detection',
            'badge': 'Warning',
            'badge_class': 'badge-warning',
            'icon': 'bi-exclamation-triangle-fill',
            'title': f'{anomaly_count} Unusual Consumption Surges Detected',
            'description': (
                f"We detected {anomaly_count} instances where electricity consumption exceeded {round(surge_threshold, 2)} kWh "
                f"(> 2.2 standard deviations above mean). The highest recorded surge occurred on {surge_time} at {surge_kwh} kWh."
            ),
            'action': 'Inspect heavy machinery, HVAC compressors, or water heaters for continuous cycling, faulty thermostats, or short circuits.',
            'potential_impact': 'Prevents equipment burnout and eliminates phantom load spikes.'
        })
    else:
        recommendations.append({
            'category': 'Consumption Stability',
            'badge': 'Optimal',
            'badge_class': 'badge-success',
            'icon': 'bi-shield-check',
            'title': 'Consistent Load Stability Observed',
            'description': f"No erratic voltage or consumption surges detected. Power usage consistently hovers within normal standard deviations (mean: {round(mean_val, 2)} kWh).",
            'action': 'Continue regular preventative maintenance on main distribution panels.',
            'potential_impact': 'Maintains power factor and extended equipment lifespan.'
        })
        
    # 3. Appliance Load Shifting & Quantified Savings
    # Shifting 25% of peak load to off-peak
    shift_kwh_daily = (avg_peak_kwh * len(peak_hours) * 0.25)
    monthly_shift_kwh = shift_kwh_daily * 30.0
    tod_savings_inr = round(monthly_shift_kwh * (tariff_per_kwh * 0.20), 2)  # Assuming 20% ToD differential or tier savings
    
    recommendations.append({
        'category': 'Load Shifting',
        'badge': 'Cost Optimization',
        'badge_class': 'badge-primary',
        'icon': 'bi-arrow-left-right',
        'title': 'Shift Flexible Loads to Low-Tariff Off-Peak Hours',
        'description': (
            f"Your most economical low-load window occurs during {offpeak_hours_str} (average: {round(avg_offpeak_kwh, 2)} kWh). "
            f"Migrating 25% of flexible energy tasks (e.g. EV charging, laundry, water pumping, storage heaters) "
            f"to this timeframe relocates approx {round(monthly_shift_kwh, 1)} kWh monthly."
        ),
        'action': f"Pre-charge batteries and schedule high-draw loads during off-peak hours ({offpeak_hours_str}).",
        'potential_impact': f"Estimated monthly bill savings of ~₹{tod_savings_inr:,.2f} under standard ToD differential rates."
    })
    
    # 4. Predicted Next-Day Forecast Comparison
    if prediction_data and 'total_predicted_next_day_kwh' in prediction_data:
        pred_next_day = float(prediction_data['total_predicted_next_day_kwh'])
        diff_pct = round(((pred_next_day - avg_daily_kwh) / avg_daily_kwh * 100), 1) if avg_daily_kwh > 0 else 0.0
        
        if diff_pct > 3.0:
            pred_badge = 'Surge Forecast'
            pred_class = 'badge-danger'
            pred_title = f'Next-Day Usage Predicted Higher by {abs(diff_pct)}%'
            pred_desc = (
                f"Machine Learning Random Forest model forecasts tomorrow's total consumption to reach {pred_next_day} kWh, "
                f"which is {diff_pct}% above your historical daily average of {avg_daily_kwh} kWh."
            )
            pred_action = "Pre-cool spaces early in the morning and postpone non-urgent electrical tasks."
        elif diff_pct < -3.0:
            pred_badge = 'Efficiency Forecast'
            pred_class = 'badge-success'
            pred_title = f'Next-Day Usage Predicted Lower by {abs(diff_pct)}%'
            pred_desc = (
                f"Machine Learning model forecasts tomorrow's consumption at {pred_next_day} kWh, "
                f"saving {abs(diff_pct)}% compared to your historical daily average ({avg_daily_kwh} kWh)."
            )
            pred_action = "Maintain disciplined usage habits to lock in this lower expenditure."
        else:
            pred_badge = 'Normal Trend'
            pred_class = 'badge-info'
            pred_title = f'Next-Day Usage Consistent with Historical Average'
            pred_desc = (
                f"Forecast for tomorrow is {pred_next_day} kWh, closely matching your 30-day daily average of {avg_daily_kwh} kWh."
            )
            pred_action = "Ensure ambient temperature settings remain at recommended 24°C - 26°C."
            
        recommendations.append({
            'category': 'Predictive Advisory',
            'badge': pred_badge,
            'badge_class': pred_class,
            'icon': 'bi-graph-up-arrow',
            'title': pred_title,
            'description': pred_desc,
            'action': pred_action,
            'potential_impact': f'Next 24-hour estimated energy cost: ₹{round(pred_next_day * tariff_per_kwh, 2):,.2f}'
        })
        
    # 5. Energy Efficiency & Environmental Impact
    # Indian emission factor: ~0.82 kg CO2 per kWh
    monthly_total_approx = avg_daily_kwh * 30.0
    ten_pct_reduction_kwh = monthly_total_approx * 0.10
    carbon_saved_kg = round(ten_pct_reduction_kwh * 0.82, 1)
    money_saved_inr = round(ten_pct_reduction_kwh * tariff_per_kwh, 2)
    
    recommendations.append({
        'category': 'Green Efficiency',
        'badge': 'Eco-Friendly',
        'badge_class': 'badge-success',
        'icon': 'bi-tree-fill',
        'title': '10% Smart Conservation Strategy',
        'description': (
            f"Adopting BEE 5-Star rated appliances, setting air conditioners to 24°C, and using smart power strips "
            f"to eliminate standby 'vampire' power can comfortably reduce total usage by 10% ({round(ten_pct_reduction_kwh, 1)} kWh/month)."
        ),
        'action': 'Raise AC setpoints by 1°C-2°C and turn off idle computing and entertainment clusters.',
        'potential_impact': f'Save ₹{money_saved_inr:,.2f}/month and reduce carbon footprint by {carbon_saved_kg} kg CO₂/month.'
    })
    
    return {
        'recommendations': recommendations,
        'summary': {
            'peak_hours': peak_hours_str,
            'offpeak_hours': offpeak_hours_str,
            'avg_peak_kwh': round(avg_peak_kwh, 2),
            'avg_offpeak_kwh': round(avg_offpeak_kwh, 2),
            'peak_excess_pct': peak_excess_pct,
            'potential_monthly_savings_inr': tod_savings_inr,
            'carbon_reduction_potential_kg': carbon_saved_kg
        }
    }
