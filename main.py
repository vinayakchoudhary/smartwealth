import streamlit as st

from core.compute_data import (
    get_goal_projections,
    get_net_rors__risk_scores__volatility_proxys__expense_ratios,
    get_weights,
)
from core.draw_fig import draw_line_graph_investments, draw_pie_chart_weigths
from core.validator import get_and_validate_investor_dict, get_and_validate_product_dict
from core.write_csv import write_allotment_csv, write_summary_csv


def main():
    st.title("Smart Wealth")
    st.set_page_config(
        page_title="Wealth",
        layout="wide",  # Options: "centered" or "wide"
    )
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
        col_init_investment, col_monthly_sip = st.columns(2)
        col_init_investment.metric("Existing Investment (inr)", f"{investor_dict[selected_investor]['existing_investment_inr']:,.0f}")
        col_monthly_sip.metric("Monthly SIP (inr)", f"{investor_dict[selected_investor]['monthly_sip_inr']:,.0f}")

        col_net_ror, col_expense_ratio = st.columns(2)
        col_net_ror.metric("Estimated Net Annual Rate of Return", f"{(net_rors[selected_investor]*100):.2f} %")
        col_expense_ratio.metric("Annual Expense Ratio", f"{(expense_ratios[selected_investor]*100):.2f} %")

        col_risk_score, col_volitility_proxy = st.columns(2)
        col_risk_score.metric("Weighted risk Score (out of 5)", f"{risk_scores[selected_investor]:.2f}")
        col_volitility_proxy.metric("Weighted Volitility Proxy", f"{volatility_proxys[selected_investor]:.3f}")
        
        col_goal_set, col_investment_projection= st.columns(2)
        goal = investor_dict[selected_investor]["goal_amount_inr"]
        projection = goal_projections[selected_investor]
        col_investment_projection.metric("Estimated Investment Corpus after Horizon Months", f"{projection:,.0f}")
        col_goal_set.metric("Goal Set (inr)", f"{goal:,.0f}")

        col_horizon_months, col_delta = st.columns(2)
        col_horizon_months.metric("Horizon Months", f"{investor_dict[selected_investor]['horizon_months']}")
        if projection >= goal:
            col_delta.metric("Surplus (inr)", f"{(projection - goal):,.0f}")
        else:
            col_delta.metric("Shortfall (inr)", f"{(goal - projection):,.0f}")






        st.plotly_chart(draw_pie_chart_weigths(product_ids, weights[selected_investor], investor_dict[selected_investor]["existing_investment_inr"], investor_dict[selected_investor]["monthly_sip_inr"]), width="stretch")
        st.plotly_chart(draw_line_graph_investments(net_rors[selected_investor], investor_dict[selected_investor]["horizon_months"],investor_dict[selected_investor]["existing_investment_inr"], \
            investor_dict[selected_investor]["monthly_sip_inr"], volatility_proxy=volatility_proxys[selected_investor]), width="stretch")
        










if __name__ == "__main__":
    main()