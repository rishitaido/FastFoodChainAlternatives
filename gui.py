# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from data_loader import load_and_process_data
from health_score import compute_health_score, get_healthier_alternatives
from caloric_needs import calculate_bmr, calculate_tdee
import pandas as pd

class NutritionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Healthy Fast Food Finder")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.include_drink = tk.BooleanVar(value=False)
        self.df, self.features = load_and_process_data("FastFoodNutritionMenuV2.csv")
        self.df_scored = compute_health_score(self.df.copy(), self.features)

        self.setup_ui()

    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=15)

        title = ttk.Label(header_frame, text="Healthy Fast Food Finder", font=("Helvetica", 20, "bold"))
        title.pack()

        subtitle = ttk.Label(header_frame, text="Find better alternatives. Eat smart, live well.", font=("Helvetica", 12))
        subtitle.pack()

        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        self.entry_label = ttk.Label(input_frame, text="Enter Menu Item:")
        self.entry_label.grid(row=0, column=0, padx=5)

        self.entry = ttk.Entry(input_frame, width=40)
        self.entry.grid(row=0, column=1, padx=5)

        self.search_button = ttk.Button(input_frame, text="🔍 Search Alternatives", command=self.search)
        self.search_button.grid(row=0, column=2, padx=5)

        self.calories_button = ttk.Button(input_frame, text="🍽 Caloric Needs Calculator", command=self.open_calorie_calc)
        self.calories_button.grid(row=1, column=1, pady=10)

        self.recommend_button = ttk.Button(input_frame, text="📋 Recommend Full Day Plan", command=self.recommend_meals)
        self.recommend_button.grid(row=2, column=1, pady=10)

        self.drink_checkbox = ttk.Checkbutton(input_frame, text="Include 0-Calorie Drink", variable=self.include_drink)
        self.drink_checkbox.grid(row=3, column=1, pady=5)

        self.result_text = tk.Text(self.root, height=20, width=100)
        self.result_text.pack(pady=10)

    def search(self):
        item_name = self.entry.get().strip()
        self.result_text.delete("1.0", tk.END)

        if not item_name:
            messagebox.showwarning("Input Error", "Please enter a menu item to search.")
            return

        original, alternatives = get_healthier_alternatives(item_name, self.df, self.df_scored)
        if isinstance(original, str):
            self.result_text.insert(tk.END, original)
        else:
            if original is None or not isinstance(original, pd.DataFrame):
                self.result_text.insert(tk.END, "Could not find the original item in the dataset.")
            return

        cal_col = next((col for col in original.columns if 'calories' in col.lower()), 'Calories')
        fat_col = next((col for col in original.columns if 'fat' in col.lower()), 'Total_Fat')
        protein_col = next((col for col in original.columns if 'protein' in col.lower()), 'Protein')

        cols = [col for col in ['Item', cal_col, fat_col, protein_col] if col in original.columns]
        self.result_text.insert(tk.END, f"Original Item:{original[cols].to_string(index=False)}")
        if alternatives is not None:
            self.result_text.insert(tk.END, "Healthier Alternatives:\n")
            self.result_text.insert(tk.END, f"{alternatives[['Item', 'Calories', 'Total_Fat_(g)', 'Protein_(g)']].to_string(index=False)}")
        else:
            self.result_text.insert(tk.END, "No healthier alternatives found.")

    def open_calorie_calc(self):
        top = tk.Toplevel(self.root)
        top.title("Caloric Needs Calculator")
        top.geometry("400x400")

        self.weight_var = tk.DoubleVar()
        self.feet_var = tk.IntVar()
        self.inches_var = tk.IntVar()
        self.age_var = tk.IntVar()
        self.gender_var = tk.StringVar()
        self.activity_var = tk.StringVar()
        self.chain_var = tk.StringVar()

        labels = ["Weight (lbs):", "Height (feet):", "Height (inches):", "Age:", "Gender:", "Activity Level:"]
        values = [self.weight_var, self.feet_var, self.inches_var, self.age_var, self.gender_var, self.activity_var]

        for i, label_text in enumerate(labels):
            ttk.Label(top, text=label_text).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            if label_text == "Activity Level:":
                activity_options = ['Sedentary', 'Lightly active', 'Moderately active', 'Very active', 'Extra active']
                activity_menu = ttk.Combobox(top, textvariable=self.activity_var, values=activity_options, state='readonly')
                activity_menu.grid(row=i, column=1, pady=5)
                activity_menu.current(0)
            else:
                ttk.Entry(top, textvariable=values[i], width=25).grid(row=i, column=1, pady=5)

        ttk.Label(top, text="Preferred Fast Food Chain:").grid(row=6, column=0, sticky='w', padx=10, pady=5)
        chains = sorted(self.df['Company'].unique())
        chain_menu = ttk.Combobox(top, textvariable=self.chain_var, values=chains, state='readonly')
        chain_menu.grid(row=6, column=1, pady=5)
        chain_menu.current(0)

        calc_button = ttk.Button(top, text="Calculate & Recommend", command=self.calculate_tdee_popup)
        calc_button.grid(row=7, column=0, columnspan=2, pady=15)

        self.result_label = ttk.Label(top, text="")
        self.result_label.grid(row=8, column=0, columnspan=2)

    def calculate_tdee_popup(self):
        try:
            weight_lbs = self.weight_var.get()
            feet = self.feet_var.get()
            inches = self.inches_var.get()
            age = self.age_var.get()
            gender = self.gender_var.get()
            activity_level = self.activity_var.get()

            weight_kg = weight_lbs * 0.453592
            height_cm = (feet * 12 + inches) * 2.54

            bmr = calculate_bmr(weight_kg, height_cm, age, gender)
            self.tdee = calculate_tdee(bmr, activity_level)
            self.selected_chain = self.chain_var.get()
            self.result_label.config(text=f"Estimated TDEE: {self.tdee:.2f} cal/day for {self.selected_chain}")
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def recommend_meals(self):
        try:
            tdee = self.tdee
            chain = self.selected_chain
        except AttributeError:
            messagebox.showwarning("Missing Info", "Please calculate TDEE first using the Caloric Needs Calculator.")
            return

        def find_col(name_hint):
            for col in self.df.columns:
                cl = col.lower()
                if name_hint in cl and 'dv' not in cl and '%' not in cl:
                    return col
            return None

        cal_col = find_col("calories")
        protein_col = find_col("protein")
        fat_col = find_col("fat")
        carb_col = find_col("carb")
        fiber_col = find_col("fiber")
        sugar_col = find_col("sugar")

        df_chain = self.df[self.df['Company'].str.lower() == chain.lower()].copy()

        for col in [cal_col, protein_col, fat_col, carb_col, fiber_col, sugar_col]:
            df_chain[col] = pd.to_numeric(df_chain[col], errors='coerce')
        for col in [cal_col, protein_col, fat_col, carb_col, fiber_col, sugar_col]:
            df_chain[col] = pd.to_numeric(df_chain[col], errors='coerce').abs()
        df_chain.dropna(subset=[cal_col, protein_col, fat_col, carb_col, fiber_col, sugar_col], inplace=True)

        # Filter out unrealistic or junk values
        df_chain = df_chain[
            (df_chain[cal_col] > 100) &
            (df_chain[protein_col] > 10) &
            (df_chain[fat_col] < 80)
        ]

        df_chain['HealthScore'] = (
            df_chain[protein_col] * 2 -
            df_chain[fat_col] * 1 -
            df_chain[sugar_col] * 1 +
            df_chain[fiber_col] * 1
        )

        df_chain = df_chain[~df_chain['Item'].str.lower().str.contains("drink|soda|coffee|juice|milk|packet|syrup|sauce")]
        df_chain.sort_values(by='HealthScore', ascending=False, inplace=True)

        meal_targets = [0.3 * tdee, 0.35 * tdee, 0.35 * tdee]
        meals = [[], [], []]
        totals = [(0, 0, 0) for _ in range(3)]
        used = set()

        for meal_idx in range(3):
            cal_limit = meal_targets[meal_idx]
            total_cals, total_prot, total_fat, total_carb = 0, 0, 0, 0
            for _, row in df_chain.iterrows():
                if row['Item'] in used:
                    continue
                if total_cals + row[cal_col] > cal_limit:
                    continue
                meals[meal_idx].append(row)
                used.add(row['Item'])
                total_cals += row[cal_col]
                total_prot += row[protein_col]
                total_fat += row[fat_col]
                total_carb += row[carb_col]
            totals[meal_idx] = (total_prot, total_fat, total_carb)

        self.result_text.delete("1.0", tk.END)
        for i, meal in enumerate(meals):
            self.result_text.insert(tk.END, f"\nMeal {i+1} Suggestions:\n")
            for item in meal:
                self.result_text.insert(tk.END, f"{item['Item']} – {item[cal_col]:.0f} cal\n")
                self.result_text.insert(tk.END, f"Protein: {item[protein_col]:.1f}g | Fat: {item[fat_col]:.1f}g | Carbs: {item[carb_col]:.1f}g\n")
            prot, fat, carb = totals[i]
            self.result_text.insert(tk.END, f"→ Meal Total: Protein: {prot:.1f}g | Fat: {fat:.1f}g | Carbs: {carb:.1f}g\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = NutritionApp(root)
    root.mainloop()
