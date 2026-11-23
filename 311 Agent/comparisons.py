"""
For comparative questions
"""

import os

import pandas as pd

from predictor import REPO_ROOT, format_duration, get_parser_categories
from preprocessing import _time_of_day

CSV_PATH = os.path.join(REPO_ROOT, 'dataset', 'cleaned_311.csv')

COLUMN_MAP = {
    'complaint_type': 'Problem (formerly Complaint Type)',
    'agency': 'Agency',
    'location_type': 'Location Type',
    'borough': 'Borough',
    'channel': 'Open Data Channel Type',
    'time_of_day': 'time_of_day',
    'day_type': 'day_type',
    'month': 'month',
}

BOROUGH_VALUES = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten island', 'unspecified']
TIME_OF_DAY_VALUES = ['night', 'morning', 'afternoon', 'evening']
DAY_TYPE_VALUES = ['weekday', 'weekend']
MONTH_VALUES = [
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december',
]


NON_HEADLINE_VALUES = {'unspecified', 'other', 'not specified', 'unknown'}

df = pd.read_csv(
    CSV_PATH,
    usecols=list(COLUMN_MAP.values())[:4] + ['Open Data Channel Type', 'Created Date', 'resolution_hours'],
    dtype={col: 'category' for col in list(COLUMN_MAP.values())[:4] + ['Open Data Channel Type']},
)
df['Created Date'] = pd.to_datetime(df['Created Date'])
df['time_of_day'] = df['Created Date'].dt.hour.map(_time_of_day).astype('category')
df['day_type'] = pd.Series(
    pd.Categorical(df['Created Date'].dt.dayofweek.map(lambda d: 'weekend' if d >= 5 else 'weekday'))
)
df['month'] = df['Created Date'].dt.month_name().str.lower().astype('category')


categories = get_parser_categories()
VALID_CATEGORIES = {
    'complaint_type': set(categories['complaint_type']),
    'agency': set(categories['agency']),
    'location_type': set(categories['location_type']),
    'borough': set(BOROUGH_VALUES),
    'channel': set(categories['open_data_channel_type']),
    'time_of_day': set(TIME_OF_DAY_VALUES),
    'day_type': set(DAY_TYPE_VALUES),
    'month': set(MONTH_VALUES),
}


def normalize_filter(category, value): # output from gemini
    if not value:
        return None
    v = value.strip().lower()
    return v if v in VALID_CATEGORIES[category] else None


def compare_resolution_times(
    group_by_filter: str,
    complaint_type: str | None = None,
    location_type: str | None = None,
    borough: str | None = None,
    agency: str | None = None,
    channel: str | None = None,
    time_of_day: str | None = None,
    day_type: str | None = None,
    month: str | None = None,
    group_values: list[str] | None = None,
    months_back: int | None = None,
    days_back: int | None = None,
) -> dict:
    """Compares historical resolution times across a chosen dimension.

    Args:
        group_by_filter: one of "borough", "agency", "complaint_type", "location_type", "channel", "time_of_day", "day_type", "month".
        complaint_type: optional filter, omit to include all.
        location_type: optional filter, omit to include all.
        borough: optional filter, omit to include all.
        agency: optional filter, omit to include all.
        channel: optional filter (how the complaint was submitted), omit to include all.
        time_of_day: optional filter ("night", "morning", "afternoon", "evening"), omit to include all.
        day_type: optional filter ("weekday" or "weekend"), omit to include all.
        month: optional filter (calendar month name), omit to include all.
        group_values: to compare specific named groups head-to-head (e.g. two agencies ot two boroughs)
        months_back: only include complaints from the most recent N months
        days_back: only include complaints from the most recent N days (use this
            instead of months_back for short windows, e.g. "the last 10 days")
    """
    if group_by_filter not in COLUMN_MAP:
        raise ValueError(f"group_by_filter must be one of {list(COLUMN_MAP)}, got {group_by_filter!r}")

    filters = {
        'complaint_type': normalize_filter('complaint_type', complaint_type),
        'agency': normalize_filter('agency', agency),
        'location_type': normalize_filter('location_type', location_type),
        'borough': normalize_filter('borough', borough),
        'channel': normalize_filter('channel', channel),
        'time_of_day': normalize_filter('time_of_day', time_of_day),
        'day_type': normalize_filter('day_type', day_type),
        'month': normalize_filter('month', month),
    }

    mask = pd.Series(True, index=df.index)
    for category, value in filters.items():
        if value is not None:
            mask &= df[COLUMN_MAP[category]] == value

    if months_back is not None:
        cutoff = df['Created Date'].max() - pd.DateOffset(months=months_back)
        mask &= df['Created Date'] >= cutoff

    if days_back is not None:
        cutoff = df['Created Date'].max() - pd.Timedelta(days=days_back)
        mask &= df['Created Date'] >= cutoff

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

    if group_values:
        wanted = {normalize_filter(group_by_filter, v) for v in group_values}
        wanted.discard(None)
        grouped = grouped[grouped['group'].isin(wanted)]

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
