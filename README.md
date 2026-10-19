# mutual-roots.github.io

Die kleinste mögliche öffentliche Seite von **Mutual Roots**: Startseite, Impressum,
Datenschutzerklärung und die Startseite des privaten OAuth-Clients `fordiverse-rclone`.
Projektseiten wie `/nvidia-legacy-580-installer/` kommen aus eigenen Repos dazu.

## So funktioniert es

- **Alle Anbieter- und Projektangaben stehen nur in `site.toml`.** `build.py` und
  `templates/` enthalten keine Personendaten (ein Test prüft das).
- `python3 build.py` erzeugt die Seiten nach `docs/`; GitHub Pages liefert `docs/` aus.
- Fehlt in `site.toml` ein Pflichtwert, bricht der Build laut ab, statt eine
  unvollständige Seite zu erzeugen.
- Die Seiten haben keine Cookies, kein Tracking, keine Skripte und keine Inhalte von
  fremden Servern. Tests: `python3 -m unittest discover -s tests`.
- Die Bestätigungsdatei der Google Search Console (`google….html`) gehört nach `verify/`;
  der Build kopiert sie an die Wurzel.

## Für eigene Seiten nutzen

Repo kopieren, `site.toml` mit den eigenen Angaben füllen (Anbieter nach § 18 MStV:
Vor- und Nachname und ladungsfähige Anschrift), `python3 build.py`, Tests laufen lassen,
fertig. Keine Rechtsberatung: Ob die Angaben für das eigene Angebot reichen, prüft jede
und jeder selbst.

## Wie es entsteht

Mutual Roots entsteht in Zusammenarbeit: Simon Moritz Reichard gibt Richtung, Entscheidungen
und Korrekturen vor; KI-Agenten schreiben, prüfen und pflegen den Code. Autorin der Umsetzung:
Kassiopeia (Claude Code, Modell Claude Opus 5.5) im Auftrag von Simon Moritz Reichard.
Einen klassischen menschlichen Maintainer gibt es nicht; jede Veröffentlichung durchläuft
automatische Prüfroutinen. Nutzung auf eigene Gefahr.

Das Wolf-Emblem (`assets/wolf-1024.png`, Webfassung `assets/wolf.webp`) stammt von Simon Moritz
Reichard: Entwurf mit Googles Bildmodell (Nano Banana), leicht überarbeitete Fassung mit OpenAIs
Bildgenerierung in Codex.

Rechteinhaber: Simon Moritz Reichard. Lizenz: noch nicht festgelegt (Vorschlag: GPL-3.0-or-later
für den Code, CC BY-SA 4.0 für die Texte).
