"""
Turns a parsed Query into a resolution-time prediction: clean inputs -> encode -> model.predict().
"""

import os
import pickle

import joblib
import pandas as pd

from preprocessing import (
    clean_agency,
    clean_channel_type,
    clean_complaint_type,
    clean_location_type,
    derive_time_features,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCODER_PATH = os.path.join(REPO_ROOT, 'dataset', 'ordinal_encoder.joblib')
MODEL_PATH = os.path.join(REPO_ROOT, 'model', 'lightgbm_model.pkl')
MODEL_LOW_PATH = os.path.join(REPO_ROOT, 'model', 'model_low.pkl')
MODEL_HIGH_PATH = os.path.join(REPO_ROOT, 'model', 'model_high.pkl')

# Same order the model was trained on (feature_selection.ipynb / modeling.ipynb).
CATEGORICAL_COLS = [
    'Problem (formerly Complaint Type)', 'Agency', 'Location Type',
    'Open Data Channel Type', 'time_of_day',
]
FEATURE_COLS = CATEGORICAL_COLS + ['is_weekend']


def _load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


encoder = joblib.load(ENCODER_PATH)
model = _load_model(MODEL_PATH)
model_low = _load_model(MODEL_LOW_PATH)
model_high = _load_model(MODEL_HIGH_PATH)

# columns order guard
expected_feature_names = [c.replace(' ', '_') for c in FEATURE_COLS]
for m, label in [(model, 'model'), (model_low, 'model_low'), (model_high, 'model_high')]:
    if m.feature_name() != expected_feature_names:
        raise RuntimeError(
            f"{label}'s trained feature order {m.feature_name()} doesn't match "
            f"FEATURE_COLS {expected_feature_names} - predictions would be silently wrong"
        )

KNOWN_CATEGORIES = dict(zip(CATEGORICAL_COLS, encoder.categories_))


def build_feature_row(query, now=None):
    """query: the agent's Query object (or anything with the same attributes)."""
    time_features = derive_time_features(now)

    row = {
        'Problem (formerly Complaint Type)': clean_complaint_type(
            getattr(query, 'complaint_type', None),
            KNOWN_CATEGORIES['Problem (formerly Complaint Type)'],
        ),
        'Agency': clean_agency(getattr(query, 'agency', None)),
        'Location Type': clean_location_type(
            getattr(query, 'location_type', None),
            KNOWN_CATEGORIES['Location Type'],
        ),
        'Open Data Channel Type': clean_channel_type(
            getattr(query, 'open_data_channel_type', None),
            KNOWN_CATEGORIES['Open Data Channel Type'],
        ),
        'time_of_day': time_features['time_of_day'],
        'is_weekend': time_features['is_weekend'],
    }
    return pd.DataFrame([row], columns=FEATURE_COLS)


def encode_row(row):
    encoded = row.copy()
    encoded[CATEGORICAL_COLS] = encoder.transform(row[CATEGORICAL_COLS])
    for c in CATEGORICAL_COLS:
        encoded[c] = encoded[c].astype(int).astype('category')
    return encoded


def predict_one(m, encoded):
    return max(float(m.predict(encoded, num_iteration=m.best_iteration)[0]), 0.0)


def predict_resolution_hours(query, now=None):
    encoded = encode_row(build_feature_row(query, now=now))
    return predict_one(model, encoded)


def predict_resolution_range(query, now=None):
    """Returns (low, median, high) hours - the 10th/50th/90th percentile
    estimates from the three models"""
    encoded = encode_row(build_feature_row(query, now=now))
    low = predict_one(model_low, encoded)
    median = predict_one(model, encoded)
    high = predict_one(model_high, encoded)
    low, median, high = sorted([low, median, high])
    return low, median, high


def pluralize_s(n, unit):
    "1 unit -> 2 units"
    return f"{n} {unit}" if n == 1 else f"{n} {unit}s"


def format_duration(hours):
    """Converts raw hours into a readable format"""
    if hours < 1 / 60:
        return "less than a minute"

    minutes = round(hours * 60)
    #less than an hour
    if minutes < 60:
        return f"about {pluralize_s(minutes, 'minute')}"

    hrs = round(hours)
    # less than a day
    if hrs < 24:
        return f"about {pluralize_s(hrs, 'hour')}"

    days = round(hours / 24)
    #less than a week
    if days < 7:
        return f"about {pluralize_s(days, 'day')}"

    weeks = round(hours / (24 * 7))
    # less than a month
    if hours < 24 * 30:
        return f"about {pluralize_s(weeks, 'week')}"

    months = round(hours / (24 * 30))
    return f"about {pluralize_s(months, 'month')}"


def format_duration_range(low, high):
    """Formats each bound in its own natural unit rather than forcing a
    shared one - e.g. (22.6, 1423.6) becomes "about 23 hours to about 2
    months", not "about 0 to 2 months" (which a shared month-based unit
    would produce, silently hiding that the low end is really about a day)."""
    low_text = format_duration(low)
    high_text = format_duration(high)
    if low_text == high_text:
        return high_text
    return f"{low_text} to {high_text}"
