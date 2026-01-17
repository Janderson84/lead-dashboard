"""
Configuration constants for the Lead Dashboard.
"""

# Account Executives - deals owned by these people = Demo Held
AES = [
    "Edgar",
    "Alfred",
    "Zach",
    "Zachary",
    "Vanessa",
    "David",
    "Pedro",
    "Gleidson",
    "Marysol",
    "Marc James",
    "Marc James Beauchamp",
]

# SC Code definitions
SC_CODES = {
    "SC1": {"name": "Meta", "include_default": True},
    "SC3": {"name": "Organic", "include_default": True},
    "SC5": {"name": "AI Demo", "include_default": False},
    "SC6": {"name": "AI Demo", "include_default": False},
    "No SC": {"name": "Unknown", "include_default": True},
}

# Default SC types to include in filter
DEFAULT_SC_INCLUDE = ["SC1", "SC3", "No SC"]

# Column name mappings from Pipedrive export
COLUMN_MAPPINGS = {
    "Deal - Title": "title",
    "Deal - Deal value": "deal_value",
    "Deal - Pipeline": "pipeline",
    "Deal - Status": "status",
    "Deal - Owner": "owner",
    "Person - Phone": "phone",
    "Deal - Deal created on": "created_date",
    "Person - Timezone": "timezone",
}

# Color palette
COLORS = {
    # Segment colors
    "AAA": "#2E86AB",
    "B-Tier": "#F6AE2D",
    "Non-Demo": "#E94F37",
    # SC Type colors
    "SC1": "#7B68EE",
    "SC3": "#3CB371",
    "SC5": "#DC143C",
    "SC6": "#DC143C",
    "No SC": "#808080",
    # Status colors
    "Won": "#28A745",
    "Lost": "#DC3545",
    "Open": "#FFC107",
}

# Heatmap color scale for Won %
HEATMAP_COLORSCALE = [
    [0.0, "#FF6B6B"],
    [0.4, "#FFE66D"],
    [1.0, "#4ECDC4"],
]
