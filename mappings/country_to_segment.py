"""
Country to segment tier mapping.
"""

COUNTRY_TO_SEGMENT = {
    # AAA Tier (Premium Markets)
    "USA": "AAA",
    "Canada": "AAA",
    "UK": "AAA",
    "Germany": "AAA",
    "France": "AAA",
    "Netherlands": "AAA",
    "Belgium": "AAA",
    "Switzerland": "AAA",
    "Austria": "AAA",
    "Ireland": "AAA",
    "Spain": "AAA",
    "Italy": "AAA",
    "Portugal": "AAA",
    "Denmark": "AAA",
    "Sweden": "AAA",
    "Norway": "AAA",
    "Finland": "AAA",
    "Iceland": "AAA",
    "Australia": "AAA",
    "New Zealand": "AAA",

    # B-Tier (Secondary Markets)
    "Poland": "B-Tier",
    "Czech Republic": "B-Tier",
    "Romania": "B-Tier",
    "Hungary": "B-Tier",
    "Slovakia": "B-Tier",
    "Croatia": "B-Tier",
    "Slovenia": "B-Tier",
    "Bulgaria": "B-Tier",
    "Estonia": "B-Tier",
    "Latvia": "B-Tier",
    "Lithuania": "B-Tier",
    "Singapore": "B-Tier",
    "Malaysia": "B-Tier",
    "Mexico": "B-Tier",
    "Brazil": "B-Tier",
    "Argentina": "B-Tier",
    "Chile": "B-Tier",
    "Colombia": "B-Tier",
    "Costa Rica": "B-Tier",
    "Panama": "B-Tier",
    "Peru": "B-Tier",
    "UAE": "B-Tier",
    "Saudi Arabia": "B-Tier",
    "Qatar": "B-Tier",
    "Israel": "B-Tier",
    "Jordan": "B-Tier",
    "Bahrain": "B-Tier",
    "Kuwait": "B-Tier",
    "Oman": "B-Tier",
    "Japan": "B-Tier",
    "South Korea": "B-Tier",
    "Hong Kong": "B-Tier",
    "Taiwan": "B-Tier",
    "South Africa": "B-Tier",
}


def get_segment(country: str) -> str:
    """Get segment tier for a country. Defaults to Non-Demo."""
    return COUNTRY_TO_SEGMENT.get(country, "Non-Demo")
