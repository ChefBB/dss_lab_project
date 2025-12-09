import pyodbc
import csv
import os

# ============================================================
# 0) CONFIGURAZIONE DATABASE + PATH CSV
# ============================================================

SERVER = "131.114.50.57"
DATABASE = "Group_ID_8_DB"
USERNAME = "Group_ID_8"
PASSWORD = "CU83R89P"

CSV_DIR = r"C:\Users\Win10\OneDrive - Università degli Studi di Torino\Desktop\repo_dss\dss_lab_project\dataset\Assignment5_CSV"

# ⚠️ CARICHIAMO SOLO QUELLO CHE MANCA DAVVERO
TABLES = [
    ("DimLyrics.csv",         "DimLyrics"),
    ("DimSong.csv",           "DimSong"),
    ("FactParticipation.csv", "FactParticipation")
]


# ============================================================
# 1) CONNESSIONE AL DATABASE
# ============================================================

print("📡 Connessione al database SQL Server...")

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
cursor = conn.cursor()

print("✔ Connessione effettuata.\n")


# ============================================================
# 2) FUNZIONE: CONTROLLA SE UNA TABELLA È VUOTA
# ============================================================

def table_is_empty(table_name: str) -> bool:
    """
    Restituisce True se la tabella è vuota.
    Solleva errore se la tabella non esiste.
    """
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0


# ============================================================
# 3) FUNZIONE UNIVERSALE DI UPLOAD CSV
# ============================================================

def upload_csv_to_table(csv_filename: str, table_name: str):

    file_path = os.path.join(CSV_DIR, csv_filename)

    if not os.path.exists(file_path):
        print(f"❌ File {csv_filename} NON trovato! Salto {table_name}.\n")
        return

    # ⚠️ Se la tabella HA GIÀ DATI → NON ricarico
    try:
        if not table_is_empty(table_name):
            print(f"⏩ {table_name} contiene già dati → skip.\n")
            return
    except Exception as e:
        print(f"❌ Errore nel controllare {table_name}: {e}\n")
        return

    print(f"⬆ Caricamento {csv_filename} → {table_name}")

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        cols = next(reader)  # header
        placeholders = ",".join(["?"] * len(cols))
        query = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({placeholders})"

        inserted = 0
        skipped = 0

        for row in reader:
            clean_row = [None if v in ("NULL", "") else v for v in row]

            try:
                cursor.execute(query, clean_row)
                inserted += 1
            except Exception as e:
                skipped += 1
                print(f"⚠️ Riga saltata ({table_name}): {clean_row[:5]}...")
                print("   Motivo:", e)

    conn.commit()
    print(f"✔ {inserted} righe inserite in {table_name} (skipped: {skipped})\n")


# ============================================================
# 4) ESECUZIONE CARICAMENTO PER LE TABELLE MANCANTI
# ============================================================

for csv_file, table_name in TABLES:
    upload_csv_to_table(csv_file, table_name)

print("🎉 ASSIGNMENT 6 COMPLETATO CON SUCCESSO!")
cursor.close()
conn.close()
print("🔌 Connessione chiusa.")
