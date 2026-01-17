"""
Lead Analytics Dashboard - Main Application

A Streamlit dashboard for analyzing SalesCloser.ai lead performance
from Pipedrive CSV exports.
"""

import streamlit as st
import pandas as pd

from data_processing import (
    load_and_clean_csv,
    enrich_dataframe,
    calculate_metrics,
    calculate_summary_metrics,
)
from visualizations import (
    create_country_map,
    create_ae_bar_chart,
    create_ae_scatter,
    create_sc_funnel,
    create_ae_segment_heatmap,
    create_ae_sc_heatmap,
    create_country_sc_bar,
    display_kpi_row,
    format_metrics_table,
    get_column_config,
)
from config import DEFAULT_SC_INCLUDE, AES

# Page config
st.set_page_config(
    page_title="Lead Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Lead Analytics Dashboard")
st.caption("SalesCloser.ai Lead Performance Analysis")

# File upload
uploaded_file = st.file_uploader("Upload Pipedrive CSV Export", type="csv")

if uploaded_file is not None:
    # Load and process data
    with st.spinner("Processing data..."):
        df_raw = load_and_clean_csv(uploaded_file)
        df = enrich_dataframe(df_raw)

    # Sidebar filters
    st.sidebar.header("Filters")

    # Date range filter
    if "created_date" in df.columns and df["created_date"].notna().any():
        min_date = df["created_date"].min().date()
        max_date = df["created_date"].max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            df = df[
                (df["created_date"].dt.date >= date_range[0]) &
                (df["created_date"].dt.date <= date_range[1])
            ]

    # SC Type filter (SC5, SC6 unchecked by default)
    sc_types = sorted(df["sc_type"].unique().tolist())
    selected_sc = st.sidebar.multiselect(
        "SC Type",
        options=sc_types,
        default=[sc for sc in sc_types if sc in DEFAULT_SC_INCLUDE]
    )
    if selected_sc:
        df = df[df["sc_type"].isin(selected_sc)]

    # Pipeline filter
    if "pipeline" in df.columns:
        pipelines = sorted(df["pipeline"].dropna().unique().tolist())
        if pipelines:
            selected_pipelines = st.sidebar.multiselect(
                "Pipeline",
                options=pipelines,
                default=pipelines
            )
            if selected_pipelines:
                df = df[df["pipeline"].isin(selected_pipelines)]

    # Segment filter
    segments = ["AAA", "B-Tier", "Non-Demo"]
    available_segments = [s for s in segments if s in df["segment"].values]
    selected_segments = st.sidebar.multiselect(
        "Segment",
        options=available_segments,
        default=available_segments
    )
    if selected_segments:
        df = df[df["segment"].isin(selected_segments)]

    # AE filter
    ae_names = sorted([ae for ae in df["ae_name"].dropna().unique().tolist()])
    if ae_names:
        selected_aes = st.sidebar.multiselect(
            "Account Executive",
            options=ae_names,
            default=ae_names
        )

    # Check if we have data after filtering
    if len(df) == 0:
        st.warning("No data matches the selected filters. Please adjust your filter criteria.")
    else:
        # KPI Summary
        st.header("Summary")
        summary = calculate_summary_metrics(df)
        display_kpi_row(summary)

        st.divider()

        # Tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🌍 By Country",
            "👤 By AE",
            "📢 By SC Type",
            "👤×🎯 AE × Segment",
            "👤×📢 AE × SC Type",
            "🌍×📢 Country × SC Type"
        ])

        # Tab 1: By Country
        with tab1:
            st.subheader("Performance by Country")
            country_metrics = calculate_metrics(df, ["country", "segment"])

            if len(country_metrics) > 0:
                # Map
                fig_map = create_country_map(country_metrics)
                st.plotly_chart(fig_map, use_container_width=True)

                # Table
                with st.expander("📊 View Data Table", expanded=True):
                    table_df = format_metrics_table(country_metrics, ["country", "segment"])
                    st.dataframe(
                        table_df,
                        column_config=get_column_config(),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Download button
                    csv = table_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="country_metrics.csv",
                        mime="text/csv"
                    )

        # Tab 2: By AE
        with tab2:
            st.subheader("Performance by Account Executive")

            # Filter to AE-owned deals only
            df_ae = df[df["is_demo_held"]]

            if len(df_ae) > 0:
                ae_metrics = calculate_metrics(df_ae, ["ae_name"])

                col1, col2 = st.columns(2)
                with col1:
                    fig_bar = create_ae_bar_chart(ae_metrics)
                    st.plotly_chart(fig_bar, use_container_width=True)
                with col2:
                    fig_scatter = create_ae_scatter(ae_metrics)
                    st.plotly_chart(fig_scatter, use_container_width=True)

                with st.expander("📊 View Data Table", expanded=True):
                    table_df = format_metrics_table(ae_metrics, ["ae_name"])
                    # Remove columns not meaningful for AE view (all deals are held)
                    cols_to_drop = [c for c in ["No-Show %", "Booked"] if c in table_df.columns]
                    if cols_to_drop:
                        table_df = table_df.drop(columns=cols_to_drop)
                    st.dataframe(
                        table_df,
                        column_config=get_column_config(),
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = table_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="ae_metrics.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No demo-held deals in the selected data.")

        # Tab 3: By SC Type
        with tab3:
            st.subheader("Performance by Lead Source (SC Type)")
            sc_metrics = calculate_metrics(df, ["sc_type"])

            if len(sc_metrics) > 0:
                fig_funnel = create_sc_funnel(sc_metrics)
                st.plotly_chart(fig_funnel, use_container_width=True)

                with st.expander("📊 View Data Table", expanded=True):
                    table_df = format_metrics_table(sc_metrics, ["sc_type"])
                    st.dataframe(
                        table_df,
                        column_config=get_column_config(),
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = table_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="sc_type_metrics.csv",
                        mime="text/csv"
                    )

        # Tab 4: AE × Segment
        with tab4:
            st.subheader("AE × Segment Matrix")

            df_ae = df[df["is_demo_held"]]

            if len(df_ae) > 0:
                ae_seg_metrics = calculate_metrics(df_ae, ["ae_name", "segment"])

                if len(ae_seg_metrics) > 0:
                    # Pivot for heatmap
                    pivot = ae_seg_metrics.pivot(
                        index="ae_name",
                        columns="segment",
                        values="Won_Pct"
                    ).fillna(0)

                    # Reorder columns
                    segment_order = ["AAA", "B-Tier", "Non-Demo"]
                    pivot = pivot[[c for c in segment_order if c in pivot.columns]]

                    fig_heatmap = create_ae_segment_heatmap(pivot)
                    st.plotly_chart(fig_heatmap, use_container_width=True)

                    with st.expander("📊 View Data Table"):
                        table_df = format_metrics_table(ae_seg_metrics, ["ae_name", "segment"])
                        cols_to_drop = [c for c in ["No-Show %", "Booked"] if c in table_df.columns]
                        if cols_to_drop:
                            table_df = table_df.drop(columns=cols_to_drop)
                        st.dataframe(
                            table_df,
                            column_config=get_column_config(),
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.info("No demo-held deals in the selected data.")

        # Tab 5: AE × SC Type
        with tab5:
            st.subheader("AE × SC Type Matrix")

            df_ae = df[df["is_demo_held"]]

            if len(df_ae) > 0:
                ae_sc_metrics = calculate_metrics(df_ae, ["ae_name", "sc_type"])

                if len(ae_sc_metrics) > 0:
                    pivot = ae_sc_metrics.pivot(
                        index="ae_name",
                        columns="sc_type",
                        values="Won_Pct"
                    ).fillna(0)

                    fig_heatmap = create_ae_sc_heatmap(pivot)
                    st.plotly_chart(fig_heatmap, use_container_width=True)

                    with st.expander("📊 View Data Table"):
                        table_df = format_metrics_table(ae_sc_metrics, ["ae_name", "sc_type"])
                        cols_to_drop = [c for c in ["No-Show %", "Booked"] if c in table_df.columns]
                        if cols_to_drop:
                            table_df = table_df.drop(columns=cols_to_drop)
                        st.dataframe(
                            table_df,
                            column_config=get_column_config(),
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.info("No demo-held deals in the selected data.")

        # Tab 6: Country × SC Type
        with tab6:
            st.subheader("Country × SC Type Comparison")

            country_sc_metrics = calculate_metrics(df, ["country", "sc_type"])

            if len(country_sc_metrics) > 0:
                fig_bar = create_country_sc_bar(country_sc_metrics)
                st.plotly_chart(fig_bar, use_container_width=True)

                with st.expander("📊 View Data Table"):
                    table_df = format_metrics_table(country_sc_metrics, ["country", "sc_type"])
                    st.dataframe(
                        table_df,
                        column_config=get_column_config(),
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = table_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="country_sc_metrics.csv",
                        mime="text/csv"
                    )

else:
    st.info("👆 Upload a Pipedrive CSV export to get started.")

    with st.expander("Expected CSV Format"):
        st.markdown("""
        The CSV should contain these columns from Pipedrive:

        | Column Name | Description |
        |-------------|-------------|
        | `Deal - Title` | Contains SC codes (e.g., "John Deal SC3") |
        | `Deal - Deal value` | Numeric deal amount |
        | `Deal - Pipeline` | Pipeline name |
        | `Deal - Status` | Open, Won, or Lost |
        | `Deal - Owner` | Rep name (AE or SDR) |
        | `Person - Phone` | Phone with country prefix |
        | `Deal - Deal created on` | Date/time created |
        | `Person - Timezone` | IANA timezone string |
        """)

    with st.expander("About This Dashboard"):
        st.markdown("""
        **Key Logic:**

        - **No-Show Detection:** If Deal Owner is an AE → Demo Held; otherwise → No-Show
        - **SC Codes:** SC1 (Meta/Paid) and SC3 (Organic) included by default; SC5/SC6 (AI Demo) excluded
        - **Country Detection:** Uses timezone first, falls back to phone prefix
        - **Segments:** AAA (premium), B-Tier (secondary), Non-Demo (excluded from marketing)

        **Metrics:**

        - **Demos Booked:** Total count of deals
        - **No-Show %:** Deals not owned by an AE
        - **Demos Held:** Deals owned by an AE
        - **Won %:** Won deals / Demos Held
        - **Won Value:** Sum of deal values for won deals
        """)
