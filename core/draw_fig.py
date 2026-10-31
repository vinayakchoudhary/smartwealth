import pandas as pd
import plotly.express as px

from core.compute_data import get_total_investment_each_month


def draw_pie_chart_weigths(product_ids: list[str], weights: list[float], investment:float, sip:float):
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


def draw_line_graph_investments(ror:float, months:int, investments:float, sip:float, volatility_proxy): 
    months = int(months)
    data = {}
    data["Month"] = range(months + 1)
    for i, j in zip(["c", "b", "o"], ["Conservative Projection", "Base Projection", "Optimistic Projection"]):
        data[j] = get_total_investment_each_month(months, ror, investments, sip, volatility_proxy, i) # type: ignore
    df = pd.DataFrame(data)

    fig = px.line(
        df,
        x="Month",
        y=["Conservative Projection", "Base Projection", "Optimistic Projection"], 
        title="Investment Corpus for each Month",
        markers=True, 
        color_discrete_sequence=["#6366F1", "#10B981", "#F59E0B"], 
    )
    fig.update_traces(
        hovertemplate="Month: <b>%{x}</b><br>Investment Corpus: <b> %{y:,.0f} inr</b><extra></extra>"
    )
    fig.update_layout(
        height=750,
        hoverlabel={"bgcolor": "white", "font_size": 16, "font_color": "black"}, 
        legend_title_text="Case Taken",
        xaxis_title="Month",
        yaxis_title="Investment Corpus",
    )
    return fig
