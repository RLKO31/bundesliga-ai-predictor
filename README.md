# Bundesliga AI Predictor Engine

[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen?logo=github)](https://RLKO31.github.io/bundesliga-ai-predictor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Leaflet: 1.9.4](https://img.shields.io/badge/Geo-Leaflet%201.9.4-199900.svg)](https://leafletjs.com/)

Eine KI-gestützte Prognose- und Simulationsplattform für die **Fußball-Bundesliga**. Das System kombiniert modernste Machine-Learning-Verfahren (DINOv2 Spatial Vision Features, Gradient Boosting, Poisson-Torverteilungen und Multi-Wettbewerbs-Elo) mit interaktiver Geodatenanalyse (Reise- und Distanzmatrizen) in einem dynamischen Single-Page-Web-Dashboard.

Entwickelt als wissenschaftliches Portfolio-Projekt an der **Technischen Hochschule Würzburg-Schweinfurt (THWS)**.

**Live-Webseite:** [https://RLKO31.github.io/bundesliga-ai-predictor/](https://RLKO31.github.io/bundesliga-ai-predictor/)

---

## Hauptfunktionen & Module

- **Spieltagesprognosen:**
  - Berechnete Siegwahrscheinlichkeiten (Heim / Unentschieden / Auswärts)
  - Erwartete Torverteilungen (Expected Goals $xG$, Poisson-Marginals) und Over/Under-Schätzungen
  - Ausführliche KI-Begründung und Formkurvenanalyse für jede Paarung
- **Tabellen-Simulation:**
  - Dynamischer Monte-Carlo-Saisonverlauf
  - Prognostizierte Abschlusstabelle mit Meisterwahrscheinlichkeit, Europapokal-Plätzen und Abstiegswahrscheinlichkeiten
- **Interaktive Geodaten- & Reisematrix (Leaflet & CARTO):**
  - Kartografische Visualisierung aller Bundesligastadien
  - Distanz-, Reise- und Belastungsmatrix (Kilometerdistanzen und Reiseaufwand bei Auswärtsfahrten)
- **Modell- & Taktikanalyse:**
  - Taktische Adaptabilität und Pressing-Indikatoren (PPDA - Passes per Defensive Action)
  - Tor-Komplexitätsmetriken und gegnerische Schwachstellenprofile
- **Modell-Benchmarks & Reality-Check:**
  - Transparente Validierung gegen reale Spieltagsdaten
  - Brier-Score, Log-Loss und Accuracy-Vergleiche

---

## Systemarchitektur & Methodik

1. **Spatial AI & DINOv2 Vision Pipeline:**
   - Extraktion räumlicher Spielzug- und Heatmap-Repräsentationen via Transfer Learning.
2. **Tabular Machine Learning Trunk:**
   - Ensembles aus Random Forest, HistGradientBoosting und Ridge Regression trainiert auf historischen Leistungs- und $xG$-Daten.
3. **Multi-Wettbewerbs-Harmonisierung:**
   - Berücksichtigung von Belastungszyklen aus DFB-Pokal und europäischen Wettbewerben (UEFA Champions League, Europa League, Conference League).

---

## Datenquellen, Danksagungen & Lizenzen (Credits)

Alle in diesem Projekt verwendeten Datenquellen, APIs und Basiskarten dienen ausschließlich nicht-kommerziellen Forschungs- und Studienzwecken:

| Komponente | Datenquelle / Anbieter | Lizenz & Verwendung |
|---|---|---|
| **Echtzeit-Spielpläne & Ergebnisse** | [OpenLigaDB](https://www.openligadb.de) | Freie Open-Source Community API für Spielpaarungen, Anstoßzeiten und offizielle Bundesliga-Ergebnisse. |
| **Statistiken & $xG$-Metriken** | [Understat](https://understat.com) | Historische Expected Goals ($xG$), PPDA und Schussdaten für offline Feature Engineering gem. §§ 44b, 60d UrhG (Text- und Data-Mining für wissenschaftliche Forschung). |
| **Kartografie & Basemap** | [OpenStreetMap](https://www.openstreetmap.org/copyright) & [CARTO](https://carto.com/attributions) | OpenStreetMap-Mitwirkende (ODbL) und CARTO Dark Matter Tiles für die interaktive Stadionkarte. |
| **Vereinswappen & Grafiken** | [Wikimedia Commons](https://commons.wikimedia.org) | Freie Vektorgrafiken zur rein redaktionellen und nominativen Identifikation gem. § 23 MarkenG. |
| **Pokal- & Europapokalhistorie** | Öffentliche Sportarchive (ESPN / DFB / UEFA) | Faktische historische Sportergebnisse (gemeinfrei nach dt. Urheberrecht). |

> [!NOTE]
> **Haftungsausschluss / Disclaimer:** Rein akademisches Forschungs- und Portfolio-Projekt. Die bereitgestellten Daten und Prognosen stellen **keine Anlageberatung, Spielprognose oder Wettempfehlung** dar. Glücksspiel kann süchtig machen.

---

## Lokale Ausführung

```bash
# Repository klonen
git clone https://github.com/RLKO31/bundesliga-ai-predictor.git
cd bundesliga-ai-predictor

# index.html direkt im Browser öffnen
start index.html
```

---

## Impressum (§ 5 DDG) & Kontakt

- **Entwickler / Betreiber:** Ralf Oppel
- **Akademische Einrichtung:** Technische Hochschule Würzburg-Schweinfurt (THWS)
- **Kontakt:** [ralf.oppel@study.thws.de](mailto:ralf.oppel@study.thws.de)
- **Lizenz:** [MIT License](LICENSE)
