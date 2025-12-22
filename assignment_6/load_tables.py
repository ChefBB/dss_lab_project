
"""

This script loads the CSV files produced by export_dw_csv.py
into the SQL Server Data Warehouse.

The loading order respects foreign key dependencies.
Each table is populated only if it is empty.

"""

import pyodbc
import csv
import os
from typing import List, Tuple

# database connection settings

SERVER = "131.114.50.57"
DATABASE = "Group_ID_8_DB"
USERNAME = "Group_ID_8"
PASSWORD = "CU83R89P"

BASE_DIR = os.getcwd()
CSV_DIR = os.path.join(BASE_DIR, "dataset/Assignment5_CSV")

# tables to load (in order)

TABLES: List[Tuple[str, str]] = [
    ("DimDate.csv",            "DimDate"),
    ("DimArtistGeography.csv", "DimArtistGeography"),
    ("DimArtist.csv",          "DimArtist"),
    ("DimAlbum.csv",           "DimAlbum"),
    ("DimLyrics.csv",          "DimLyrics"),
    ("DimSymphony.csv",        "DimSymphony"),
    ("DimSong.csv",            "DimSong"),
    ("FactParticipation.csv",  "FactParticipation"),
]

# connect to database

print("Connecting to SQL Server")

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
cursor = conn.cursor()

print("Connection established.\n")

# utility functions

def table_is_empty(table_name: str) -> bool:
    """
    Checks whether a database table is empty.
    If the table does not exist or an error occurs,
    it is treated as empty.

    """
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] == 0
    except Exception:
        return True


def upload_csv_to_table(csv_file: str, table_name: str, batch_size: int = 500) -> None:
    
    file_path = os.path.join(CSV_DIR, csv_file)

    if not os.path.exists(file_path):
        print(f"File not found: {csv_file}")
        return

    if not table_is_empty(table_name):
        print(f"Table {table_name} already populated — skipped.\n")
        return

    print(f" Loading {csv_file} → {table_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = next(reader)

        placeholders = ",".join(["?"] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        batch = []
        inserted = 0

        for row in reader:
            clean_row = [None if v in ("", "NULL") else v for v in row]
            batch.append(clean_row)

            if len(batch) == batch_size:
                cursor.executemany(query, batch)
                conn.commit()
                inserted += len(batch)
                batch = []

        if batch:
            cursor.executemany(query, batch)
            conn.commit()
            inserted += len(batch)

    print(f" Inserted {inserted} rows into {table_name}\n")

# main

def main():
    print(" Starting loading\n")

    for csv_file, table_name in TABLES:
        upload_csv_to_table(csv_file, table_name)

    print(" DW populated.")

if __name__ == "__main__":
    main()
