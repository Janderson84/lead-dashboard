"""
Table formatting and styling functions.
"""

import pandas as pd
import streamlit as st


def format_metrics_table(df: pd.DataFrame, group_cols: list) -> pd.DataFrame:
    """
    Format metrics dataframe for display with proper column names and formatting.
    """
    display_df = df.copy()

    # Build column list with proper naming
    col_name_map = {
        "country": "Country",
        "segment": "Segment",
        "owner": "AE",
        "ae_name": "AE",
        "sc_type": "SC Type",
    }

    columns = []

    # Add group columns
    for col in group_cols:
        if col in display_df.columns:
            new_name = col_name_map.get(col, col.title())
            if col != new_name:
                display_df[new_name] = display_df[col]
            columns.append(new_name)

    # Rename and format metric columns
    if "Demos_Booked" in display_df.columns:
        display_df["Booked"] = display_df["Demos_Booked"].astype(int)
        columns.append("Booked")

    if "NoShow_Pct" in display_df.columns:
        display_df["No-Show %"] = (display_df["NoShow_Pct"] * 100).round(1)
        columns.append("No-Show %")

    if "Demos_Held" in display_df.columns:
        display_df["Held"] = display_df["Demos_Held"].astype(int)
        columns.append("Held")

    if "Won" in display_df.columns:
        display_df["Won"] = display_df["Won"].astype(int)
        columns.append("Won")

    if "Won_Pct" in display_df.columns:
        display_df["Won %"] = (display_df["Won_Pct"] * 100).round(1)
        columns.append("Won %")

    if "Won_Value" in display_df.columns:
        display_df["Value"] = display_df["Won_Value"].round(0)
        columns.append("Value")

    if "Value_Per_Held" in display_df.columns:
        display_df["Value/Held"] = display_df["Value_Per_Held"].round(0)
        columns.append("Value/Held")

    # Select only the columns we want
    available_cols = [c for c in columns if c in display_df.columns]
    display_df = display_df[available_cols]

    return display_df


def get_column_config():
    """
    Get Streamlit column configuration for better table display.
    """
    return {
        "Booked": st.column_config.NumberColumn(
            "Booked",
            help="Total demos booked",
            format="%d",
        ),
        "Held": st.column_config.NumberColumn(
            "Held",
            help="Demos held (assigned to AE)",
            format="%d",
        ),
        "Won": st.column_config.NumberColumn(
            "Won",
            help="Deals won",
            format="%d",
        ),
        "No-Show %": st.column_config.NumberColumn(
            "No-Show %",
            help="No-show rate (lower is better)",
            format="%.1f %%",
        ),
        "Won %": st.column_config.NumberColumn(
            "Won %",
            help="Win rate",
            format="%.1f %%",
        ),
        "Value": st.column_config.NumberColumn(
            "Value",
            help="Total won value",
            format="$ %.0f",
        ),
        "Value/Held": st.column_config.NumberColumn(
            "Value/Held",
            help="Value per demo held",
            format="$ %.0f",
        ),
        "Country": st.column_config.TextColumn(
            "Country",
            width="medium",
        ),
        "Segment": st.column_config.TextColumn(
            "Segment",
            width="small",
        ),
        "AE": st.column_config.TextColumn(
            "AE",
            width="medium",
        ),
        "SC Type": st.column_config.TextColumn(
            "SC Type",
            width="small",
        ),
    }


def display_styled_table(df: pd.DataFrame, key: str = None):
    """
    Display a nicely styled data table using Streamlit's dataframe.
    """
    st.dataframe(
        df,
        column_config=get_column_config(),
        hide_index=True,
        use_container_width=True,
        key=key,
    )


def display_kpi_row(metrics: dict):
    """
    Display KPI summary row using Streamlit columns.
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Demos Booked",
            value=f"{metrics['demos_booked']:,}"
        )

    with col2:
        st.metric(
            label="No-Show %",
            value=f"{metrics['noshow_pct']:.1%}",
            delta=None,
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="Demos Held",
            value=f"{metrics['demos_held']:,}"
        )

    with col4:
        st.metric(
            label="Won %",
            value=f"{metrics['won_pct']:.1%}"
        )

    with col5:
        st.metric(
            label="Won Value",
            value=f"${metrics['won_value']:,.0f}"
        )
