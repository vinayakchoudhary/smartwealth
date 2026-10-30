from typing import Literal

from scipy.optimize import linprog

from core.validator import get_and_validate_investor_dict, get_and_validate_product_dict


def allocate_weights(amount: float, investor_data: dict, products:list[tuple[str, dict]]) -> list[float] | None:
    n = len(products)
    bounds = get_bounds(investor_data, products)
    A_ub, b_ub = get_A_and_b_matrix(investor_data, products)
    c = get_c_matrix(investor_data, products)
    A_eq, b_eq = [[1]*n], [1]
    res = linprog(
        c = c,
        A_ub = A_ub,
        b_ub = b_ub,
        A_eq = A_eq,
        b_eq = b_eq,
        bounds = bounds,
        method = 'highs'
    )
    return [max(0.0, float(x)) for x in res.x] if res.success else None



def get_bounds(investor_data:dict, products:list[tuple[str, dict]]) -> list[tuple[float, float]]:
    res = []
    max_lock_in = 0 if investor_data["preference"] == "no_lock_in" else investor_data["horizon_months"] 
    for product_id, product_data in products:
        if product_data["lock_in_months"] > max_lock_in or \
            (investor_data["preference"] == "avoid_equity" and product_data["asset_class"] == "equity"):
            res.append((0.0, 0.0))
        else:
            res.append((0.0, 0.4))
    return res



def get_A_and_b_matrix(investor_data:dict, products:list[tuple[str, dict]]) -> tuple[list[list[float]], list[float]]:
    A, b = [], []

    # Horizon-based allocation limits
    if investor_data["horizon_months"] <= 36:
        A.append(product_with_risk_scale(products, 1, 4, 5))
        b.append(0.1)
        A.append(product_with_risk_scale(products, -1, 1, 2))
        b.append(-0.7)
    elif investor_data["horizon_months"] <= 84:
        A.append(product_with_risk_scale(products, 1, 4, 5))
        b.append(0.3)
        A.append(product_with_risk_scale(products, -1, 1, 2))
        b.append(-0.45)
    else:
        A.append(product_with_risk_scale(products, 1, 4, 5))
        b.append(0.55)
        A.append(product_with_risk_scale(products, -1, 1, 2))
        b.append(-0.25)

    # Risk-tolerance preference
    risks = [product_data["risk_score"] for product_id, product_data in products]
    A.append(risks)
    b.append(investor_data["risk_tolerance_score"] + 0.25)
    return A, b
        






def product_with_risk_scale(products:list[tuple[str, dict]], sign:Literal[1, -1], *risk) -> list[int]:
    res = []
    for product_id, product_data in products:
        res.append(sign if product_data["risk_score"] in risk else 0)
    return res



# score_i = (return_i − expense_i) − risk_aversion_coefficient * volatility_proxy_i + tax_savings_factor
def get_c_matrix(investor_data:dict, products:list[tuple[str, dict]]) -> list[float]:
    res = []
    risk_aversion_coefficient = 0.05 if investor_data["preference"] == "high_growth" else 0.25 if investor_data["preference"] == "capital_protection" else 0.1 
    for product_id, product_data in products:
        score_i = product_data["assumed_annual_return"]
        score_i -= product_data["annual_expense_ratio"] * (3 if investor_data["preference"] == "low_cost" else 1)
        score_i -= risk_aversion_coefficient * product_data["volatility_proxy"] 
        score_i += 0.02 if "tax" in (product_data["category_description"] + product_data["product_name"]).lower() else 0.0
        res.append(-score_i) # as the library minimizes 
    return res


def main():
    investor = get_and_validate_investor_dict("investor_profiles.csv")[0]
    products = get_and_validate_product_dict("investment_products.csv")[0]
    for i in range(1, 13):
        l = allocate_weights(10_000, investor[f"INV{i:02}"], list(products.items()))
        print(l)
    
    
if __name__ == "__main__":
    main()

