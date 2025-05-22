def calculate_bmr(weight, height, age, gender):
    return (
        88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        if gender.lower() == 'male'
        else 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    )

def calculate_tdee(bmr, activity_level):
    levels = {
        'sedentary': 1.2, 'lightly active': 1.375,
        'moderately active': 1.55, 'very active': 1.725, 'extra active': 1.9
    }
    return bmr * levels.get(activity_level.lower(), 1.2)
