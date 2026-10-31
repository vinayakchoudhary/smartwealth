import pandas as pd
import plotly.express as px


def draw_pie_chart(product_ids: list[str], weights: list[float], investment:float, sip:float):
    existing_investment_inr = [investment * weight for weight in weights]
    monthly_sip_inr = [sip * weight for weight in weights]
    data = {"product_id": product_ids, "weightage": weights, "existing_investment_inr":existing_investment_inr, "monthly_sip_inr":monthly_sip_inr}
    df = pd.DataFrame(data)
    df = df[df["weightage"] > 0]
    fig = px.pie(
        df,
        values="weightage",
        names="product_id",
        title="Portfolio Allocation",
        custom_data=["existing_investment_inr", "monthly_sip_inr"],
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>"
        + " weightage: <b>%{percent}</b><br>"
        # + "existing_investment_inr: %{customdata[0][0]}<br>"
        + " existing_investment_inr: <b>%{customdata[0][0]:,.0f}</b><br>"
        + " jmonthly_sip_inr: <b>%{customdata[0][1]:,.0f}</b><br>"
    )
    return fig