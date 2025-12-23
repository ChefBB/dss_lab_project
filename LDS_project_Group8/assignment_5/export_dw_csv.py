"""
This script generates the CSV files used to populate the Data Warehouse.
It takes as input the cleaned JSON datasets produced by prepare_dw_datasets.py
and exports one CSV per dimension and fact table.
"""

import json
import csv
import os
from typing import Dict, List, Any


# path settings

BASE_DIR = os.getcwd()

CLEAN_DIR = os.path.join(BASE_DIR, "dataset/cleaned_json")
OUT_DIR   = os.path.join(BASE_DIR, "dataset/Assignment5_CSV")

os.makedirs(OUT_DIR, exist_ok=True)

ARTISTS_PATH = os.path.join(CLEAN_DIR, "artists_clean.json")
TRACKS_PATH  = os.path.join(CLEAN_DIR, "tracks_clean.json")
PART_PATH    = os.path.join(CLEAN_DIR, "participations_clean.json")
DATES_PATH   = os.path.join(CLEAN_DIR, "dates_clean.json")
GEO_PATH     = os.path.join(CLEAN_DIR, "geo_clean.json")

# load datasets

def load_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


artists = load_json(ARTISTS_PATH)
tracks  = load_json(TRACKS_PATH)
parts   = load_json(PART_PATH)
dates   = load_json(DATES_PATH)
geo     = load_json(GEO_PATH)


# DimDate

