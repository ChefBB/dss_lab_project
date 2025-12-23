
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

print(" Loaded datasets")
print("  Artists:", len(artists))
print("  Tracks:", len(tracks))
print("  Participations:", len(parts))
print("  Dates:", len(dates))
print("  Geography:", len(geo))

# DimDate

def export_dim_date(dates: List[Dict[str, Any]]) -> None:
    with open(os.path.join(OUT_DIR, "DimDate.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["DateKey", "Year", "Month", "Day", "Season"])

        for d in dates:
            w.writerow([
                d["date_id"],
                d["year"],
                d["month"],
                d["day"],
                d["season"]
            ])

    print(" DimDate.csv written")

# DimArtistGeography

def export_dim_artist_geography(geo: List[Dict[str, Any]]) -> None:
    with open(os.path.join(OUT_DIR, "DimArtistGeography.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "GeoKey", "BirthPlace", "Province",
            "Region", "Country", "Latitude", "Longitude"
        ])

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

    print(" DimArtistGeography.csv written")

# DimArtist

def export_dim_artist(artists: List[Dict[str, Any]]) -> None:
    with open(os.path.join(OUT_DIR, "DimArtist.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "ArtistKey", "Name", "Gender", "BirthDate",
            "Nationality", "Description", "ActiveStart",
            "ActiveEnd", "Type", "GeoKey"
        ])

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

    print("DimArtist.csv written")

#  DimAlbum

def export_dim_album(tracks: List[Dict[str, Any]]) -> None:

    album_seen = {}

    for t in tracks:
        key = t["new_id_album"]
        if key not in album_seen:
            album_seen[key] = [
                t["album_name"],
                t["album_release_date"],
                t["album_type"]
            ]

    with open(os.path.join(OUT_DIR, "DimAlbum.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["AlbumKey", "AlbumName", "ReleaseDate", "AlbumType"])

        for k, row in album_seen.items():
            w.writerow([k] + row)

    print(" DimAlbum.csv written")

# DimLyrics

def export_dim_lyrics(tracks: List[Dict[str, Any]]) -> None:
    
    with open(os.path.join(OUT_DIR, "DimLyrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "LyricsKey", "Language", "Swear_IT", "Swear_EN",
            "Swear_IT_Words", "Swear_EN_Words", "NSentences",
            "NTokens", "CharPerToken", "AvgTokenPerClause",
            "Explicit", "LyricsText"
        ])

        for t in tracks:
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

    print("DimLyrics.csv written")

# DimSymphony

def export_dim_symphony(tracks: List[Dict[str, Any]]) -> None:

    with open(os.path.join(OUT_DIR, "DimSymphony.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "SymphonyKey", "BPM", "Rolloff", "Flux", "RMS",
            "Flatness", "SpectralComplexity", "Pitch", "Loudness"
        ])

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

    print(" DimSymphony.csv written")

# DimSong

def export_dim_song(tracks: List[Dict[str, Any]]) -> None:

    with open(os.path.join(OUT_DIR, "DimSong.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "SongKey", "Title", "DiscNumber", "TrackNumber",
            "DurationMs", "Popularity", "FeaturingArtists",
            "AlbumKey", "LyricsKey", "SymphonyKey", "Category"
        ])

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

    print("DimSong.csv written")

# FactParticipation

def export_fact_participation(tracks: List[Dict[str, Any]],parts: List[Dict[str, Any]]) -> None:
   
    track_index = {t["new_track_id"]: t for t in tracks}

    with open(os.path.join(OUT_DIR, "FactParticipation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["SongKey", "ArtistKey", "DateKey", "Streams1Month", "IsPrimary"])

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

    print(" FactParticipation.csv written")

# main

def main():
    export_dim_date(dates)
    export_dim_artist_geography(geo)
    export_dim_artist(artists)
    export_dim_album(tracks)
    export_dim_lyrics(tracks)
    export_dim_symphony(tracks)
    export_dim_song(tracks)
    export_fact_participation(tracks, parts)

    print("\n CSV files generated.")

if __name__ == "__main__":
    main()
