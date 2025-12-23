"""
Loads the CSV files produced by export_dw_csv.py into the SQL Server Data Warehouse.
"""

import pyodbc
import csv
import os
from typing import List, Tuple

# connection settings

SERVER = "131.114.50.57"
DATABASE = "Group_ID_8_DB"
USERNAME = "Group_ID_8"
PASSWORD = "CU83R89P"

# path settings

BASE_DIR = os.getcwd()
CSV_DIR = os.path.join(BASE_DIR, "dataset", "Assignment5_CSV")

#tables to load

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

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
cursor = conn.cursor()

# utility functions

def table_is_empty(table_name: str) -> bool:
    """
    Check if a database table is empty.

    Parameters
    ----------
    table_name : str
        Name of the table to check.

    Returns
    -------
    bool
        True if the table is empty or an error occurs, False otherwise.
    """
    try:
        # Execute a simple count query on the table
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        # Return True if count is zero
        return cursor.fetchone()[0] == 0
    except Exception:
        # Return True if the table does not exist or any error occurs
        return True


def cast_value(value, column_name: str):
    """
    Cast a value to the appropriate type based on the column.

    Parameters
    ----------
    value
        The value to cast.
    column_name : str
        The name of the column which determines casting rules.

    Returns
    -------
    any
        The casted value, or None if it is missing or invalid.
    """
    # Treat common missing indicators as None
    if value in ("", "NULL", "None", None):
        return None

    # Cast Streams1Month to integer
    if column_name == "Streams1Month":
        try:
            return int(float(value))
        except Exception:
            return None

    # Cast IsPrimary to integer
    if column_name == "IsPrimary":
        try:
            return int(value)
        except Exception:
            return None

    return value


def upload_csv_to_table(csv_file: str, table_name: str, batch_size: int = 500):
    """
    Upload a CSV file into a database table in batches.

    Parameters
    ----------
    csv_file : str
        Name of the CSV file to upload (located in CSV_DIR).
    table_name : str
        Target table in the database.
    batch_size : int, optional
        Number of rows to insert per batch (default 500).
    """
    file_path = os.path.join(CSV_DIR, csv_file)

    if not os.path.exists(file_path):
        print(f"File not found: {csv_file}")
        return

    # Skip if table already populated
    if not table_is_empty(table_name):
        print(f"Table {table_name} already populated — skipped.\n")
        return

    print(f"Loading {csv_file} → {table_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = next(reader)  # header row

        placeholders = ",".join(["?"] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        batch = []
        inserted = 0

        for row in reader:
            # Cast each value according to column type
            clean_row = [cast_value(v, columns[i]) for i, v in enumerate(row)]
            batch.append(clean_row)

            # Insert batch when reaching batch_size
            if len(batch) == batch_size:
                cursor.executemany(query, batch)
                conn.commit()
                inserted += len(batch)
                batch = []

        if batch:
            cursor.executemany(query, batch)
            conn.commit()
            inserted += len(batch)

    print(f"Inserted {inserted} rows into {table_name}\n")



for csv_file, table_name in TABLES:
    upload_csv_to_table(csv_file, table_name)