def export_dim_date(dates: list):
    """
    Export the Date dimension table to a CSV file.

    Parameters
    ----------
    dates : list of dict
        List of date records.
    """
    # Open output CSV file for writing
    with open(os.path.join(OUT_DIR, "DimDate.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header row
        w.writerow(["DateKey", "Year", "Month", "Day", "Season"])

        # Write one row per date record
        for d in dates:
            w.writerow([
                d["date_id"],
                d["year"],
                d["month"],
                d["day"],
                d["season"]
            ])

# DimArtistGeography

def export_dim_artist_geography(geo: list):
    """
    Export the Artist Geography dimension table to a CSV file.

    Parameters
    ----------
    geo : list of dict
        List of geography records.
    """
    # Open output CSV file for writing
    with open(os.path.join(OUT_DIR, "DimArtistGeography.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header row
        w.writerow([
            "GeoKey", "BirthPlace", "Province",
            "Region", "Country", "Latitude", "Longitude"
        ])

        # Write one row per geography record
        for g in geo:
            w.writerow([
                g["geo_id"],
                g["birth_place"],
                g["province"],
                g["region"],
                g["country"],
                g["latitude"],
                g["longitude"]
            ])


# DimArtist

def export_dim_artist(artists: list):
    """
    Export the Artist dimension table to a CSV file.

    Parameters
    ----------
    artists : list of dict
        List of artist records.
    """
    # Open output CSV file for writing
    with open(os.path.join(OUT_DIR, "DimArtist.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header row
        w.writerow([
            "ArtistKey", "Name", "Gender", "BirthDate",
            "Nationality", "Description", "ActiveStart",
            "ActiveEnd", "Type", "GeoKey"
        ])

        # Write one row per artist
        for a in artists:
            w.writerow([
                a["new_id_artist"],
                a["name"],
                a["gender"],
                a["birth_date"],
                a["nationality"],
                a["description"],
                a["active_start"],
                a["active_end"],
                a["type"],
                a["geo_id"]
            ])


#  DimAlbum

def export_dim_album(tracks: list):
    """
    Export the Album dimension table to a CSV file.

    Parameters
    ----------
    tracks : list of dict
        List of track records.
    """
    # Dictionary used to keep unique albums by album key
    album_seen = {}

    # Extract unique albums from tracks
    for t in tracks:
        key = t["new_id_album"]
        if key not in album_seen:
            album_seen[key] = [
                t["album_name"],
                t["album_release_date"],
                t["album_type"]
            ]

    # Write Album dimension CSV
    with open(os.path.join(OUT_DIR, "DimAlbum.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header
        w.writerow(["AlbumKey", "AlbumName", "ReleaseDate", "AlbumType"])

        # Write one row per album
        for k, row in album_seen.items():
            w.writerow([k] + row)


# DimLyrics

def export_dim_lyrics(tracks: list):
    """
    Export the Lyrics dimension table to a CSV file.

    Parameters
    ----------
    tracks : list of dict
        List of track records.
    """
    # Open output CSV file for the Lyrics dimension
    with open(os.path.join(OUT_DIR, "DimLyrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header
        w.writerow([
            "LyricsKey", "Language", "Swear_IT", "Swear_EN",
            "Swear_IT_Words", "Swear_EN_Words", "NSentences",
            "NTokens", "CharPerToken", "AvgTokenPerClause",
            "Explicit", "LyricsText"
        ])

        # Write one row per track
        for t in tracks:
            # Convert boolean explicit flag to integer
            explicit_flag = 1 if t["explicit"] else 0

            w.writerow([
                t["LyricsKey"],
                t["language"],
                t["swear_IT"],
                t["swear_EN"],
                t["swear_IT_words"],
                t["swear_EN_words"],
                t["n_sentences"],
                t["n_tokens"],
                t["char_per_tok"],
                t["avg_token_per_clause"],
                explicit_flag,
                t["lyrics"]
            ])


# DimSymphony

def export_dim_symphony(tracks: list):
    """
    Export the Symphony dimension table to a CSV file.

    Parameters
    ----------
    tracks : list of dict
        List of track records.
    """
    # Open output CSV file for the Symphony dimension
    with open(os.path.join(OUT_DIR, "DimSymphony.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header
        w.writerow([
            "SymphonyKey", "BPM", "Rolloff", "Flux", "RMS",
            "Flatness", "SpectralComplexity", "Pitch", "Loudness"
        ])

        # Write one row per track
        for t in tracks:
            w.writerow([
                t["SymphonyKey"],
                t["bpm"],
                t["rolloff"],
                t["flux"],
                t["rms"],
                t["flatness"],
                t["spectral_complexity"],
                t["pitch"],
                t["loudness"]
            ])


# DimSong

def export_dim_song(tracks: list):
    """
    Export the Song dimension table to a CSV file.

    Parameters
    ----------
    tracks : list of dict
        List of track records.
    """
    # Open output CSV file for the Song dimension
    with open(os.path.join(OUT_DIR, "DimSong.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header
        w.writerow([
            "SongKey", "Title", "DiscNumber", "TrackNumber",
            "DurationMs", "Popularity", "FeaturingArtists",
            "AlbumKey", "LyricsKey", "SymphonyKey", "Category"
        ])

        # Write one row per track
        for t in tracks:
            w.writerow([
                t["new_track_id"],
                t["title"],
                t["disc_number"],
                t["track_number"],
                t["duration_ms"],
                t["popularity"],
                t["featured_artists"],
                t["new_id_album"],
                t["LyricsKey"],
                t["SymphonyKey"],
                t["category"]
            ])


# FactParticipation

def export_fact_participation(tracks: list, parts: list):
    """
    Export the Participation fact table to a CSV file.

    Parameters
    ----------
    tracks : list of dict
        List of track records.

    parts : list of dict
        List of participation records.
    """
    # Build a lookup dictionary for tracks by track ID
    track_index = {t["new_track_id"]: t for t in tracks}

    # Open output CSV file for the FactParticipation table
    with open(os.path.join(OUT_DIR, "FactParticipation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)

        # Write header row
        w.writerow(["SongKey", "ArtistKey", "DateKey", "Streams1Month", "IsPrimary"])

        # Write one row per participation record
        for p in parts:
            tr = track_index.get(p["new_track_id"])
            if tr:
                w.writerow([
                    p["new_track_id"],
                    p["new_id_artist"],
                    tr["date_id"],
                    tr["streams@1month"],
                    p["isPrimary"]
                ])


export_dim_date(dates)
export_dim_artist_geography(geo)
export_dim_artist(artists)
export_dim_album(tracks)
export_dim_lyrics(tracks)
export_dim_symphony(tracks)
export_dim_song(tracks)
export_fact_participation(tracks, parts)