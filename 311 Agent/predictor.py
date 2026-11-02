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

# Same order the model was trained on (feature_selection.ipynb / modeling.ipynb).
CATEGORICAL_COLS = [
    'Problem (formerly Complaint Type)', 'Agency', 'Location Type',
    'Open Data Channel Type', 'time_of_day', 'season',
]
FEATURE_COLS = CATEGORICAL_COLS + ['is_weekend']

encoder = joblib.load(ENCODER_PATH)
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

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
        'season': time_features['season'],
        'is_weekend': time_features['is_weekend'],
    }
    return pd.DataFrame([row], columns=FEATURE_COLS)


def predict_resolution_hours(query, now=None):
    row = build_feature_row(query, now=now)

    encoded = row.copy()
    encoded[CATEGORICAL_COLS] = encoder.transform(row[CATEGORICAL_COLS])
    for c in CATEGORICAL_COLS:
        encoded[c] = encoded[c].astype(int).astype('category')

    prediction = model.predict(encoded, num_iteration=model.best_iteration)[0]
    return max(float(prediction), 0.0)

def get_parser_categories():
    return {
        "complaint_type": KNOWN_CATEGORIES[
            "Problem (formerly Complaint Type)"
        ].tolist(),
        "agency": KNOWN_CATEGORIES["Agency"].tolist(),
        "location_type": KNOWN_CATEGORIES["Location Type"].tolist(),
        "open_data_channel_type": KNOWN_CATEGORIES[
            "Open Data Channel Type"
        ].tolist(),
    }

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
