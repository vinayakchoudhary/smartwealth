from math import sqrt
from typing import Literal, cast

from core.allocator import allocate_weights


def get_weights(investor_dict: dict[str, dict[str, str|float|None]], product_list:list[tuple[str, dict[str, str|float]]]) -> dict[str, list[float]]:
    weights = {}
    for investor_id, investor_data in investor_dict.items():
        investments, sip = cast(float, investor_data["existing_investment_inr"]), cast(float, investor_data["monthly_sip_inr"]) 
        amount_for_weights = sip if investments == 0 or (sip > 0 and sip < investments) else investments
        weights[investor_id] = allocate_weights(amount_for_weights, investor_data, product_list)
    return weights


def get_net_rors__risk_scores__volatility_proxys__expense_ratios(investor_dict: dict[str, dict[str, str|float|None]], product_dict:dict[str, dict[str, str|float]], weights: dict[str, list[float]], \
product_ids: list[str]) -> tuple[dict[str,  float], dict[str, float], dict[str, float], dict[str, float]]:
    net_rors, risk_scores, volatility_proxys, expense_ratios = {},  {}, {}, {}
    for investor_id in investor_dict:
        if weights[investor_id] is None:
            net_rors[investor_id] = None
            risk_scores[investor_id] = None
            volatility_proxys[investor_id] = None
            expense_ratios[investor_id] = None
            continue
        net_rors[investor_id], risk_scores[investor_id], volatility_proxys[investor_id], expense_ratios[investor_id] = 0, 0, 0, 0
        for i, product_id in enumerate(product_ids):
            net_rors[investor_id] += weights[investor_id][i] * (cast(float, product_dict[product_id]["assumed_annual_return"]) - cast(float, product_dict[product_id]["annual_expense_ratio"]))
            risk_scores[investor_id] += weights[investor_id][i] * cast(float, product_dict[product_id]["risk_score"])
            volatility_proxys[investor_id] += weights[investor_id][i] * cast(float, product_dict[product_id]["volatility_proxy"])
            expense_ratios[investor_id] += weights[investor_id][i] * cast(float, product_dict[product_id]["annual_expense_ratio"])
    return net_rors, risk_scores, volatility_proxys, expense_ratios


# r = r_b + z * volitility_factor / (sqrt(12) * sprt(m))
def goal_projection(ror: float, months: int, investments: float, sip: float, case_taken: Literal["b", "o", "c"], volatility_proxy: float) -> float:
    if months == 0:
        return investments
    z = 1 if case_taken == "o" else -1 if case_taken == "c" else 0
    rm = ror / 12 + z * volatility_proxy / (sqrt(12) * sqrt(months))
    if (rm == 0):
        return investments + months * sip
    return investments*(1 + rm)**months + sip*((1 + rm)**months - 1)/rm
        


def get_goal_projections(investor_dict: dict[str, dict[str, str|float|None]], net_rors: dict[str, float]):
    goal_projections = {}
    for investor_id, investor_data in investor_dict.items():
        if net_rors[investor_id] is None:
            goal_projections[investor_id] = None    
        else:
            goal_projections[investor_id] = goal_projection(
                net_rors[investor_id], 
                int (cast(float, investor_data["horizon_months"])),  
                cast(float, investor_data["existing_investment_inr"]),
                cast(float, investor_data["monthly_sip_inr"]),
                "b", # volitility_proxy is not needed here 
                0,
            )  
    return goal_projections


def get_total_investment_each_month(months:int, ror: float, investments: float, sip: float, volatility_proxy: float, case_taken:Literal["o", "c", "b"]) -> list[float]:
    res = []
    for i in range(months + 1):
        res.append(goal_projection(ror, i, investments, sip, case_taken, volatility_proxy))
    return res;