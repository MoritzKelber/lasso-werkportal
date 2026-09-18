"""Exportiert data/werke.sqlite in die von der Website benoetigten Formate.

Wird bei jedem Build (lokal und in GitHub Actions) ausgefuehrt und erzeugt:
  - data/werke.json   -> Eingabedaten fuer die Hugo-Website (Tabelle/Suche)
  - static/werke.ttl   -> RDF/Turtle-Export (Dublin Core) fuer Linked-Open-Data
  - data/werke.sql     -> lesbarer SQL-Dump, damit Datenaenderungen in Git als
                           Textdiff sichtbar bleiben (werke.sqlite selbst ist binaer)

Aufruf: python scripts/export.py
"""

import json
import sqlite3
from pathlib import Path

from rdflib import DCTERMS, OWL, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

GND = Namespace("https://d-nb.info/gnd/")
VIAF = Namespace("https://viaf.org/viaf/")

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "werke.sqlite"
JSON_PATH = ROOT / "data" / "werke.json"
SQL_DUMP_PATH = ROOT / "db" / "werke.sql"
TTL_PATH = ROOT / "static" / "werke.ttl"

SITE_BASE = "https://moritzkelber.github.io/lasso-werkportal/"
LASSO = Namespace(SITE_BASE + "vocab/")
WERK = Namespace(SITE_BASE + "werke/")

QUERY = """
SELECT
    w.id, w.lv_nummer, w.lv_haupt, w.lv_unter, w.lv_teil, w.titel, w.stimmen,
    w.textprovenienz, p.name AS textdichter, p.gnd_id AS textdichter_gnd,
    p.viaf_id AS textdichter_viaf, e.code AS edition, q.referenz AS quelle
FROM werke w
LEFT JOIN personen  p ON p.id = w.textdichter_id
LEFT JOIN editionen e ON e.id = w.edition_id
LEFT JOIN quellen   q ON q.id = w.quelle_id
ORDER BY w.lv_haupt, w.lv_unter IS NOT NULL, w.lv_unter
"""


def fetch_werke(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(QUERY)]


def write_json(werke: list[dict]) -> None:
    JSON_PATH.parent.mkdir(exist_ok=True)
    JSON_PATH.write_text(json.dumps(werke, ensure_ascii=False, indent=2), encoding="utf-8")


def write_sql_dump(conn: sqlite3.Connection) -> None:
    SQL_DUMP_PATH.write_text("\n".join(conn.iterdump()), encoding="utf-8")


def write_ttl(werke: list[dict]) -> None:
    g = Graph()
    g.bind("dcterms", DCTERMS)
    g.bind("lasso", LASSO)

    for werk in werke:
        # Werk-URI entspricht der Detailseiten-URL auf der Website (/werke/<id>/).
        subject = URIRef(WERK[str(werk["id"])])
        g.add((subject, RDF.type, LASSO.Werk))
        g.add((subject, DCTERMS.identifier, Literal(werk["lv_nummer"])))
        g.add((subject, DCTERMS.title, Literal(werk["titel"], lang="it")))
        if werk["textdichter"]:
            if werk["textdichter_gnd"]:
                person = URIRef(GND[werk["textdichter_gnd"]])
                g.add((subject, DCTERMS.creator, person))
                g.add((person, RDF.type, LASSO.Textdichter))
                g.add((person, DCTERMS.identifier, Literal(werk["textdichter"])))
                if werk["textdichter_viaf"]:
                    g.add((person, OWL.sameAs, URIRef(VIAF[werk["textdichter_viaf"]])))
            else:
                g.add((subject, DCTERMS.creator, Literal(werk["textdichter"])))
        if werk["stimmen"] is not None:
            g.add((subject, LASSO.stimmen, Literal(werk["stimmen"])))
        if werk["textprovenienz"]:
            g.add((subject, LASSO.textprovenienz, Literal(werk["textprovenienz"])))
        if werk["edition"]:
            g.add((subject, LASSO.ersterscheinung, Literal(werk["edition"])))
        if werk["quelle"]:
            g.add((subject, LASSO.gesamtaufnahme, Literal(werk["quelle"])))

    TTL_PATH.parent.mkdir(exist_ok=True)
    g.serialize(destination=str(TTL_PATH), format="turtle")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    werke = fetch_werke(conn)

    write_json(werke)
    write_sql_dump(conn)
    write_ttl(werke)

    print(f"{len(werke)} Werke exportiert nach:")
    print(f"  {JSON_PATH.relative_to(ROOT)}")
    print(f"  {SQL_DUMP_PATH.relative_to(ROOT)}")
    print(f"  {TTL_PATH.relative_to(ROOT)}")

    conn.close()


if __name__ == "__main__":
    main()
