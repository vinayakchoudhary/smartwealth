from core.compute_data import (
    get_goal_projections,
    get_net_rors__risk_scores__volatility_proxys__expense_ratios,
    get_weights,
)
from core.validator import get_and_validate_investor_dict, get_and_validate_product_dict
from core.write_csv import write_allotment_csv, write_summary_csv


def main():
    investor_dict, investor_erros, investor_warnings = get_and_validate_investor_dict("investor_profiles.csv")
    product_dict, product_errors, product_warnings = get_and_validate_product_dict("investment_products.csv")
    product_list = list(product_dict.items())
    product_ids = [product_id for product_id, product_data in product_list]
    weights = get_weights(investor_dict, product_list)
    write_allotment_csv(investor_dict, product_ids, weights)
    net_rors, risk_scores, volatility_proxys, expense_ratios = get_net_rors__risk_scores__volatility_proxys__expense_ratios(investor_dict, product_dict, weights, product_ids)
    goal_projections = get_goal_projections(investor_dict, net_rors)
    write_summary_csv(investor_dict, net_rors, volatility_proxys, risk_scores, goal_projections, expense_ratios)
    










if __name__ == "__main__":
    main()