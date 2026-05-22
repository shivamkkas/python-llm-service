from datetime import datetime

def build_alarm_query(asset_id: str) -> str:
    now = datetime.now()
    month_name = now.strftime("%B")
    year = now.year

    return f"""
    Generate an alarm summary report for asset '{asset_id}' 
    for the month of {month_name} {year}.
    
    Include:
    - Total alarms
    - Alarm types distribution
    - Critical vs non-critical count
    - Any anomaly patterns
    
    Ensure data is strictly within {month_name} {year}.
    """