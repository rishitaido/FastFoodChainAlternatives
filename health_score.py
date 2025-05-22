import numpy as np

def compute_health_score(df, features):
    health_weights = {
        'Calories': -1, 'Total_Fat(g)': -1, 'Saturated_Fat(g)': -1, 'Trans_Fat(g)': -1,
        'Cholesterol(mg)': -1, 'Sodium_(mg)': -1, 'Fiber(g)': 1, 'Protein(g)': 1
    }

    df['Health_Score'] = np.zeros(len(df))
    for feature, weight in health_weights.items():
        if feature in df.columns:
            df['Health_Score'] += df[feature] * weight
    return df

def get_healthier_alternatives(item_name, df_original, df_scored, top_n=3):
    item_data = df_original[df_original['Item'].str.contains(item_name, case=False, na=False)]
    if item_data.empty:
        return None, f"Item '{item_name}' not found."

    item_data = item_data.iloc[0]
    candidates = df_original[
        (df_original['Calories'] <= item_data['Calories']) &
        (df_original['Total_Fat(g)'] < item_data['Total_Fat(g)']) &
        (df_original['Sugars(g)'] < item_data['Sugars(g)']) &
        (df_original['Fiber(g)'] >= item_data['Fiber(g)']) &
        (df_original['Protein(g)'] > item_data['Protein(g)'])
    ]
    if candidates.empty:
        return item_data.to_frame().T, None

    top_indices = df_scored.loc[candidates.index].sort_values(by='Health_Score').head(top_n).index
    return item_data.to_frame().T, df_original.loc[top_indices]
