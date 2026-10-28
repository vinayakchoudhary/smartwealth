from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent # this is the main project folder
CSV_DIR = BASE_DIR / "data"


def get_product_csv(filename: str):
    df = pd.read_csv(CSV_DIR / filename).set_index("product_id")
    return df.to_dict(orient="index")

def get_inverstor_csv(filename: str):
    df = pd.read_csv(CSV_DIR / filename).set_index("investor_id")
    df['preference'] = df['preference'].astype(object).where(df['preference'].notna(), None)
    # replace Nan in preference with None
    return df.to_dict(orient="index")    

if __name__ == "__main__":
    print(get_product_csv("investment_products.csv"))
    print(get_inverstor_csv("investor_profiles.csv"))