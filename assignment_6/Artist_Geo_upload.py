
import pyodbc
import csv
import os
from typing import List, Tuple

# =====================================================================
# DATABASE CONNECTION SETTINGS
# =====================================================================

SERVER = "131.114.50.57"
DATABASE = "Group_ID_8_DB"
USERNAME = "Group_ID_8"
PASSWORD = "CU83R89P"

# =====================================================================
# PATH CONFIGURATION (RELATIVE TO PROJECT ROOT)
# =====================================================================


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "dataset", "Assignment5_CSV")

# =====================================================================
# TABLES TO LOAD (FK ORDER)
# =====================================================================

TABLES: List[Tuple[str, str]] = [
    ("DimArtistGeography.csv", "DimArtistGeography"),
    ("DimArtist.csv",          "DimArtist"),
]

# =====================================================================
# CONNECT TO DATABASE
# =====================================================================

print("Connecting to SQL Server...")

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
cursor = conn.cursor()

print("Connection established.\n")

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def table_is_empty(table_name: str) -> bool:
  
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] == 0
    except Exception:
        return True


def upload_csv_to_table(csv_file: str, table_name: str, batch_size: int = 500) -> None:
  

    file_path = os.path.join(CSV_DIR, csv_file)

    if not os.path.exists(file_path):
        print(f" File not found: {csv_file}")
        return

    if not table_is_empty(table_name):
        print(f" Table {table_name} already populated — skipped.\n")
        return

    print(f"Loading {csv_file} → {table_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = next(reader)

        placeholders = ",".join(["?"] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"

        batch = []
        inserted = 0

        for row in reader:
            clean_row = [
                None if v in ("", "NULL", "None") else v
                for v in row
            ]

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

# =====================================================================
# MAIN
# =====================================================================

def main():
    print("Starting Artist & Geography loading...\n")

    for csv_file, table_name in TABLES:
        upload_csv_to_table(csv_file, table_name)

    print("DimArtistGeography and DimArtist loaded successfully.")

if __name__ == "__main__":
    main()
