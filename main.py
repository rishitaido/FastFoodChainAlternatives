from data_loader import load_and_process_data
from health_score import compute_health_score, get_healthier_alternatives
from caloric_needs import calculate_bmr, calculate_tdee

if __name__ == "__main__":
    df, features = load_and_process_data("/Users/rishi/Projects Python/FastFoodChainAlternatives/FastFoodNutritionMenuV2.csv")
    df_scored = compute_health_score(df.copy(), features)

    # Example usage:
    item = "Cheeseburger"
    original, alternatives = get_healthier_alternatives(item, df, df_scored)
    print("Original Item:\n", original)
    if alternatives is not None:
        print("\nHealthier Alternatives:\n", alternatives)
    else:
        print("\nNo healthier alternatives found.")
