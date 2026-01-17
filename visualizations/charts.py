"""
Chart creation functions using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import COLORS, HEATMAP_COLORSCALE


def create_country_map(df: pd.DataFrame) -> go.Figure:
    """
    Create choropleth map showing Won % by country.

    df should have columns: country, Won_Pct, Demos_Held, Won, Won_Value
    """
    # Create custom hover text
    df = df.copy()
    df["hover_text"] = df.apply(
        lambda row: (
            f"<b>{row['country']}</b><br>"
            f"Won Rate: {row['Won_Pct']:.1%}<br>"
            f"Demos Held: {int(row['Demos_Held']):,}<br>"
            f"Won: {int(row['Won']):,}<br>"
            f"Value: ${row['Won_Value']:,.0f}"
        ),
        axis=1
    )

    fig = go.Figure(data=go.Choropleth(
        locations=df["country"],
        locationmode="country names",
        z=df["Won_Pct"],
        text=df["hover_text"],
        hoverinfo="text",
        colorscale=[
            [0.0, "#dc3545"],      # Red - 0%
            [0.4, "#ffc107"],      # Yellow - 8%
            [0.6, "#28a745"],      # Green - 12%
            [1.0, "#155724"],      # Dark green - 20%+
        ],
        zmin=0,
        zmax=0.20,
        marker=dict(
            line=dict(color="#ffffff", width=0.5)
        ),
        colorbar=dict(
            title=dict(text="Won %", font=dict(size=14)),
            tickformat=".0%",
            tickvals=[0, 0.05, 0.10, 0.15, 0.20],
            ticktext=["0%", "5%", "10%", "15%", "20%"],
            len=0.6,
            thickness=15,
            x=1.02,
        ),
    ))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#cccccc",
            showland=True,
            landcolor="#f8f9fa",
            showocean=True,
            oceancolor="#e3f2fd",
            showlakes=True,
            lakecolor="#e3f2fd",
            showcountries=True,
            countrycolor="#dee2e6",
            countrywidth=0.5,
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
        ),
        height=550,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_ae_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create horizontal bar chart ranking AEs by Won %.

    df should have columns: ae_name or owner, Won_Pct, Demos_Held
    """
    # Determine column name
    name_col = "ae_name" if "ae_name" in df.columns else "owner"

    df_sorted = df.sort_values("Won_Pct", ascending=True)

    fig = px.bar(
        df_sorted,
        x="Won_Pct",
        y=name_col,
        orientation="h",
        text=df_sorted["Won_Pct"].apply(lambda x: f"{x:.1%}"),
        hover_data={"Demos_Held": True, "Won": True},
        color="Won_Pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 0.20],
        title="Won % by AE"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Won %",
        yaxis_title="",
        xaxis_tickformat=".0%",
        showlegend=False,
        height=400,
        coloraxis_showscale=False
    )

    return fig


