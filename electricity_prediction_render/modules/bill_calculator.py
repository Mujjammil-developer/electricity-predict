"""
Electricity Bill Calculator Module.
Computes estimated energy costs based on user-defined tariff rates,
Indian DISCOM tiered tariff slabs, Time-of-Day (ToD) rates,
and efficiency reduction simulation scenarios.
"""

# Default standard Indian DISCOM residential/commercial tiered tariff slabs
DEFAULT_SLABS = [
    {"limit": 100, "rate": 4.50, "label": "0 - 100 kWh (Slab 1)"},
    {"limit": 200, "rate": 7.00, "label": "101 - 300 kWh (Slab 2)"},
    {"limit": 200, "rate": 9.50, "label": "301 - 500 kWh (Slab 3)"},
    {"limit": float('inf'), "rate": 11.00, "label": "> 500 kWh (Slab 4)"}
]

def calculate_slab_bill(kwh, slabs=None):
    """
    Computes total electricity cost based on tiered slab rates.
    """
    if slabs is None:
        slabs = DEFAULT_SLABS
        
    remaining_kwh = float(kwh)
    total_cost = 0.0
    breakdown = []
    
    for slab in slabs:
        if remaining_kwh <= 0:
            break
        limit = slab["limit"]
        rate = slab["rate"]
        label = slab["label"]
        
        consumed_in_slab = min(remaining_kwh, limit)
        slab_cost = consumed_in_slab * rate
        total_cost += slab_cost
        remaining_kwh -= consumed_in_slab
        
        breakdown.append({
            "slab": label,
            "units_consumed": round(consumed_in_slab, 2),
            "rate_per_unit": rate,
            "cost_inr": round(slab_cost, 2)
        })
        
    return round(total_cost, 2), breakdown

def calculate_electricity_bill(daily_kwh, predicted_kwh=None, flat_tariff_rate=7.50, slabs=None):
    """
    Calculates detailed electricity bill estimates in Indian Rupees (₹).
    
    Parameters:
        daily_kwh (float): Average daily consumption in kWh
        predicted_kwh (float): Next 24-hour predicted consumption in kWh
        flat_tariff_rate (float): User specified rate per kWh in ₹
        slabs (list): Optional custom slab configuration
    """
    daily_kwh = max(0.0, float(daily_kwh))
    monthly_kwh = daily_kwh * 30.0
    annual_kwh = daily_kwh * 365.0
    
    # Flat rate calculations
    flat_daily_cost = round(daily_kwh * flat_tariff_rate, 2)
    flat_monthly_cost = round(monthly_kwh * flat_tariff_rate, 2)
    flat_annual_cost = round(annual_kwh * flat_tariff_rate, 2)
    
    # Tiered slab calculation on monthly consumption
    slab_monthly_cost, slab_breakdown = calculate_slab_bill(monthly_kwh, slabs)
    slab_daily_cost = round(slab_monthly_cost / 30.0, 2)
    
    # Predicted 24-hour cost
    if predicted_kwh is not None:
        pred_kwh = max(0.0, float(predicted_kwh))
        pred_cost_flat = round(pred_kwh * flat_tariff_rate, 2)
        # Daily variance
        cost_diff = round(pred_cost_flat - flat_daily_cost, 2)
        cost_diff_pct = round(((pred_cost_flat - flat_daily_cost) / flat_daily_cost * 100), 1) if flat_daily_cost > 0 else 0.0
    else:
        pred_kwh = daily_kwh
        pred_cost_flat = flat_daily_cost
        cost_diff = 0.0
        cost_diff_pct = 0.0
        
    # Energy savings simulator (5%, 10%, 15%, 20% reduction)
    savings_scenarios = []
    for reduction_pct in [5, 10, 15, 20]:
        saved_kwh_month = round(monthly_kwh * (reduction_pct / 100.0), 2)
        new_monthly_kwh = round(monthly_kwh - saved_kwh_month, 2)
        saved_amount_inr = round(saved_kwh_month * flat_tariff_rate, 2)
        new_bill_inr = round(flat_monthly_cost - saved_amount_inr, 2)
        
        savings_scenarios.append({
            'reduction_pct': reduction_pct,
            'saved_kwh_month': saved_kwh_month,
            'new_monthly_kwh': new_monthly_kwh,
            'saved_amount_inr': saved_amount_inr,
            'new_bill_inr': new_bill_inr
        })
        
    return {
        'flat_tariff_rate': flat_tariff_rate,
        'daily_consumption_kwh': round(daily_kwh, 2),
        'monthly_consumption_kwh': round(monthly_kwh, 2),
        'annual_consumption_kwh': round(annual_kwh, 2),
        'flat_daily_cost': flat_daily_cost,
        'flat_monthly_cost': flat_monthly_cost,
        'flat_annual_cost': flat_annual_cost,
        'slab_monthly_cost': slab_monthly_cost,
        'slab_daily_cost': slab_daily_cost,
        'slab_breakdown': slab_breakdown,
        'predicted_kwh': round(pred_kwh, 2),
        'predicted_daily_cost': pred_cost_flat,
        'cost_difference': cost_diff,
        'cost_difference_pct': cost_diff_pct,
        'savings_scenarios': savings_scenarios,
        'disclaimer': "Calculations are realistic estimates based on energy consumption. Excludes fixed meter rents, municipal taxes, electricity duties, and fuel surcharge adjustments (FSA) unless configured."
    }
