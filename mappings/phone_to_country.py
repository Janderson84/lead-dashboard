"""
Phone prefix to country mapping and parsing functions.
"""

PHONE_PREFIX_TO_COUNTRY = {
    # North America (+1 handled separately with area codes)
    "+1": "USA",  # Default, use area code for Canada detection

    # Europe
    "+44": "UK",
    "+353": "Ireland",
    "+49": "Germany",
    "+33": "France",
    "+31": "Netherlands",
    "+32": "Belgium",
    "+41": "Switzerland",
    "+43": "Austria",
    "+34": "Spain",
    "+39": "Italy",
    "+351": "Portugal",
    "+352": "Luxembourg",
    "+45": "Denmark",
    "+46": "Sweden",
    "+47": "Norway",
    "+358": "Finland",
    "+354": "Iceland",
    "+48": "Poland",
    "+420": "Czech Republic",
    "+36": "Hungary",
    "+40": "Romania",
    "+359": "Bulgaria",
    "+385": "Croatia",
    "+386": "Slovenia",
    "+421": "Slovakia",
    "+372": "Estonia",
    "+371": "Latvia",
    "+370": "Lithuania",
    "+381": "Serbia",
    "+380": "Ukraine",
    "+7": "Russia",
    "+30": "Greece",
    "+90": "Turkey",

    # Middle East
    "+971": "UAE",
    "+966": "Saudi Arabia",
    "+974": "Qatar",
    "+972": "Israel",
    "+962": "Jordan",
    "+973": "Bahrain",
    "+965": "Kuwait",
    "+968": "Oman",
    "+961": "Lebanon",

    # Latin America
    "+52": "Mexico",
    "+55": "Brazil",
    "+54": "Argentina",
    "+56": "Chile",
    "+57": "Colombia",
    "+506": "Costa Rica",
    "+507": "Panama",
    "+51": "Peru",
    "+593": "Ecuador",
    "+591": "Bolivia",
    "+595": "Paraguay",
    "+598": "Uruguay",
    "+58": "Venezuela",
    "+502": "Guatemala",
    "+503": "El Salvador",
    "+504": "Honduras",
    "+505": "Nicaragua",

    # Caribbean
    "+1809": "Dominican Republic",
    "+1829": "Dominican Republic",
    "+1849": "Dominican Republic",
    "+1876": "Jamaica",
    "+53": "Cuba",
    "+509": "Haiti",

    # Asia Pacific
    "+81": "Japan",
    "+82": "South Korea",
    "+852": "Hong Kong",
    "+886": "Taiwan",
    "+65": "Singapore",
    "+60": "Malaysia",
    "+66": "Thailand",
    "+62": "Indonesia",
    "+63": "Philippines",
    "+84": "Vietnam",

    # South Asia
    "+91": "India",
    "+92": "Pakistan",
    "+880": "Bangladesh",
    "+94": "Sri Lanka",
    "+977": "Nepal",

    # China
    "+86": "China",

    # Oceania
    "+61": "Australia",
    "+64": "New Zealand",

    # Africa
    "+27": "South Africa",
    "+20": "Egypt",
    "+234": "Nigeria",
    "+254": "Kenya",
    "+233": "Ghana",
    "+212": "Morocco",
    "+213": "Algeria",
    "+216": "Tunisia",
}

# Canadian area codes for +1 number disambiguation
CANADIAN_AREA_CODES = {
    "204", "226", "236", "249", "250", "289", "306", "343", "365",
    "403", "416", "418", "431", "437", "438", "450", "506", "514",
    "519", "548", "579", "581", "587", "604", "613", "639", "647",
    "672", "705", "709", "778", "780", "782", "807", "819", "825",
    "867", "873", "902", "905"
}


def parse_country_from_phone(phone: str) -> str:
    """Extract country from phone number prefix."""
    if not phone:
        return None

    # Clean phone number
    phone = str(phone).strip().replace("'", "").replace(" ", "").replace("-", "")

    # Handle +1 (USA/Canada)
    if phone.startswith("+1") or (phone.startswith("1") and len(phone) >= 11):
        # Extract area code (digits 2-4 for +1, or 1-3 for 1)
        if phone.startswith("+1"):
            area_code = phone[2:5]
        else:
            area_code = phone[1:4]

        if area_code in CANADIAN_AREA_CODES:
            return "Canada"
        return "USA"

    # Check other prefixes (longest match first)
    for prefix in sorted(PHONE_PREFIX_TO_COUNTRY.keys(), key=len, reverse=True):
        if phone.startswith(prefix):
            return PHONE_PREFIX_TO_COUNTRY[prefix]

    return None
