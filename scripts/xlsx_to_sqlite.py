"""Migriert Werke_aus_TEX.xlsx (Blatt 'LV-Katalog') nach data/werke.sqlite.

Einmalig auszufuehren, um die bestehende Excel-Tabelle in die relationale
Pflegedatenbank zu ueberfuehren. Danach ist werke.sqlite die Datenquelle;
die xlsx-Datei wird nicht mehr automatisch eingelesen.

Aufruf: python scripts/xlsx_to_sqlite.py
"""

import re
import sqlite3
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "Werke_aus_TEX.xlsx"
DB_PATH = ROOT / "db" / "werke.sqlite"

SCHEMA = """
CREATE TABLE personen (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE editionen (
    id   INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE  -- z.B. '1555-1' (Ersterscheinung)
);

CREATE TABLE quellen (
    id        INTEGER PRIMARY KEY,
    referenz  TEXT NOT NULL UNIQUE  -- z.B. 'GA 2 II,I 1' (Gesamtaufnahme)
);

CREATE TABLE werke (
    id               INTEGER PRIMARY KEY,
    lv_nummer        TEXT NOT NULL,      -- Rohwert, z.B. '3-2' oder '74 (IV)'
    lv_haupt         INTEGER NOT NULL,   -- numerischer Hauptteil, fuer Sortierung
    lv_unter         INTEGER,            -- numerischer Unterteil (NULL bei Haupteintrag)
    lv_teil          TEXT,               -- roemischer Teil-Zusatz, z.B. 'IV' bei '74 (IV)'
    titel            TEXT NOT NULL,
    stimmen          INTEGER,
    textprovenienz   TEXT,
    textdichter_id   INTEGER REFERENCES personen(id),
    edition_id       INTEGER REFERENCES editionen(id),
    quelle_id        INTEGER REFERENCES quellen(id)
);
"""

LV_PATTERN = re.compile(r"^(\d+)(?:-(\d+))?(?:\s*\(([IVXLC]+)\))?$")


def parse_lv(lv_raw: str) -> tuple[int, int | None, str | None]:
    match = LV_PATTERN.match(lv_raw.strip())
    if not match:
        raise ValueError(f"Unerwartetes LV-Format: {lv_raw!r}")
    haupt, unter, teil = match.groups()
    return int(haupt), (int(unter) if unter is not None else None), teil


def get_or_create_id(cache: dict, cursor: sqlite3.Cursor, table: str, column: str, value: str) -> int | None:
    value = value.strip() if value else ""
    if not value:
        return None
    if value in cache:
        return cache[value]
    cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
    cache[value] = cursor.lastrowid
    return cache[value]


def main() -> None:
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    sheet = wb["LV-Katalog"]

    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    cur = conn.cursor()

    personen_cache: dict[str, int] = {}
    editionen_cache: dict[str, int] = {}
    quellen_cache: dict[str, int] = {}

    row_count = 0
    haupteintrag_count = 0

    rows = sheet.iter_rows(min_row=2, values_only=True)
    for lv, titel, stimmen, ersterscheinung, textdichter, textprovenienz, gesamtaufnahme in rows:
        if lv is None and titel is None:
            continue  # leere Zeile ueberspringen
        lv_raw = str(lv).strip()
        lv_haupt, lv_unter, lv_teil = parse_lv(lv_raw)
        if lv_unter is None:
            haupteintrag_count += 1

        textdichter_id = get_or_create_id(personen_cache, cur, "personen", "name", textdichter or "")
        edition_id = get_or_create_id(editionen_cache, cur, "editionen", "code", str(ersterscheinung) if ersterscheinung else "")
        quelle_id = get_or_create_id(quellen_cache, cur, "quellen", "referenz", gesamtaufnahme or "")

        cur.execute(
            """
            INSERT INTO werke (lv_nummer, lv_haupt, lv_unter, lv_teil, titel, stimmen,
                                textprovenienz, textdichter_id, edition_id, quelle_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lv_raw,
                lv_haupt,
                lv_unter,
                lv_teil,
                (titel or "").strip(),
                int(stimmen) if stimmen not in (None, "") else None,
                (textprovenienz or "").strip() or None,
                textdichter_id,
                edition_id,
                quelle_id,
            ),
        )
        row_count += 1

    conn.commit()

    distinct_haupt = cur.execute("SELECT COUNT(DISTINCT lv_haupt) FROM werke").fetchone()[0]

    print(f"Werke importiert (alle Zeilen): {row_count}")
    print(f"davon Haupteintraege (ohne '-N'): {haupteintrag_count}")
    print(f"eindeutige LV-Hauptnummern:      {distinct_haupt}")
    print(f"Personen (Textdichter):   {len(personen_cache)}")
    print(f"Editionen (Ersterscheinung): {len(editionen_cache)}")
    print(f"Quellen (Gesamtaufnahme): {len(quellen_cache)}")

    conn.close()


if __name__ == "__main__":
    main()
