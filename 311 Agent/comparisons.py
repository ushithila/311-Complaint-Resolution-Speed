"""
For comparative questions
"""

import os

import pandas as pd

from predictor import REPO_ROOT, format_duration, get_parser_categories

CSV_PATH = os.path.join(REPO_ROOT, 'dataset', 'cleaned_311.csv')

COLUMN_MAP = {
    'complaint_type': 'Problem (formerly Complaint Type)',
    'agency': 'Agency',
    'location_type': 'Location Type',
    'borough': 'Borough',
}

BOROUGH_VALUES = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten island', 'unspecified']


NON_HEADLINE_VALUES = {'unspecified', 'other', 'not specified'}

df = pd.read_csv(
    CSV_PATH,
    usecols=list(COLUMN_MAP.values()) + ['resolution_hours'],
    dtype={col: 'category' for col in COLUMN_MAP.values()},
)


categories = get_parser_categories()
VALID_CATEGORIES = {
    'complaint_type': set(categories['complaint_type']),
    'agency': set(categories['agency']),
    'location_type': set(categories['location_type']),
    'borough': set(BOROUGH_VALUES),
}


def normalize_filter(category, value): # output from gemini
    if not value:
        return None
    v = value.strip().lower()
    return v if v in VALID_CATEGORIES[category] else None


def compare_resolution_times(group_by_filter: str, complaint_type: str | None = None, location_type: str | None = None, borough: str | None = None, agency: str | None = None) -> dict:
    """Compares historical resolution times across boroughs, agencies, complaint types, or location types.

    Args:
        group_by_filter: one of "borough", "agency", "complaint_type", "location_type".
        complaint_type: optional filter, omit to include all.
        location_type: optional filter, omit to include all.
        borough: optional filter, omit to include all.
        agency: optional filter, omit to include all.
    """
    if group_by_filter not in COLUMN_MAP:
        raise ValueError(f"group_by_filter must be one of {list(COLUMN_MAP)}, got {group_by_filter!r}")

    filters = {
        'complaint_type': normalize_filter('complaint_type', complaint_type),
        'agency': normalize_filter('agency', agency),
        'location_type': normalize_filter('location_type', location_type),
        'borough': normalize_filter('borough', borough),
    }

    mask = pd.Series(True, index=df.index)
    for category, value in filters.items():
        if value is not None:
            mask &= df[COLUMN_MAP[category]] == value

    subset = df[mask]
    if subset.empty:
        return {'group_by': group_by_filter, 'filters': filters, 'results': []}

    grouped = (
        subset.groupby(COLUMN_MAP[group_by_filter], observed=True)['resolution_hours']
        .agg(median_hours='median', mean_hours='mean', count='count')
        .reset_index()
        .rename(columns={COLUMN_MAP[group_by_filter]: 'group'})
        .sort_values('median_hours')
    )
    grouped['median_hours'] = grouped['median_hours'].round(1)
    grouped['mean_hours'] = grouped['mean_hours'].round(1)
    grouped['count'] = grouped['count'].astype(int)

    return {
        'group_by': group_by_filter,
        'filters': filters,
        'results': grouped.to_dict(orient='records'),
    }


def format_comparison_message(result: dict) -> str:
    results = result['results']
    if not results:
        return "I couldn't find historical data matching that comparison."

    headline = [r for r in results if r['group'] not in NON_HEADLINE_VALUES] or results
    fastest, slowest = headline[0], headline[-1]

    if fastest['group'] == slowest['group']:
        return f"{fastest['group'].title()} resolves in {format_duration(fastest['median_hours'])}."

    return (
        f"{fastest['group'].title()} resolves fastest at {format_duration(fastest['median_hours'])}, "
        f"while {slowest['group'].title()} is slowest at {format_duration(slowest['median_hours'])}."
    )
