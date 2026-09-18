"""Ergaenzt GND- und VIAF-Nummern fuer sicher identifizierte Textdichter.

Muss NACH xlsx_to_sqlite.py laufen (das legt die personen-Tabelle neu an).
Die Zuordnung wurde recherchiert (Wikidata, gegengeprueft gegen Name/Lebensdaten/
Beschreibung) und nur fuer eindeutige Treffer uebernommen. Unsichere/mehrdeutige
Faelle bleiben absichtlich ohne Normdaten.

Aufruf: python scripts/add_normdaten.py
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "werke.sqlite"

# name (exakt wie in personen.name) -> (gnd_id, viaf_id)
NORMDATEN: dict[str, tuple[str, str]] = {
    "Ant. Cossuuino (= Antonius Gosswin)": ("103895736", "49649283"),
    "Ariost": ("118503952", "71386455"),
    "Ariosto": ("118503952", "71386455"),
    "Asinari": ("1089648103", "88349997"),
    "B. Guarini": ("118698753", "54142932"),
    "B. Tasso": ("118867687", "54258258"),
    "Belleau": ("118658042", "12304848"),
    "Bembo": ("118658115", "54144140"),
    "C.Marot": ("118731122", "59086239"),
    "Cl. Marot": ("118731122", "59086239"),
    "Clément Marot": ("118731122", "59086239"),
    # Enthaelt eingebetteten Zeilenumbruch aus der TeX-Konvertierung, ist aber
    # ebenfalls eine Marot-Zuschreibung (Nachdichtung von Ps 130 Anfang).
    "Anfang von Ps 130, Nachdichtung von \nClement Marot": ("118731122", "59086239"),
    "Marot": ("118731122", "59086239"),
    "Fiamma": ("130088730", "88878886"),
    "Fiamme": ("130088730", "88878886"),
    "Gabriel Fiamma": ("130088730", "88878886"),
    "Fileno Cornazzani": ("130582816", "258804626"),
    "François I roi de France": ("118534947", "88805531"),
    "G. Guéroult": ("124384927", "202471443"),
    "G.Guéroult": ("124384927", "202471443"),
    "G. Pontano": ("118833324", "9919481"),
    "Gioseppo da Lucca (= Gioseffo Guami)": ("131967983", "49408169"),
    "Greiter": ("104059389", "61731997"),
    "Guidiccione": ("118719297", "88331"),
    "Hans Sachs": ("118604597", "61551907"),
    "Hätzer": ("118719823", "34445896"),
    "Iuo de Vento": ("128380144", "15037297"),
    "Jean Bouchet": ("104236116", "46755492"),
    "Johannes Agricola": ("118501070", "46803216"),
    "Knöpken": ("119731789", "151746467"),
    "Luigi Cassola": ("124707556", "56859607"),
    "M. d'Angoulême": ("118577719", "89797196"),
    "Manrrique": ("11878160X", "51692805"),
    "Martin Luther": ("118575449", "14773105"),
    "Massimo Troiano": ("122151763", "69802744"),
    "Melin de Saint Gelais": ("118750801", "64045845"),
    "Octavien de Saint Gelais": ("118829254", "51700679"),
    "Minturno": ("100214037", "29685362"),
    "Notker Balbulus": ("118588850", "27863792"),
    "Odo von Cluny": ("100955916", "59199545"),
    "Olivier de Magny": ("119035456", "46831090"),
    "Hymnus, Paulus Diaconus": ("118789961", "40174477"),
    "Petrarca": ("118593234", "39382430"),
    "Pibrac": ("120054981", "39467880"),
    "Pierre Grognet": ("1055570284", "297960191"),
    "Pierre de Ronsard": ("118602519", "61551687"),
    "Ronsard": ("118602519", "61551687"),
    "Reuchlin": ("118744658", "66542815"),
    "S. Brant": ("118514474", "29530930"),
    "Sannazaro": ("118794469", "87990970"),
    "Savonarola": ("118605933", "74117553"),
    "Seneca": ("118613200", "90637919"),
    "Stefano Tucci": ("124214169", "95293442"),
    "Tansillo": ("118801325", "22279481"),
    "Thomas von Aquin": ("118622110", "100910150"),
    "Vergil": ("118626574", "8194433"),
    "Horaz": ("118553569", "100227522"),
    "du Bellay": ("118527649", "39447168"),
    "Fulbert v. Chartres": ("118703528", "41811055"),
    "nach Villon": ("118627066", "7398349"),
}


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cols = {row[1] for row in cur.execute("PRAGMA table_info(personen)")}
    if "gnd_id" not in cols:
        cur.execute("ALTER TABLE personen ADD COLUMN gnd_id TEXT")
    if "viaf_id" not in cols:
        cur.execute("ALTER TABLE personen ADD COLUMN viaf_id TEXT")

    updated, missing = 0, []
    for name, (gnd, viaf) in NORMDATEN.items():
        result = cur.execute(
            "UPDATE personen SET gnd_id = ?, viaf_id = ? WHERE name = ?", (gnd, viaf, name)
        )
        if result.rowcount == 0:
            missing.append(name)
        else:
            updated += 1

    conn.commit()
    print(f"Normdaten gesetzt: {updated} von {len(NORMDATEN)}")
    if missing:
        print("Nicht in der Datenbank gefunden (Namensabweichung?):")
        for name in missing:
            print(f"  - {name}")
    conn.close()


if __name__ == "__main__":
    main()
