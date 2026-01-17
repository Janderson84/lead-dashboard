"""
Mappings module for country detection and segmentation.
"""

from .timezone_to_country import TIMEZONE_TO_COUNTRY
from .phone_to_country import parse_country_from_phone, CANADIAN_AREA_CODES, PHONE_PREFIX_TO_COUNTRY
from .country_to_segment import COUNTRY_TO_SEGMENT, get_segment

__all__ = [
    "TIMEZONE_TO_COUNTRY",
    "parse_country_from_phone",
    "CANADIAN_AREA_CODES",
    "PHONE_PREFIX_TO_COUNTRY",
    "COUNTRY_TO_SEGMENT",
    "get_segment",
]
