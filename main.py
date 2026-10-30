import csv

from core import allocator, validator


def main():
    investor_dict, investor_erros, investor_warnings = validator.get_and_validate_investor_dict("investor_profiles.csv")
    product_dict, product_errors, product_warnings = validator.get_and_validate_product_dict("investment_products.csv")
    product_list = list(product_dict.items())
    product_ids = [product_id for product_id, product_data in product_list]
    weights = get_weights(investor_dict, product_list)
    write_allotment_csv(investor_dict, product_ids, weights)
    net_rors = get_net_rors(investor_dict, product_dict, weights, product_ids)
    print(net_rors)
    
    

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
        writer = csv.writer(file)
        writer.writerow(first_line)
        writer.writerows(data)


def get_weights(investor_dict: dict[str, dict[str, str|float|None]], product_list:list[tuple[str, dict[str, str|float]]]) -> dict[str, list[float]]:
    weights = {}
    for investor_id, investor_data in investor_dict.items():
        investments, sip = investor_data["existing_investment_inr"], investor_data["existing_investment_inr"] # type: ignore , pydantics has already confirmed it to be a float 
        amount_for_weights = investments if investments > 0 and investments < sip else sip # type: ignore
        weights[investor_id] = allocator.allocate_weights(amount_for_weights, investor_data, product_list) # type: ignore
    return weights


def get_net_rors(investor_dict: dict[str, dict[str, str|float|None]], product_dict:dict[str, dict[str, str|float]], weights: dict[str, list[float]], product_ids: list[str]):
    net_rors = {}
    for investor_id in investor_dict:
        curr_net_ror = 0
        if not weights[investor_id]:
            net_rors[investor_id] = None
            continue
        for i, product_id in enumerate(product_ids):
            curr_net_ror += weights[investor_id][i] * (product_dict[product_id]["assumed_annual_return"] - product_dict[product_id]["annual_expense_ratio"]) # type: ignore
        net_rors[investor_id] = curr_net_ror
    return net_rors

if __name__ == "__main__":
    main()