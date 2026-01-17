"""
Core data processing functions for the Lead Dashboard.
"""

import pandas as pd
import re
from config import AES, COLUMN_MAPPINGS
from mappings import TIMEZONE_TO_COUNTRY, parse_country_from_phone, get_segment


def load_and_clean_csv(uploaded_file):
    """Load CSV and standardize column names."""
    df = pd.read_csv(uploaded_file)

    # Rename columns using mapping
    rename_dict = {k: v for k, v in COLUMN_MAPPINGS.items() if k in df.columns}
    df = df.rename(columns=rename_dict)

    # Parse dates
    if "created_date" in df.columns:
        df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")

    # Clean deal value
    if "deal_value" in df.columns:
        df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce").fillna(0)

    return df


def extract_sc_code(title: str) -> str:
    """Extract SC code from deal title."""
    if not title or pd.isna(title):
        return "No SC"
    match = re.search(r"SC(\d+)", str(title), re.IGNORECASE)
    return f"SC{match.group(1)}" if match else "No SC"


def is_ae(owner: str) -> bool:
    """Check if deal owner is an Account Executive."""
    if not owner or pd.isna(owner):
        return False
    owner_lower = str(owner).lower().strip()
    for ae in AES:
        if ae.lower() in owner_lower:
            return True
    return False


def get_ae_name(owner: str) -> str:
    """Get standardized AE name from owner field."""
    if not owner or pd.isna(owner):
        return None
    owner_lower = str(owner).lower().strip()
    for ae in AES:
        if ae.lower() in owner_lower:
            return ae
    return None


def get_country(timezone: str, phone: str) -> str:
    """Derive country from timezone, falling back to phone prefix."""
    # Try timezone first
    if timezone and not pd.isna(timezone):
        tz_clean = str(timezone).strip()
        if tz_clean in TIMEZONE_TO_COUNTRY:
            return TIMEZONE_TO_COUNTRY[tz_clean]

    # Fall back to phone
    country = parse_country_from_phone(phone)
    if country:
        return country

    return "Unknown"


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns to dataframe."""
    df = df.copy()

    # Extract SC code
    df["sc_type"] = df["title"].apply(extract_sc_code)

    # Determine if demo was held (owner is AE)
    df["is_demo_held"] = df["owner"].apply(is_ae)

    # Get standardized AE name
    df["ae_name"] = df["owner"].apply(get_ae_name)

    # Derive country
    df["country"] = df.apply(
        lambda row: get_country(row.get("timezone"), row.get("phone")),
        axis=1
    )

    # Derive segment
    df["segment"] = df["country"].apply(get_segment)

    # Is won
    df["is_won"] = df["status"].str.lower() == "won"

    return df


def calculate_metrics(df: pd.DataFrame, group_cols: list) -> pd.DataFrame:
    """
    Calculate standard metrics grouped by specified columns.

    Returns dataframe with: Demos_Booked, No_Shows, NoShow_Pct,
    Demos_Held, Won, Won_Pct, Won_Value, Value_Per_Held
    """
    # Aggregate base metrics
    agg = df.groupby(group_cols, as_index=False).agg(
        Demos_Booked=("title", "count"),
        Demos_Held=("is_demo_held", "sum"),
        Won=("is_won", "sum"),
    )

    # Calculate Won_Value separately (sum of deal_value where is_won is True)
    won_value = df[df["is_won"]].groupby(group_cols, as_index=False).agg(
        Won_Value=("deal_value", "sum")
    )

    # Merge won value
    agg = agg.merge(won_value, on=group_cols, how="left")
    agg["Won_Value"] = agg["Won_Value"].fillna(0)

    # Calculate derived metrics
    agg["No_Shows"] = agg["Demos_Booked"] - agg["Demos_Held"]
    agg["NoShow_Pct"] = agg["No_Shows"] / agg["Demos_Booked"].replace(0, pd.NA)
    agg["Won_Pct"] = agg["Won"] / agg["Demos_Held"].replace(0, pd.NA)
    agg["Value_Per_Held"] = agg["Won_Value"] / agg["Demos_Held"].replace(0, pd.NA)

    # Fill NaN with 0
    agg = agg.fillna(0)

    return agg


def calculate_summary_metrics(df: pd.DataFrame) -> dict:
    """Calculate overall summary metrics."""
    demos_booked = len(df)
    demos_held = int(df["is_demo_held"].sum())
    no_shows = demos_booked - demos_held
    won = int(df["is_won"].sum())
    won_value = df.loc[df["is_won"], "deal_value"].sum() if "deal_value" in df.columns else 0

    return {
        "demos_booked": demos_booked,
        "demos_held": demos_held,
        "noshow_pct": no_shows / demos_booked if demos_booked > 0 else 0,
        "won": won,
        "won_pct": won / demos_held if demos_held > 0 else 0,
        "won_value": won_value,
    }


def filter_dataframe(
    df: pd.DataFrame,
    date_range: tuple = None,
    sc_types: list = None,
    pipelines: list = None,
    segments: list = None,
    aes: list = None,
) -> pd.DataFrame:
    """Apply filters to dataframe."""
    filtered = df.copy()

    if date_range and len(date_range) == 2 and "created_date" in filtered.columns:
        filtered = filtered[
            (filtered["created_date"].dt.date >= date_range[0]) &
            (filtered["created_date"].dt.date <= date_range[1])
        ]

    if sc_types:
        filtered = filtered[filtered["sc_type"].isin(sc_types)]

    if pipelines:
        filtered = filtered[filtered["pipeline"].isin(pipelines)]

    if segments:
        filtered = filtered[filtered["segment"].isin(segments)]

    if aes:
        filtered = filtered[filtered["ae_name"].isin(aes) | ~filtered["is_demo_held"]]

    return filtered
