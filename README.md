# EET Analyse App

Diese Streamlit-App ermöglicht die Analyse von EET-Daten auf Basis einer Excel-Datei. Für eine eingegebene ISIN werden die Werte mit Fonds derselben Klassifikation verglichen.

## Funktionen

- Analyse nachhaltiger und taxonomiekonformer Investitionen
- Auswertung von Scope 1, 2 und 3 Emissionen
- Visuelle Histogramme mit Vergleich zu Mittelwert und Median
- PDF-Download der Analyse

## Nutzung

1. Lege die Datei `EET_Beispieldaten_100_ISINs_variiert.xlsx` in das gleiche Verzeichnis wie `app.py`.
2. Starte die App mit:

```bash
streamlit run app.py
```

## Voraussetzungen

Siehe `requirements.txt` für benötigte Pakete.
