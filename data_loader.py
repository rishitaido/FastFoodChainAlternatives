import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_and_process_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = [col.strip().replace('\n', '').replace(' ', '_') for col in df.columns]

    features = ['Calories', 'Total_Fat(g)', 'Saturated_Fat(g)', 'Trans_Fat(g)', 
                'Cholesterol(mg)', 'Sodium_(mg)', 'Carbs(g)', 'Fiber(g)', 
                'Sugars(g)', 'Protein(g)']

    df[features] = df[features].apply(pd.to_numeric, errors='coerce')
    df.dropna(subset=features, inplace=True)

    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])

    return df, features
