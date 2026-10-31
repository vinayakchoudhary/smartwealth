import streamlit as st

from core.compute_data import (
    get_goal_projections,
    get_net_rors__risk_scores__volatility_proxys__expense_ratios,
    get_weights,
)
from core.draw_fig import draw_pie_chart
from core.validator import get_and_validate_investor_dict, get_and_validate_product_dict
from core.write_csv import write_allotment_csv, write_summary_csv


def main():
    st.title("Smart Wealth")
    investor_dict, investor_errors, investor_warnings = get_and_validate_investor_dict("investor_profiles.csv")
    product_dict, product_errors, product_warnings = get_and_validate_product_dict("investment_products.csv")
    product_list = list(product_dict.items())
    product_ids = [product_id for product_id, product_data in product_list]
    weights = get_weights(investor_dict, product_list)
    write_allotment_csv(investor_dict, product_ids, weights)
    net_rors, risk_scores, volatility_proxys, expense_ratios = get_net_rors__risk_scores__volatility_proxys__expense_ratios(investor_dict, product_dict, weights, product_ids)
    goal_projections = get_goal_projections(investor_dict, net_rors)
    write_summary_csv(investor_dict, net_rors, volatility_proxys, risk_scores, goal_projections, expense_ratios)
    if (len(investor_warnings) > 0):
        st.warning("Warnings for investor data:\n- " + "\n- ".join(investor_warnings))
    if (len(investor_errors) > 0):
        st.error("Errors in investor data:\n- " + "\n- ".join(investor_errors))
    if (len(product_warnings) > 0):
        st.warning("Warning for product data:\n- " + "\n- ".join(product_warnings))
    if (len(product_errors) > 0):
        st.warning("Errors in product data:\n- " + "\n- ".join(product_errors))
    failed_to_allot_investors = [k for k in weights if weights[k] is None]
    if len(failed_to_allot_investors) > 0:
        st.error("Failed to allot weights with given Constraints to:\n- " + "\n- ".join(failed_to_allot_investors))
    alloted_investors = [k for k in investor_dict if weights[k] is not None]
    selected_investor = st.selectbox("Choose an invester:", sorted(alloted_investors), index=None, placeholder="Select investor_id")
    if selected_investor:
        st.plotly_chart(draw_pie_chart(product_ids, weights[selected_investor], investor_dict[selected_investor]["existing_investment_inr"], investor_dict[selected_investor]["monthly_sip_inr"]), width="stretch")
        










if __name__ == "__main__":
    main()