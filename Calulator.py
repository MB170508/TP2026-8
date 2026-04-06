def get_grades():
    total_weighted_sum = 0
    total_weight = 0
    while True:
        try:
            grade = int(input("Enter a grade (1-5), write 0 to stop: "))
            if grade == 0:
                break
            if grade < 1 or grade > 5:
                print("Grade must be between 1 and 5.")
                continue
            weight = float(input("Enter the weight of the grade: "))
            if weight <= 0:
                print("Weight must be greater than 0.")
                continue
            total_weighted_sum += grade * weight
            total_weight += weight
        except ValueError:
            print("Only numbers allowed.")
            continue
    if total_weight == 0:
        print("No grades entered.")
    else:
        average = total_weighted_sum / total_weight
        print(f"Weighted average: {average:.2f}")
get_grades()