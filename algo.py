import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

# Load the CSV file
file_path_v2 = "/Users/rishi/Projects Python/Fast Food Chain Rep/FastFoodNutritionMenuV2.csv"
nutrition_data_v2 = pd.read_csv(file_path_v2)

# Clean column names for easier handling
nutrition_data_v2.columns = [col.strip().replace('\n', '').replace(' ', '_') for col in nutrition_data_v2.columns]

# Print the cleaned column names to verify
print("Column Names: ", nutrition_data_v2.columns)

# Normalize relevant nutritional values for comparison
# Adjust the feature names to match the cleaned column names
features = ['Calories', 'Total_Fat(g)', 'Saturated_Fat(g)', 'Trans_Fat(g)', 
            'Cholesterol(mg)', 'Sodium_(mg)', 'Carbs(g)', 'Fiber(g)', 
            'Sugars(g)', 'Protein(g)']

# Check if all the features exist in the DataFrame
missing_features = [feature for feature in features if feature not in nutrition_data_v2.columns]
if missing_features:
    print(f"Missing Features: {missing_features}")

# Make a copy of the original data for comparison
original_data = nutrition_data_v2.copy()

# Replace non-numeric values with NaN and drop rows with NaN values
nutrition_data_v2[features] = nutrition_data_v2[features].apply(pd.to_numeric, errors='coerce')
original_data[features] = original_data[features].apply(pd.to_numeric, errors='coerce')
nutrition_data_v2.dropna(subset=features, inplace=True)

# Standardize the features
scaler = StandardScaler()
nutrition_data_v2[features] = scaler.fit_transform(nutrition_data_v2[features])

# Define health score: We will consider lower calories, fat, and sodium as healthier
# Negative impact (lower is better): Calories, Total_Fat, Saturated_Fat, Trans_Fat, Cholesterol, Sodium
# Positive impact (higher is better): Fiber, Protein
health_weights = {
    'Calories': -1,
    'Total_Fat(g)': -1,
    'Saturated_Fat(g)': -1,
    'Trans_Fat(g)': -1,
    'Cholesterol(mg)': -1,
    'Sodium_(mg)': -1,
    'Fiber(g)': 1,
    'Protein(g)': 1
}

# Calculate health score
nutrition_data_v2['Health_Score'] = np.zeros(len(nutrition_data_v2))
for feature, weight in health_weights.items():
    if feature in nutrition_data_v2.columns:
        nutrition_data_v2['Health_Score'] += nutrition_data_v2[feature] * weight

# Function to get healthier alternatives
def get_healthier_alternatives(item_name, top_n=3):
    # Find the item in the dataset
    item_data = original_data[original_data['Item'].str.contains(item_name, case=False, na=False)]
    if item_data.empty:
        return f"Item '{item_name}' not found in the dataset.", None

    # Filter for healthier items
    item_data = item_data.iloc[0]
    healthier_items = original_data[
        (original_data['Calories'] < item_data['Calories']) &
        (original_data['Total_Fat(g)'] < item_data['Total_Fat(g)']) &
        (original_data['Sugars(g)'] < item_data['Sugars(g)']) &
        (original_data['Fiber(g)'] > item_data['Fiber(g)']) &
        (original_data['Protein(g)'] > item_data['Protein(g)'])
    ]

    if healthier_items.empty:
        return f"No healthier alternatives found for '{item_name}'.", None

    # Sort by health score and select top N items
    healthier_items = nutrition_data_v2.loc[healthier_items.index]
    top_healthier_items = healthier_items.sort_values(by='Health_Score').head(top_n)

    original_top_healthier_items = original_data.loc[top_healthier_items.index]
    
    return item_data.to_frame().T, original_top_healthier_items

    

def print_nutritional_comparison(selected_item, item_data, healthier_alternatives):
    print(f"\nNutritional Comparison for '{selected_item}':\n")
    print("Selected Item:")
    print(item_data[['Company', 'Item', 'Calories', 'Total_Fat(g)', 'Saturated_Fat(g)', 'Trans_Fat(g)', 
                     'Cholesterol(mg)', 'Sodium_(mg)', 'Carbs(g)', 'Fiber(g)', 'Sugars(g)', 'Protein(g)']])
    
    print("\nHealthier Alternatives:")
    for index, row in healthier_alternatives.iterrows():
        print("\nItem:")
        print(row[['Company', 'Item']])
        print(f"Calories: {row['Calories']} (Difference: {row['Calories'] - item_data['Calories']})")
        print(f"Total Fat: {row['Total_Fat(g)']} (Difference: {row['Total_Fat(g)'] - item_data['Total_Fat(g)']})")
        print(f"Saturated Fat: {row['Saturated_Fat(g)']} (Difference: {row['Saturated_Fat(g)'] - item_data['Saturated_Fat(g)']})")
        print(f"Trans Fat: {row['Trans_Fat(g)']} (Difference: {row['Trans_Fat(g)'] - item_data['Trans_Fat(g)']})")
        print(f"Cholesterol: {row['Cholesterol(mg)']} (Difference: {row['Cholesterol(mg)'] - item_data['Cholesterol(mg)']})")
        print(f"Sodium: {row['Sodium_(mg)']} (Difference: {row['Sodium_(mg)'] - item_data['Sodium_(mg)']})")
        print(f"Carbs: {row['Carbs(g)']} (Difference: {row['Carbs(g)'] - item_data['Carbs(g)']})")
        print(f"Fiber: {row['Fiber(g)']} (Difference: {row['Fiber(g)'] - item_data['Fiber(g)']})")
        print(f"Sugars: {row['Sugars(g)']} (Difference: {row['Sugars(g)'] - item_data['Sugars(g)']})")
        print(f"Protein: {row['Protein(g)']} (Difference: {row['Protein(g)'] - item_data['Protein(g)']})")

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr, activity_level):
    activity_levels = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    return bmr * activity_levels.get(activity_level.lower(), 1.2)

# Function to get user input for caloric needs calculation
def get_user_caloric_needs():
    weight_pounds = float(input("Enter your weight (pounds): "))
    weight_kg = weight_pounds * 0.453592  # Convert pounds to kilograms
    height = float(input("Enter your height (cm): "))
    age = int(input("Enter your age (years): "))
    gender = input("Enter your gender (male/female): ")
    activity_level = input("Enter your activity level (sedentary, lightly active, moderately active, very active, extra active): ")
    
    bmr = calculate_bmr(weight_kg, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    print(f"\nBased on your inputs, your estimated daily caloric intake is: {tdee:.2f} calories.")
    return tdee

# Function to get nutritional information for a specific item
def get_nutritional_info(item_name):
    item_data = original_data[original_data['Item'].str.contains(item_name, case=False, na=False)]
    if item_data.empty:
        return f"Item '{item_name}' not found in the dataset."
    return item_data[['Company', 'Item', 'Calories', 'Total_Fat(g)', 'Saturated_Fat(g)', 'Trans_Fat(g)', 
                      'Cholesterol(mg)', 'Sodium_(mg)', 'Carbs(g)', 'Fiber(g)', 'Sugars(g)', 'Protein(g)']]

# Example usage for healthier alternatives
selected_item = 'McChicken'
item_data, healthier_alternatives = get_healthier_alternatives(selected_item)

if healthier_alternatives is not None:
    print_nutritional_comparison(selected_item, item_data, healthier_alternatives)
else:
    print(item_data)

#Get user caloric needs
#daily_caloric_intake = get_user_caloric_needs()

