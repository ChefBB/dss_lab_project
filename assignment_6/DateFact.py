import pyodbc
import csv
import os


SERVER = "131.114.50.57"
DATABASE = "Group_ID_8_DB"
USERNAME = "Group_ID_8"
PASSWORD = "CU83R89P"

#path 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "dataset", "Assignment5_CSV")

# SOLO le tabelle droppate
TABLES = [
    ("DimDate.csv",           "DimDate"),
    ("FactParticipation.csv", "FactParticipation")
]

# connect to database

print("Connessione al database...")
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
cursor = conn.cursor()
print(" Connessione stabilita.\n")

# check if table is empty

def table_is_empty(table):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0] == 0
    except:
        return True

# casting function

def cast_value(value, col_name):
    
    if value in ("", "NULL", "None", None):
        return None

    
    if col_name == "Streams1Month":
        try:
            return int(float(value))   # gestisce "123", "123.0"
        except:
            return None

    
    if col_name == "IsPrimary":
        try:
            return int(value)
        except:
            return None

    
    return value

# upload function with casting

def upload_csv(filename, table_name):
    file_path = os.path.join(CSV_DIR, filename)

    if not os.path.exists(file_path):
        print(f" File mancante: {filename}")
        return

    if not table_is_empty(table_name):
        print(f" Tabella {table_name} già popolata → salto.\n")
        return

    print(f"⬆ Caricamento {filename} → {table_name}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        cols = next(reader)

        placeholders = ",".join(["?"] * len(cols))
        query = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({placeholders})"

        batch = []
        count = 0

        for row in reader:
            clean_row = [
                cast_value(v, cols[i])
                for i, v in enumerate(row)
            ]

            batch.append(clean_row)

            if len(batch) == 100:
                cursor.executemany(query, batch)
                conn.commit()
                count += len(batch)
                batch = []

        if batch:
            cursor.executemany(query, batch)
            conn.commit()
            count += len(batch)

    print(f"✔ Inserite {count} righe in {table_name}\n")

# esecuzione caricamento

print("INIZIO CARICAMENTO...\n")

for csv_file, table_name in TABLES:
    upload_csv(csv_file, table_name)

print(" ASSIGNMENT 6 COMPLETATO — DimDate + FactParticipation caricate")
