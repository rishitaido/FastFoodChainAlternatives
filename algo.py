'''import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


# Load the CSV file
file_path_v2 = "/Users/rishi/Projects Python/FastFoodNutritionMenuV2.csv"
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
        (original_data['Calories'] <= item_data['Calories']) &
        (original_data['Total_Fat(g)'] < item_data['Total_Fat(g)']) &
        (original_data['Sugars(g)'] < item_data['Sugars(g)']) &
        (original_data['Fiber(g)'] >= item_data['Fiber(g)']) &
        (original_data['Protein(g)'] > item_data['Protein(g)'])
    ]

    if healthier_items.empty:
        return f"No healthier alternatives found for '{item_name}'.", None

    # Sort by health score and select top N items
    healthier_items = nutrition_data_v2.loc[healthier_items.index]
    top_healthier_items = healthier_items.sort_values(by = 'Health_Score').head(top_n)

    original_top_healthier_items = original_data.loc[top_healthier_items.index]
    
    return item_data.to_frame().T, original_top_healthier_items

def print_nutritional_comparison(selected_item, item_data, healthier_alternatives):
    result = f"\nNutritional Comparison for '{selected_item}':\n"
    result += "Selected Item:\n"
    result += f"Company: {item_data['Company'].values[0]}\n"
    result += f"Item: {item_data['Item'].values[0]}\n"
    result += f"Calories: {item_data['Calories'].values[0]}\n"
    result += f"Total Fat: {item_data['Total_Fat(g)'].values[0]}g\n"
    result += f"Protein: {item_data['Protein(g)'].values[0]}g\n"
    result += f"Carbs: {item_data['Carbs(g)'].values[0]}g\n"
    
    result += "\nHealthier Alternatives:\n"
    for index, row in healthier_alternatives.iterrows():
        result += "\nItem:\n"
        result += f"Company: {row['Company']}\n"
        result += f"Item: {row['Item']}\n"
        result += f"Calories: {row['Calories']} (Difference: {row['Calories'] - item_data['Calories'].values[0]})\n"
        result += f"Total Fat: {row['Total_Fat(g)']}g (Difference: {row['Total_Fat(g)'] - item_data['Total_Fat(g)'].values[0]}g)\n"
        result += f"Protein: {row['Protein(g)']}g (Difference: {row['Protein(g)'] - item_data['Protein(g)'].values[0]}g)\n"
        result += f"Carbs: {row['Carbs(g)']}g (Difference: {row['Carbs(g)'] - item_data['Carbs(g)'].values[0]}g)\n"
    return result


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

#GUI 
class NutritionalGUI(tk.Tk): 
    def __init__(self, root):
        self.root = root
        self.root.title("Fast Food Nutrition")

        self.company_label = tk.Label(root, text="Fast Food Chain:")
        self.company_label.grid(row=0, column=0, padx=10, pady=10)
        self.company_entry = tk.Entry(root)
        self.company_entry.grid(row=0, column=1, padx=10, pady=10)

        self.item_label = tk.Label(root, text="Item Name:")
        self.item_label.grid(row=1, column=0, padx=10, pady=10)
        self.item_entry = tk.Entry(root)
        self.item_entry.grid(row=1, column=1, padx=10, pady=10)

        self.search_button = tk.Button(root, text="Search", command=self.search_item)
        self.search_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(root, height=25, width=100, wrap=tk.WORD)
        self.result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        #For users caloric intake
        self.caloric_needs_label = tk.Label(root, text="Calculate Your Caloric Needs:")
        self.caloric_needs_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.weight_label = tk.Label(root, text="Weight (pounds):")
        self.weight_label.grid(row=5, column=0, padx=10, pady=5)
        self.weight_entry = tk.Entry(root)
        self.weight_entry.grid(row=5, column=1, padx=10, pady=5)

        self.height_label = tk.Label(root, text="Height (cm):")
        self.height_label.grid(row=6, column=0, padx=10, pady=5)
        self.height_entry = tk.Entry(root)
        self.height_entry.grid(row=6, column=1, padx=10, pady=5)

        self.age_label = tk.Label(root, text="Age (years):")
        self.age_label.grid(row=7, column=0, padx=10, pady=5)
        self.age_entry = tk.Entry(root)
        self.age_entry.grid(row=7, column=1, padx=10, pady=5)

        self.gender_label = tk.Label(root, text="Gender (male/female):")
        self.gender_label.grid(row=8, column=0, padx=10, pady=5)
        self.gender_entry = tk.Entry(root)
        self.gender_entry.grid(row=8, column=1, padx=10, pady=5)

        self.activity_label = tk.Label(root, text="Activity Level:")
        self.activity_label.grid(row=10, column=0, padx=10, pady=5)
        self.activity_var = tk.StringVar()
        self.activity_dropdown = ttk.Combobox(root, textvariable=self.activity_var)
        self.activity_dropdown['values'] = ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active']
        self.activity_dropdown.grid(row=10, column=1, padx=10, pady=5)

        self.calculate_button = tk.Button(root, text="Calculate Caloric Needs", command=self.calculate_caloric_needs)
        self.calculate_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

    def search_item(self):
        company = self.company_entry.get()
        item_name = self.item_entry.get()
        if company and item_name:
            selected_item = item_name
            item_data, healthier_alternatives = get_healthier_alternatives(selected_item)
            if healthier_alternatives is not None:
                result = print_nutritional_comparison(selected_item, item_data, healthier_alternatives)
            else:
                result = item_data
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
        else:
            messagebox.showwarning("Input Error", "Please enter both the fast food chain and item name.")


    def calculate_caloric_needs(self):
        try:
            weight_pounds = float(self.weight_entry.get())
            weight_kg = weight_pounds * 0.453592  # Convert pounds to kilograms
            height = float(self.height_entry.get())
            age = int(self.age_entry.get())
            gender = self.gender_entry.get()
            activity_level = self.activity_entry.get()
            
            bmr = calculate_bmr(weight_kg, height, age, gender)
            tdee = calculate_tdee(bmr, activity_level)
            
            result = f"\nBased on your inputs, your estimated daily caloric intake is: {tdee:.2f} calories."
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter valid inputs for weight, height, age, gender, and activity level.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NutritionalGUI(root)
    root.mainloop()
'''

