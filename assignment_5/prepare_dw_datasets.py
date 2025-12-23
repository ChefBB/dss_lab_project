
"""

This script prepares the datasets used in the Data Warehouse by:
- loading JSON files from dataset/correct_ids
- normalizing attributes and data types
- exporting cleaned datasets to dataset/cleaned_json

The script is meant to be executed once, after the exploratory notebook phase.
"""

import os
import json
import uuid
import argparse
from typing import Any, Dict, List, Optional
from collections import Counter

def get_parent_dir() -> str:
    return os.path.abspath(os.path.join(os.getcwd(), os.pardir))


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# LOAD / SAVE

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_all_json(input_dir: str) -> Dict[str, Any]:
    data = {}
    for fname in os.listdir(input_dir):
        if fname.endswith(".json"):
            data[fname] = load_json(os.path.join(input_dir, fname))
    return data

# cleaning 

MISSING = {None, "", " ", "none", "None", "null", "unknown", "Unknown"}


def clean_string(v: Any) -> Optional[str]:
    if v in MISSING:
        return None
    return str(v)


def to_int(v: Any) -> Optional[int]:
    if v in MISSING:
        return None
    try:
        return int(float(v))
    except Exception:
        return None


def to_float(v: Any) -> Optional[float]:
    if v in MISSING:
        return None
    try:
        return float(v)
    except Exception:
        return None


def list_to_string(v: Any) -> Optional[str]:
    if v in (None, "", []):
        return None
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)

# artists

def fix_artists_keys(artists: List[Dict[str, Any]]) -> None:
    """
    Fixes inconsistent attribute naming inherited from raw data 
    
    """
    for a in artists:
        if "active-end" in a:
            if "active_end" not in a and a["active-end"] not in MISSING:
                a["active_end"] = a["active-end"]
            a.pop("active-end", None)


