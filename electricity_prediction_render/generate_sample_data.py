"""
Sample Electricity Consumption Dataset Generator.
Generates 1 full year of realistic hourly smart meter electricity consumption data (8784 hours for 2024).
Realistic features:
- Morning peak (7:00 - 10:00)
- Midday moderate consumption
- Evening peak (18:00 - 22:00)
- Night trough (01:00 - 05:00)
- Seasonal summer cooling spike (May - July)
- Weekend schedule shifts
- Realistic random stochastic noise and appliance spikes
"""
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "dataset", "sample_electricity_consumption.csv")

def generate_sample_dataset(output_path=DEFAULT_OUTPUT):
    np.random.seed(42)
    # 2024 is a leap year: 366 days * 24 = 8784 hours
    dates = pd.date_range(start="2024-01-01 00:00:00", end="2024-12-31 23:00:00", freq="h")
    
    records = []
    base_load = 1.6  # Base load in kWh (refrigerator, standby, router)
    
    for dt in dates:
        hour = dt.hour
        month = dt.month
        dayofweek = dt.day_of_week  # 0=Monday, 6=Sunday
        is_weekend = 1 if dayofweek in [5, 6] else 0
        
        # Diurnal (hourly) component
        if 0 <= hour <= 5:
            hourly_factor = 0.2 + 0.1 * np.sin((hour / 5.0) * np.pi)
        elif 6 <= hour <= 9:  # Morning peak
            hourly_factor = 2.2 + 0.4 * (1 if not is_weekend else 0.5)
        elif 10 <= hour <= 16:  # Daytime
            hourly_factor = 1.4 + (0.5 if is_weekend else 0.1)
        elif 17 <= hour <= 21:  # Evening peak (lighting, cooking, TV, AC/geyser)
            hourly_factor = 3.2 + 0.3 * np.sin(((hour - 17) / 4.0) * np.pi)
        else:  # 22 - 23 winding down
            hourly_factor = 1.2
            
        # Seasonal component (Indian climate: Hot summer in April-July, mild winter in Dec-Jan)
        if month in [4, 5, 6, 7]:
            season_factor = 1.35 + 0.15 * (1 if 12 <= hour <= 23 else 0.05)  # AC usage
        elif month in [12, 1]:
            season_factor = 1.1 + 0.1 * (1 if 6 <= hour <= 9 else 0.0)  # Geyser usage
        else:
            season_factor = 1.0
            
        # Day of week factor
        dow_factor = 1.15 if is_weekend else 1.0
        
        # Random variation
        noise = np.random.normal(0, 0.25)
        
        # Occasional appliance spike (e.g. laundry, oven, pump)
        spike = 1.8 if np.random.rand() < 0.03 else 0.0
        
        consumption = (base_load + hourly_factor * 1.5) * season_factor * dow_factor + noise + spike
        consumption = max(0.4, round(consumption, 3))
        
        records.append({
            "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "consumption_kwh": consumption
        })
        
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Sample dataset generated successfully at {output_path}: {len(df)} records.")
    return df

if __name__ == "__main__":
    generate_sample_dataset()
