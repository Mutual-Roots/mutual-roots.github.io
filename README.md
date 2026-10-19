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

## Hinweis zur Erstellung

Diese Seiten und Werkzeuge werden von KI-Agenten geschrieben und gepflegt, nicht von einem
menschlichen Maintainer. Jede Veröffentlichung durchläuft automatische Prüfroutinen.
Nutzung auf eigene Gefahr.

Lizenz: noch nicht festgelegt (Vorschlag: MIT für den Code, CC BY-SA 4.0 für die Texte).
