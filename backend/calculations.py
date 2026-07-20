def calculate_bmr(weight: float, height: float, age: int, sex: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
    
    weight: kg
    height: cm
    age: years
    sex: "male" or "female"
    """
    if sex.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return bmr

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure
    
    activity_level options:
    - sedentary: 1.2
    - light: 1.375
    - moderate: 1.55
    - active: 1.725
    - very_active: 1.9
    """
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    factor = activity_factors.get(activity_level.lower(), 1.55)
    tdee = bmr * factor
    
    return tdee

def calculate_daily_calorie_target(tdee: float, goal: str, sex: str) -> float:
    """
    Calculate daily calorie target based on goal
    
    goal options:
    - lose: TDEE - 500
    - maintain: TDEE
    - gain: TDEE + 400
    
    Minimum safety floor:
    - Female: 1200
    - Male: 1500
    """
    if goal.lower() == "lose":
        target = tdee - 500
    elif goal.lower() == "gain":
        target = tdee + 400
    else:  # maintain
        target = tdee
    
    # Safety floor
    min_calories = 1200 if sex.lower() == "female" else 1500
    target = max(target, min_calories)
    
    return target

def calculate_status(total_calories: int, daily_target: int) -> str:
    """
    Determine status based on calorie intake
    
    - "Low": below target
    - "On Target": within 100 calories of target
    - "Over": more than 100 calories above target
    """
    if total_calories < daily_target:
        return "Low"
    elif total_calories <= daily_target + 100:
        return "On Target"
    else:
        return "Over"