import csv
import pyodbc
import time

# ============================================================
# 1) FUNZIONE DI CONNESSIONE
# ============================================================

def connect():
    print(" Connessione al database...")
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=131.114.50.57;"
        "DATABASE=Group_ID_8_DB;"
        "UID=Group_ID_8;"
        "PWD=CU83R89P;"
    )
    print("✔ Connessione stabilita\n")
    return conn, conn.cursor()

conn, cursor = connect()


# ============================================================
# 2) SAFE EXECUTE (GESTIONE ERRORI 10053)
# ============================================================

def safe_execute(query, params=None, retry=True):
    global conn, cursor

    try:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)

    except pyodbc.OperationalError as e:
        if retry and "10053" in str(e):
            print(" Connessione persa, riconnessione...")
            time.sleep(1)
            conn, cursor = connect()
            return safe_execute(query, params, retry=False)
        else:
            raise


# ============================================================
# 3) FUNZIONI DI SUPPORTO
# ============================================================

def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def safe_int(v):
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except:
        return None


# ============================================================
# 4) LETTURA SOLO DEL CSV DimSong
# ============================================================

CSV_PATH = r"C:\Users\Win10\OneDrive - Università degli Studi di Torino\Desktop\repo_dss\dss_lab_project\dataset"

song_rows = read_csv(f"{CSV_PATH}\\DimSong.csv")
print("✔ CSV DimSong letto correttamente\n")


# ============================================================
# 5) MAPPA ALBUMKEY (SONG → ALBUM)
# ============================================================

def map_album_keys():
    cursor.execute("SELECT AlbumKey, AlbumID_Original FROM DimAlbum")
    return {orig: key for key, orig in cursor.fetchall()}

album_map = map_album_keys()


# ============================================================
# 6) CARICAMENTO SOLO DI DIMSONG
# ============================================================

def load_dim_song(rows, album_key_map):
    print(" Inizio caricamento DimSong...\n")
    count = 0

    for r in rows:
        album_key = album_key_map.get(r["AlbumID_Original"])

        safe_execute("""
            INSERT INTO DimSong
            (SongID_Original, SongTitle, DiscNumber, TrackNumber,
             DurationMS, Popularity, AlbumKey)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            r["SongID_Original"],
            r["SongTitle"],
            safe_int(r["DiscNumber"]),
            safe_int(r["TrackNumber"]),
            safe_int(r["DurationMS"]),
            safe_int(r["Popularity"]),
            album_key
        ))

        count += 1
        if count % 300 == 0:
            print(f"➡ {count} righe caricate...")
            conn.commit()

    conn.commit()
    print(f"✔ DimSong caricata correttamente ({count} righe)\n")


# ============================================================
# 7) ESECUZIONE SOLO DIMSONG
# ============================================================

load_dim_song(song_rows, album_map)

print("\n CARICAMENTO SOLO DIMSONG COMPLETATO ")
