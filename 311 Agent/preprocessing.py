"""
Helper functions to map user input to known categories for complaint_type and location_type. If the user input is not in the known categories, it is mapped to 'other' (or 'not specified' for location_type).
It also derives time features (time_of_day, season, is_weekend) from the current time.
"""

from datetime import datetime


DEFAULT_OPEN_DATA_CHANNEL_TYPE = 'online'

SEASON_MAP = {
    12: 'winter', 1: 'winter', 2: 'winter',
    3: 'spring', 4: 'spring', 5: 'spring',
    6: 'summer', 7: 'summer', 8: 'summer',
    9: 'fall', 10: 'fall', 11: 'fall',
}


def _time_of_day(hour):
    if hour <= 5:
        return 'night'
    if hour <= 11:
        return 'morning'
    if hour <= 17:
        return 'afternoon'
    return 'evening'


def derive_time_features(now=None):
    now = now or datetime.now()
    return {
        'time_of_day': _time_of_day(now.hour),
        'season': SEASON_MAP[now.month],
        'is_weekend': int(now.weekday() >= 5),
    }


def merge(value, groups):
    for values, new_value in groups:
        if value in values:
            return new_value
    return value


COMPLAINT_TYPE_MERGES = [
    (['noise - house of worship', 'noise - commercial', 'noise - vehicle', 'noise - park', 'noise - street/sidewalk', 'noise - residential'], 'noise - general'),
    (['street sign - missing', 'street sign - damaged', 'street sign - dangling'], 'street sign'),
    (['highway sign - missing', 'highway sign - damaged', 'highway sign - dangling'], 'highway sign'),
    (["building marshal's office", 'building marshals office'], "building marshal's office"),
    (['hazardous material', 'hazardous materials'], 'hazardous materials'),
    (['electric', 'electrical'], 'electrical'),
]

LOCATION_TYPE_MERGES = [
    (['residential building/house', 'residential building'], 'residential building'),
    (['comercial', 'commercial'], 'commercial'),
    (['catch basin or sewer', 'catch basin/sewer'], 'catch basin/sewer'),
    (['mixed use building', 'mixed use'], 'mixed use'),
    (['parking lot/garage', 'parking lot or garage'], 'parking lot or garage'),
    (['subway station', 'subway'], 'subway'),
    (['other (explain below)', 'other (explain in complaint details)'], 'other (explain further)'),
    (['3+ family apt. building', '3+ family apartment building'], '3+ family apartment building'),
]


def clean_agency(raw):
    if not raw:
        return None
    return raw.lower().strip()


def clean_complaint_type(raw, known_categories):
    if not raw:
        return 'other'
    value = merge(raw.lower().strip(), COMPLAINT_TYPE_MERGES)
    return value if value in known_categories else 'other'


def clean_location_type(raw, known_categories):
    if not raw:
        return 'not specified'
    value = merge(raw.lower().strip(), LOCATION_TYPE_MERGES)
    return value if value in known_categories else 'other'


def clean_channel_type(raw, known_categories):
    if not raw:
        return DEFAULT_OPEN_DATA_CHANNEL_TYPE
    value = raw.lower().strip()
    return value if value in known_categories else DEFAULT_OPEN_DATA_CHANNEL_TYPE
