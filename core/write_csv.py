from csv import writer
from typing import cast


def write_allotment_csv(investor_dict: dict[str, dict[str, str|float|None]], product_ids: list[str], weights: dict[str, list[float]]):
    first_line = ["investor_id", "existing_investment_inr", "monthly_sip_inr", "status"]
    for product_id in product_ids:
        first_line.extend([f"{product_id}_weight", f"{product_id}_existing_investment_inr", f"{product_id}_monthly_sip_inr"])
    data = []
    for investor_id, inverstor_data in investor_dict.items():
        investments, sip = inverstor_data["existing_investment_inr"], inverstor_data["monthly_sip_inr"]
        line = [investor_id, investments, sip]
        if weights[investor_id] == None:
            line.append("Error: Infeasible Constraints")   
            line.extend(["" for _ in range(3*len(product_ids))])
        else:
            line.append("Success: Allocated")
            for i, product_id in enumerate(product_ids):
                line.extend([f"{weights[investor_id][i]:.4f}", f"{(weights[investor_id][i]*investments):.0f}", f"{(weights[investor_id][i]*sip):.0f}"]) # type: ignore
        data.append(line)
    
    with open("allotment.csv", "w") as file:
        csv_writer = writer(file)
        csv_writer.writerow(first_line)
        csv_writer.writerows(data)



def write_summary_csv(investor_dict: dict[str, dict[str, str|float|None]], net_rors: dict[str, float], volatility_proxys: dict[str, float], risk_scores: dict[str, float], \
    goal_projections: dict[str, float], expense_ratios: dict[str, float]):
    # pending -> liquidity, warnings 
    data = [["investor_id", "existing_investment_inr", "monthly_sip_inr", "status", "assumed_net_annual_return", "annual_expense_ratios", "volatility_proxy", \
        "risk_score", "projected_amount_inr", "goal_amount_inr", "goal_status", "estimated_surplus_or_shortfall_inr"]]
    for investor_id, inverstor_data in investor_dict.items():
        line = [investor_id, inverstor_data["existing_investment_inr"], inverstor_data["monthly_sip_inr"]]
        if net_rors[investor_id] == None:
            data.append(line + ["Error: Infeasible Constraints"] + [""]*8)
        else:
            line.extend(["Success: Allocated", f"{net_rors[investor_id]:.4f}", f"{expense_ratios[investor_id]:.4f}", f"{volatility_proxys[investor_id]:.3f}", \
                f"{risk_scores[investor_id]:.2f}", f"{goal_projections[investor_id]:.0f}", f"{inverstor_data['goal_amount_inr']:.0f}"])
            line.append("Achievable" if goal_projections[investor_id] >= cast(float, inverstor_data["goal_amount_inr"]) else "Not Achievable")
            data.append(line + [f"{(goal_projections[investor_id] - cast(float, inverstor_data['goal_amount_inr'])):.0f}"])

    with open("summary.csv", "w") as file:
        csv_writer = writer(file)
        csv_writer.writerows(data)
