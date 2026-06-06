def calculate_weighted_average(grades: list[tuple[int, float]]) -> dict:
    """Calculate weighted average from list of (grade, weight) tuples.
    
    Args:
        grades: List of tuples (grade, weight) where grade is 1-5 and weight is positive number.
    
    Returns:
        dict with success status and message.
    """
    if not grades:
        return {"success": False, "message": "No grades entered."}
    
    total_weighted_sum = sum(grade * weight for grade, weight in grades)
    total_weight = sum(weight for _, weight in grades)
    
    if total_weight == 0:
        return {"success": False, "message": "Total weight cannot be zero."}
    
    average = total_weighted_sum / total_weight
    return {"success": True, "value": average, "message": f"Weighted average: {average:.2f}"}
