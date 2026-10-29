from collections.abc import KeysView
from math import floor

from loader import get_investor_dict, get_monthly_return_dict, get_product_dict
from models import AllowedPreference, Investor, MonthlyReturn, Product
from pydantic import ValidationError


def get_and_validate_investor_dict(filename) -> tuple[dict, list[str], list[str]]:
    data = get_investor_dict(filename)
    errors, warnings = [], []
    for investor_id, investor_data in tuple(data.items()):
        try:
            Investor(investor_id=investor_id, **investor_data)
        except ValidationError as e:
            errors.append(f"investor_id {investor_id} invalid input found\n{e}")
            data.pop(investor_id) # safe as we iterate over the tupele
        else:
            horizon_months = float(investor_data["horizon_months"])
            if not horizon_months.is_integer():
                warnings.append(f"investor_id {investor_id}: has fractional horizon_months {horizon_months}, the model assumes it to be an integer, horizon months are taken as {floor(horizon_months)}")
            data[investor_id]["horizon_months"] = floor(horizon_months)

            if investor_data["preference"] and investor_data["preference"] not in AllowedPreference:
                warnings.append(f"investor_id {investor_id}: has preference {investor_data['preference']}, model only allows {AllowedPreference} as preferences, preference not considered ")
                investor_data["preference"] = None
            
            if investor_data["goal_amount_inr"] < 10_000:
                warnings.append(f"investor_id {investor_id}: consider checking units of goal_amount_inr(inr{investor_data['goal_amount_inr']})")

            if investor_data["goal_amount_inr"] <= investor_data["existing_investment_inr"]:
                
                warnings.append(f"investor_id {investor_id}: goal is already achieved")
            elif investor_data["goal_amount_inr"] <= investor_data["existing_investment_inr"] + investor_data["monthly_sip_inr"] * investor_data["horizon_months"]:
                warnings.append(f"investor_id {investor_id}: goal can be achieved without returns from the market")
    if len(data) == 0:
        errors.append("Fatal Error: There must be at least one investor")
    return (data, errors, warnings)




def get_and_validate_product_dict(filename) -> tuple[dict, list[str], list[str]]:
    data = get_product_dict(filename)
    errors, warnings = [], []
    safe_product_cnt = 0
    for product_id, product_data in tuple(data.items()):
        try:
            Product(product_id=product_id, **product_data)
        except ValidationError as e:
            errors.append(f"product_id {product_id} invalid input found\n{e}")
            data.pop(product_id)
        else:
            if product_data["risk_score"] < 3:
                safe_product_cnt += 1

            if product_data["assumed_annual_return"] > 0.5 or product_data["assumed_annual_return"] < -0.3:
                warnings.append(f"product_id={product_id}, assumed_annual_return={product_data['assumed_annual_return']}: ror is assumed to be a decimal not a percentage")
            if product_data["annual_expense_ratio"] > 0.03:
                warnings.append(f"product_id={product_id}, annual_expense_ratio={product_data['annual_expense_ratio']}: the ratio is assumed to be a decimal not a percentage")
            if product_data["volatility_proxy"] > 1.0:
                warnings.append(f"product_id={product_id}, volatility_proxy={product_data['volatility_proxy']}: volatility_proxy is assumed to be a decimal not a percentage")
            if product_data["annual_expense_ratio"] > product_data["assumed_annual_return"]:
                warnings.append(f"product_id {product_id}: annual_expense_ratio({product_data['annual_expense_ratio']}) is larger than assumed_annual_return({product_data['assumed_annual_return']})")
    
    if len(data) < 3:
        errors.append("Fatal Error: there must be at least 3 product available")
        data.clear()
    elif safe_product_cnt == 0:
        errors.append("Fatal Error: there must be at least one product with risk_score of 1 or 2")
        data.clear()
    return (data, errors, warnings)




def get_and_validate_monthly_return_dict(filename:str, products:KeysView[str]) -> tuple[dict, list[str], list[str]]:
    data = get_monthly_return_dict(filename)
    errors, warnings = [], []
    for product_id, product_data in tuple(data.items()):
        if product_id not in products:
            warnings.append(f"product_id {product_id}: not in main products csv and thus will not be considered")
            data.pop(product_id)
            continue
        for month, rate in tuple(product_data.items()):
            try:
                MonthlyReturn(product_id=product_id, month=month, monthly_return=rate)
            except ValidationError as e:            
                errors.append(f"product_id {product_id} month {month}: invalid input found\n{e}")
                data[product_id].pop(month)
            else:
                if abs(rate) > 0.3:
                    warnings.append(f"product_id={product_id}, month={month}, monthly_return={rate}: return is assumed to be a decimal not a percentage")

    return (data, errors, warnings)




if __name__ == "__main__":
    products = get_and_validate_product_dict("investment_products.csv")[0]
    print(get_and_validate_monthly_return_dict("synthetic_monthly_returns.csv", products.keys()))


    