def normalize_artists(artists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes artist records by:
    - cleaning textual attributes
    - enforcing numeric types on coordinates
    - keeping surrogate keys and foreign keys unchanged

    """
    normalized = []

    for a in artists:
        normalized.append({
            "new_id_artist": a.get("new_id_artist"),
            "id_author": a.get("id_author"),
            "name": clean_string(a.get("name")),
            "gender": clean_string(a.get("gender")),
            "birth_date": a.get("birth_date") if a.get("birth_date") not in MISSING else None,
            "birth_place": clean_string(a.get("birth_place")),
            "nationality": clean_string(a.get("nationality")),
            "description": clean_string(a.get("description")),
            "active_start": a.get("active_start") if a.get("active_start") not in MISSING else None,
            "active_end": a.get("active_end") if a.get("active_end") not in MISSING else None,
            "type": clean_string(a.get("type")),
            "geo_id": a.get("geo_id"),
            "province": clean_string(a.get("province")),
            "region": clean_string(a.get("region")),
            "country": clean_string(a.get("country")),
            "latitude": to_float(a.get("latitude")),
            "longitude": to_float(a.get("longitude")),
        })

    return normalized



#artists geography

def normalize_geo(geo: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes geographical records by:
    - cleaning textual fields
    - enforcing float type on latitude and longitude

    """
    normalized = []

    for g in geo:
        normalized.append({
            "geo_id": g.get("geo_id"),
            "birth_place": clean_string(g.get("birth_place")),
            "province": clean_string(g.get("province")),
            "region": clean_string(g.get("region")),
            "country": clean_string(g.get("country")),
            "latitude": to_float(g.get("latitude")),
            "longitude": to_float(g.get("longitude")),
        })

    return normalized

# date

def determine_season(month: int, day: int) -> str:
    """
    Determines the season based on month and day

    """
    if (month == 12 and day >= 21) or month in (1, 2) or (month == 3 and day <= 20):
        return "Winter"
    if (month == 3 and day >= 21) or month in (4, 5) or (month == 6 and day <= 20):
        return "Spring"
    if (month == 6 and day >= 21) or month in (7, 8) or (month == 9 and day <= 22):
        return "Summer"
    if (month == 9 and day >= 23) or month in (10, 11) or (month == 12 and day <= 20):
        return "Autumn"
    return "Unknown"


def normalize_dates(dates: List[Dict[str, Any]], default_year: int = 2016) -> List[Dict[str, Any]]:
    """
    Normalizes date records by:
    - enforcing integer types for year, month and day
    - assigning a default year when missing
    - handling incomplete dates conservatively
    - deriving the season attribute

    """
    normalized = []

    for d in dates:
        year = to_int(d.get("year")) or default_year
        month = to_int(d.get("month"))
        day = to_int(d.get("day"))

        if month is None and day is None:
            month, day = 1, 1
            season = "Unknown"
        else:
            if month is not None and day is None:
                day = 1
            if month is None:
                month = 1
                season = "Unknown"
            else:
                season = determine_season(month, day)

        normalized.append({
            "date_id": d.get("date_id"),
            "year": year,
            "month": month,
            "day": day,
            "season": season
        })

    return normalized

# songs / tracks

def normalize_tracks(tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes track records by:
    - enforcing numeric types on audio and popularity features
    - converting list-based attributes into comma-separated strings
    - normalizing empty lyrics as proper missing values
    - generating surrogate keys for Lyrics and Symphony only once

    """
    int_fields = [
        "disc_number", "track_number", "duration_ms",
        "n_sentences", "n_tokens", "year", "month", "day"
    ]

    float_fields = [
        "popularity", "avg_token_per_clause", "char_per_tok",
        "bpm", "flux", "rms", "rolloff", "flatness",
        "pitch", "spectral_complexity", "loudness",
        "streams@1month"
    ]

    for t in tracks:
        for f in int_fields:
            t[f] = to_int(t.get(f))

        for f in float_fields:
            t[f] = to_float(t.get(f))

        t["swear_IT_words"] = list_to_string(t.get("swear_IT_words"))
        t["swear_EN_words"] = list_to_string(t.get("swear_EN_words"))

        if t.get("lyrics") == "":
            t["lyrics"] = None

        if "LyricsKey" not in t or t.get("LyricsKey") in MISSING:
            t["LyricsKey"] = uuid.uuid4().hex

        if "SymphonyKey" not in t or t.get("SymphonyKey") in MISSING:
            t["SymphonyKey"] = uuid.uuid4().hex

    return tracks

# duplicate check

def count_duplicates(data: List[Dict[str, Any]], key: str) -> int:
    values = [d.get(key) for d in data if d.get(key) not in MISSING]
    return len(values) - len(set(values))

# main

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", default=get_parent_dir())
    args = parser.parse_args()

    base_dir = args.base_dir
    input_dir = os.path.join(base_dir, "dataset/correct_ids")
    output_dir = os.path.join(base_dir, "dataset/cleaned_json")

    ensure_dir(output_dir)

    raw = load_all_json(input_dir)

    artists = raw.get("artists.json", [])
    tracks = raw.get("tracks.json", [])
    geo = raw.get("geo.json", [])
    dates = raw.get("dates.json", [])
    participations = raw.get("participations.json", [])

    fix_artists_keys(artists)

    artists_clean = normalize_artists(artists)
    geo_clean = normalize_geo(geo)
    dates_clean = normalize_dates(dates)
    tracks_clean = normalize_tracks(tracks)

    participations_clean = participations  # no changes needed

    outputs = {
        "artists_clean.json": artists_clean,
        "geo_clean.json": geo_clean,
        "dates_clean.json": dates_clean,
        "tracks_clean.json": tracks_clean,
        "participations_clean.json": participations_clean,
    }

    for fname, data in outputs.items():
        save_json(os.path.join(output_dir, fname), data)
        print(f" Saved {fname} ({len(data)} records)")

    print("\nDuplicate check:")
    print("Artists:", count_duplicates(artists_clean, "new_id_artist"))
    print("Geo:", count_duplicates(geo_clean, "geo_id"))
    print("Dates:", count_duplicates(dates_clean, "date_id"))
    print("Tracks:", count_duplicates(tracks_clean, "new_track_id"))

    print("\n Dataset preparation completed successfully.")


if __name__ == "__main__":
    main()
