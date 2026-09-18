---
title: "Über diese Datenbank"
---

Die Daten dieses Portals stammen aus einer Excel-Tabelle (`Werke_aus_TEX.xlsx`), die ihrerseits
automatisiert aus einer TeX-Quelldatei erzeugt wurde. Die folgenden Hinweise zur Datengrundlage
stammen aus dieser Konvertierung:

- **Quelldatei:** `LVTEX1.TEX`
- **Datengrundlage:** Ausschließlich die angegebene TeX-Datei; keine externen Ergänzungen.
- **Textdichter:** Nur explizite Inline-Angaben aus der LV-Tabelle.
- **Textprovenienz:** Nur ausdrücklich mit `TEXTPROVENIENZ` markierte Angaben sowie explizite
  generische Inline-Labels.
- **Untereinträge:** Nur unmittelbar auf einen `\fg`-Eintrag folgende unnummerierte Titelzeilen.
  Eine neue Drucknummer beendet die Gruppe.
- **Leere Zellen:** In der Quelldatei wurde keine eindeutig zuordenbare Angabe gefunden.

> **Hinweis zur Datenqualität:** Die ursprüngliche Konvertierungsnotiz nannte „309 Datensätze".
> Diese Zahl ließ sich beim Aufbau dieses Portals nicht nachvollziehen (weder als Anzahl der
> LV-Hauptnummern noch als Anzahl der Zeilen) und wurde daher durch eine automatisch gezählte,
> stets aktuelle Angabe ersetzt (siehe unten).

## Datenpflege

Die Werkdaten werden in einer SQLite-Datenbank gepflegt und bei jeder Veröffentlichung neu in
diese Website sowie in einen RDF/Turtle-Export (Dublin Core) umgewandelt.