def create_ae_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot: X = Demos Held (volume), Y = Won % (quality).

    Helps identify performance quadrants.
    """
    name_col = "ae_name" if "ae_name" in df.columns else "owner"

    fig = px.scatter(
        df,
        x="Demos_Held",
        y="Won_Pct",
        text=name_col,
        size="Won_Value",
        color="Won_Pct",
        color_continuous_scale="RdYlGn",
        range_color=[0, 0.20],
        hover_data={
            "Won": True,
            "Won_Value": ":$,.0f"
        },
        title="AE Performance: Volume vs Quality"
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(sizemin=10)
    )

    fig.update_layout(
        xaxis_title="Demos Held (Volume)",
        yaxis_title="Won % (Quality)",
        yaxis_tickformat=".0%",
        showlegend=False,
        height=400,
        coloraxis_showscale=False
    )

    # Add quadrant lines (median-based)
    if len(df) > 0:
        median_held = df["Demos_Held"].median()
        median_won = df["Won_Pct"].median()

        fig.add_hline(y=median_won, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_held, line_dash="dash", line_color="gray", opacity=0.5)

    return fig


def create_sc_funnel(df: pd.DataFrame) -> go.Figure:
    """
    Create funnel chart showing Booked -> Held -> Won for each SC type.

    df should have columns: sc_type, Demos_Booked, Demos_Held, Won
    """
    fig = go.Figure()

    sc_colors = {
        "SC1": COLORS.get("SC1", "#7B68EE"),
        "SC3": COLORS.get("SC3", "#3CB371"),
        "SC5": COLORS.get("SC5", "#DC143C"),
        "SC6": COLORS.get("SC6", "#DC143C"),
        "No SC": COLORS.get("No SC", "#808080")
    }

    for _, row in df.iterrows():
        sc_type = row["sc_type"]

        fig.add_trace(go.Funnel(
            name=sc_type,
            y=["Booked", "Held", "Won"],
            x=[row["Demos_Booked"], row["Demos_Held"], row["Won"]],
            textinfo="value+percent initial",
            marker=dict(color=sc_colors.get(sc_type, "#808080")),
            connector=dict(line=dict(color="gray", width=1))
        ))

    fig.update_layout(
        title="Lead Funnel by SC Type",
        height=400,
        showlegend=True
    )

    return fig


def create_ae_segment_heatmap(pivot_df: pd.DataFrame) -> go.Figure:
    """
    Create heatmap matrix: Rows = AEs, Columns = Segments, Values = Won %.

    pivot_df should be pivoted with AE as index, Segment as columns, Won_Pct as values.
    """
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Segment", y="AE", color="Won %"),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        color_continuous_scale=HEATMAP_COLORSCALE,
        zmin=0,
        zmax=0.25,
        text_auto=".1%",
        aspect="auto"
    )

    fig.update_layout(
        title="Won % by AE x Segment",
        height=500,
        xaxis_title="",
        yaxis_title=""
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b> x <b>%{x}</b><br>Won %%: %{z:.1%}<extra></extra>"
    )

    return fig


def create_ae_sc_heatmap(pivot_df: pd.DataFrame) -> go.Figure:
    """
    Create heatmap matrix: Rows = AEs, Columns = SC Types, Values = Won %.
    """
    fig = px.imshow(
        pivot_df,
        labels=dict(x="SC Type", y="AE", color="Won %"),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        color_continuous_scale=HEATMAP_COLORSCALE,
        zmin=0,
        zmax=0.25,
        text_auto=".1%",
        aspect="auto"
    )

    fig.update_layout(
        title="Won % by AE x SC Type",
        height=500,
        xaxis_title="",
        yaxis_title=""
    )

    return fig


def create_country_sc_bar(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """
    Create grouped bar chart: Countries on Y-axis, bars grouped by SC Type.

    df should have columns: country, sc_type, Won_Pct, Demos_Held
    """
    # Filter to top N countries by total demos held
    country_totals = df.groupby("country")["Demos_Held"].sum().nlargest(top_n)
    df_filtered = df[df["country"].isin(country_totals.index)]

    # Sort countries by total demos
    country_order = country_totals.index.tolist()

    fig = px.bar(
        df_filtered,
        x="Won_Pct",
        y="country",
        color="sc_type",
        orientation="h",
        barmode="group",
        text=df_filtered["Won_Pct"].apply(lambda x: f"{x:.1%}"),
        hover_data={"Demos_Held": True, "Won": True},
        color_discrete_map={
            "SC1": COLORS.get("SC1", "#7B68EE"),
            "SC3": COLORS.get("SC3", "#3CB371"),
            "SC5": COLORS.get("SC5", "#DC143C"),
            "SC6": COLORS.get("SC6", "#DC143C"),
            "No SC": COLORS.get("No SC", "#808080")
        },
        category_orders={"country": country_order},
        title=f"Won % by Country x SC Type (Top {top_n} Countries)"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Won %",
        yaxis_title="",
        xaxis_tickformat=".0%",
        legend_title="SC Type",
        height=500,
        bargap=0.2
    )

    return fig
