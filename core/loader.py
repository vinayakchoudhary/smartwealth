from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent 
# this is the main project folder, this depends only on this file not the file in which the function is called 
CSV_DIR = BASE_DIR / "data"


def get_product_dict(filename: str) -> dict:
    df = pd.read_csv(CSV_DIR / filename).set_index("product_id")
    return df.to_dict(orient="index")

def get_investor_dict(filename: str) -> dict:
    df = pd.read_csv(CSV_DIR / filename).set_index("investor_id")
    df['preference'] = df['preference'].astype(object).where(df['preference'].notna(), None)
    # replace Nan in preference with None
    return df.to_dict(orient="index")    

def get_monthly_return_dict(filename: str) -> dict:
    df = pd.read_csv(CSV_DIR / filename)
    df = df.pivot(index="month", columns="product_id", values="monthly_return")
    # dict is made like col1:{r1Idx: value } and so on
    # this give us the dict {productId: {month: rate}}
    return df.to_dict()

if __name__ == "__main__":
    print(get_product_dict("investment_products.csv"))
    print(get_investor_dict("investor_profiles.csv"))
    print(get_monthly_return_dict("synthetic_monthly_returns.csv"))