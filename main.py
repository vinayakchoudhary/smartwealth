import csv

from core import allocator, validator


def main():
    investor_dict, investor_erros, investor_warnings = validator.get_and_validate_investor_dict("investor_profiles.csv")
    product_dict, product_errors, product_warnings = validator.get_and_validate_product_dict("investment_products.csv")
    product_list = list(product_dict.items())
    product_ids = [product_id for product_id, product_data in product_list]

    weights = {} 
    for investor_id, investor_data in investor_dict.items():
        investments, sip = investor_data["existing_investment_inr"], investor_data["existing_investment_inr"]
        amount_for_weights = investments if investments > 0 and investments < sip else sip
        weights[investor_id] = allocator.allocate_weights(amount_for_weights, investor_data, product_list)


    write_allotment_csv(investor_dict, product_ids, weights)

    # net_ror = 0
    # for weight, product in zip(weights, product_list):
    #     net_ror += weight * (product[1]["assumed_annual_return"] - product[1]["annual_expense_ratio"])
    
    

def write_allotment_csv(investor_dict: dict[str, dict], product_ids: list[str], weights: dict[str, list[float]]):
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
                line.extend([f"{weights[investor_id][i]:.4f}", f"{(weights[investor_id][i]*investments):.0f}", f"{(weights[investor_id][i]*sip):.0f}"])
        data.append(line)
    
    with open("allotment.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(first_line)
        writer.writerows(data)




    

if __name__ == "__main__":
    main()