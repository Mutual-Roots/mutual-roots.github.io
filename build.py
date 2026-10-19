#!/usr/bin/env python3
"""build.py: erzeugt die statischen Seiten aus site.toml und templates/ nach docs/.

Alle Personen- und Projektangaben kommen aus site.toml; fehlt ein Pflichtwert, bricht
der Build laut ab. Keine externen Ressourcen, keine Cookies, kein Skript in den Seiten.
Aufruf: python3 build.py [--config site.toml] [--out docs]
"""
import argparse
import html
import shutil
import sys
import tomllib
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
REQUIRED = {
    "site": ["base_url", "project_name", "lang", "stand", "emblem"],
    "operator": ["name", "street", "postal_code", "city", "country", "email", "responsible_18_2"],
    "ai": ["notice"],
}
APP_REQUIRED = ["id", "title", "kind", "tool_name", "tool_url", "scope", "data_examples", "token_storage", "no_ml_training"]


def die(msg):
    sys.exit(f"ABBRUCH: {msg}")


def load(path):
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    for sec, keys in REQUIRED.items():
        if sec not in cfg:
            die(f"Abschnitt [{sec}] fehlt in {path}")
        for k in keys:
            if k not in cfg[sec] or cfg[sec][k] in ("", None):
                die(f"{sec}.{k} fehlt in {path}")
    for app in cfg.get("apps", []):
        for k in APP_REQUIRED:
            if k not in app or app[k] in ("", None):
                die(f"apps.{k} fehlt fuer {app.get('id', '?')}")
    for p in cfg.get("projects", []):
        for k in ("id", "title", "summary", "enabled"):
            if k not in p:
                die(f"projects.{k} fehlt fuer {p.get('id', '?')}")
    return cfg


def e(s):
    return html.escape(str(s), quote=True)


def link(url, text=None):
    return f'<a href="{e(url)}">{e(text or url)}</a>'


def address_block(op):
    return (f"<address>{e(op['name'])}<br>{e(op['street'])}<br>"
            f"{e(op['postal_code'])} {e(op['city'])}<br>{e(op['country'])}</address>")


def page_index(cfg):
    s, op = cfg["site"], cfg["operator"]
    items = []
    for app in cfg.get("apps", []):
        items.append(f"<li>{link('/' + app['id'] + '/', app['title'])}: {e(app['kind'])}, nur für die eigene Nutzung.</li>")
    for p in cfg.get("projects", []):
        if p["enabled"]:
            items.append(f"<li>{link('/' + p['id'] + '/', p['title'])}: {e(p['summary'])}</li>")
    lst = "<ul>\n" + "\n".join(items) + "\n</ul>" if items else ""
    return (f"<h1>{e(s['project_name'])}</h1>\n"
            f"<p class=\"lede\">Ein privates, nicht-kommerzielles Projekt von {e(op['name'])}. "
            f"Keine Werbung, keine Einnahmen, kein Verkauf.</p>\n"
            + (f"<h2>Hier zu finden</h2>\n{lst}\n" if lst else "")
            + f"<p class=\"note\">{e(cfg['ai']['notice'])}</p>")


def page_impressum(cfg):
    s, op = cfg["site"], cfg["operator"]
    out = [f"<h1>Impressum</h1>",
           f"<p><strong>{e(s['project_name'])}</strong> ist ein privates, nicht-kommerzielles Projekt von {e(op['name'])}. "
           f"„{e(s['project_name'])}“ ist keine Firma und keine juristische Person.</p>",
           "<h2>Anbieter (§ 18 Abs. 1 MStV)</h2>", address_block(op),
           "<h2>Kontakt</h2>", f"<p>E-Mail: {link('mailto:' + op['email'], op['email'])}</p>"]
    if op["responsible_18_2"]:
        out += ["<h2>Verantwortlich für den Inhalt (§ 18 Abs. 2 MStV)</h2>", f"<p>{e(op['name'])}, Anschrift wie oben.</p>"]
    out += [f"<p>Diese Angaben gelten für alle Seiten unter {link(s['base_url'] + '/')}, auch für die Projektseiten in Unterverzeichnissen.</p>",
            f"<p>Datenschutzerklärung: {link('/datenschutz/', s['base_url'] + '/datenschutz/')}</p>",
            f"<p class=\"muted\">Stand: {e(s['stand'])}</p>"]
    return "\n".join(out)


def app_privacy(app, op):
    n = e(op["name"])
    ml = "<li><strong>Kein KI-Training:</strong> Die Daten werden nicht zum Training von KI- oder ML-Modellen verwendet.</li>" if app["no_ml_training"] else ""
    return f"""<h2 id="{e(app['id'])}">{e(app['title'])} ({e(app['kind'])})</h2>
<p>„{e(app['title'])}“ ist der Name eines OAuth-Clients in einem Google-Cloud-Projekt von {n}. Ihn nutzt ausschließlich {n} selbst, um mit dem Open-Source-Programm {link(app['tool_url'], app['tool_name'])} auf das eigene Google-Drive-Konto zuzugreifen. Es ist kein öffentlicher Dienst; es gibt keine weiteren Nutzerinnen oder Nutzer, keine Registrierung und keinen Download.</p>
<ul>
<li><strong>Abgerufene Google-Daten:</strong> Über den Berechtigungsumfang <code>{e(app['scope'])}</code> werden Dateien und deren Metadaten (Namen, Ordner, Größen, Zeitstempel, Prüfsummen) im eigenen Google Drive von {n} abgerufen.</li>
<li><strong>Nutzung:</strong> ausschließlich, um eigene Dateien (z. B. {e(app['data_examples'])}) zwischen eigenen Geräten und dem eigenen Google Drive hochzuladen, herunterzuladen, zu synchronisieren und zu sichern.</li>
<li><strong>Speicherung:</strong> Das OAuth-Token liegt {e(app['token_storage'])}. Dateien aus Google Drive liegen nur auf eigenen Geräten von {n}. Diese Website speichert und verarbeitet keine Google-Daten.</li>
<li><strong>Weitergabe:</strong> keine Weitergabe an Dritte, kein Verkauf, keine Werbung, keine Profilbildung.</li>
{ml}
<li><strong>Limited Use:</strong> Die Nutzung und Weitergabe von Informationen, die {e(app['title'])} von Google-APIs erhält, an andere Apps richtet sich nach der {link('https://developers.google.com/terms/api-services-user-data-policy', 'Google API Services User Data Policy')}, einschließlich der Limited-Use-Anforderungen.</li>
<li><strong>Widerruf:</strong> jederzeit im Google-Konto unter {link('https://myaccount.google.com/permissions')}; lokale Tokens werden dann ebenfalls gelöscht.</li>
<li><strong>Betroffene:</strong> Verarbeitet werden ausschließlich eigene Daten von {n}.</li>
</ul>
<p lang="en"><em>English summary:</em> {e(app['title'])} is a private OAuth client ({e(app['kind'])}) used only by {n} with the open-source tool {e(app['tool_name'])} to access {n}'s own Google Drive (upload, download, sync and back up own files). It is not a public service and has no other users. Google user data stays on {n}'s own devices and is never shared, sold or used for advertising{', nor used to train AI/ML models' if app['no_ml_training'] else ''}. {e(app['title'])}'s use and transfer to any other app of information received from Google APIs will adhere to the Google API Services User Data Policy, including the Limited Use requirements. Access can be revoked at https://myaccount.google.com/permissions. Contact: {e(op['email'])}.</p>"""


def page_datenschutz(cfg):
    s, op = cfg["site"], cfg["operator"]
    apps = "\n".join(app_privacy(a, op) for a in cfg.get("apps", []))
    return f"""<h1>Datenschutz&shy;erklärung</h1>
<p class="muted">Stand: {e(s['stand'])}</p>
<h2>1. Verantwortlicher</h2>
{address_block(op)}
<p>E-Mail: {link('mailto:' + op['email'], op['email'])} – siehe auch das {link('/impressum/', 'Impressum')}.</p>
<h2>2. Kurzfassung</h2>
<p>Die Seiten unter {link(s['base_url'] + '/')} sind statische HTML-Seiten. Es gibt keine Cookies, keine Analyse- oder Tracking-Werkzeuge, keine Formulare und keine Inhalte von fremden Servern (keine fremden Schriftarten, Skripte, Bilder oder Videos). Ich selbst erhebe und speichere keine Daten über Besucherinnen und Besucher. Technisch verarbeitet werden Daten nur beim Hoster (Abschnitt 3).</p>
<h2>3. Hosting bei GitHub Pages</h2>
<p>Die Seiten werden über GitHub Pages ausgeliefert, einen Dienst von GitHub (GitHub, Inc., USA, ein Unternehmen des Microsoft-Konzerns). Beim Aufruf verarbeitet GitHub die für die Auslieferung nötigen Verbindungsdaten, insbesondere Ihre IP-Adresse. Nach der Dokumentation von GitHub wird die IP-Adresse von Besucherinnen und Besuchern einer GitHub-Pages-Seite aus Sicherheitsgründen protokolliert und gespeichert, auch ohne Anmeldung bei GitHub. Ich habe auf diese Protokolle keinen Zugriff; die Speicherdauer legt GitHub fest.</p>
<ul>
<li>Zweck: sichere und stabile Auslieferung der Seiten.</li>
<li>Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO; berechtigtes Interesse ist die sichere, zuverlässige und kostenfreie Bereitstellung dieser privaten Seiten.</li>
<li>Drittland: Die Daten können in den USA verarbeitet werden. GitHub stützt Übermittlungen nach eigenen Angaben auf das EU-US Data Privacy Framework und auf EU-Standardvertragsklauseln.</li>
<li>Weitere Informationen: {link('https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement', 'GitHub General Privacy Statement')}</li>
</ul>
<h2>4. Links zu anderen Websites</h2>
<p>Links zu anderen Websites werden erst aufgerufen, wenn Sie sie anklicken. Ab dann gilt die Datenschutzerklärung des jeweiligen Anbieters.</p>
<h2>5. OAuth-Clients für die eigene Nutzung</h2>
{apps}
<h2>6. Ihre Rechte</h2>
<p>Sie haben nach der DSGVO das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18) und Datenübertragbarkeit (Art. 20). Gegen Verarbeitungen auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO können Sie Widerspruch einlegen (Art. 21). Weil ich selbst keine Besucherdaten speichere, betreffen solche Anliegen praktisch die Protokolle von GitHub; bitte wenden Sie sich dafür auch direkt an GitHub. Sie haben außerdem das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren (Art. 77 DSGVO).</p>"""


def page_app(app, cfg):
    s, op = cfg["site"], cfg["operator"]
    n = e(op["name"])
    return f"""<h1>{e(app['title'])}</h1>
<p><strong>Was ist das?</strong> {e(app['title'])} ist ein privater {e(app['kind'])} von {n}. Er wird mit dem Open-Source-Programm {link(app['tool_url'], app['tool_name'])} benutzt, um von eigenen Rechnern auf das eigene Google Drive zuzugreifen: eigene Dateien hochladen, herunterladen, synchronisieren und sichern.</p>
<p><strong>Für wen?</strong> Nur für {n} selbst. Es ist kein öffentlicher Dienst; es gibt keine Anmeldung, keinen Download und keine weiteren Nutzerinnen oder Nutzer.</p>
<p><strong>Welche Daten?</strong> Nur Dateien und Metadaten im eigenen Google Drive von {n} (Berechtigung: <code>{e(app['scope'])}</code>). Die Daten bleiben auf eigenen Geräten; keine Weitergabe, kein Verkauf, keine Werbung. Die Nutzung von Daten aus Google-APIs folgt der Google API Services User Data Policy, einschließlich der Limited-Use-Anforderungen. Details: {link('/datenschutz/#' + app['id'], 'Datenschutzerklärung, Abschnitt ' + app['title'])}.</p>
<p><strong>Zugriff widerrufen:</strong> {link('https://myaccount.google.com/permissions')}</p>
<p><strong>Kontakt:</strong> {link('mailto:' + op['email'], op['email'])}</p>
<h2 lang="en">English</h2>
<p lang="en"><strong>{e(app['title'])}</strong> is a private OAuth client ({e(app['kind'])}) used by {n} together with the open-source tool {e(app['tool_name'])} ({e(app['tool_url'])}) to access {n}'s own Google Drive: uploading, downloading, syncing and backing up own files. It is not a public service and has no sign-up, no download and no other users. It accesses only files and metadata in {n}'s own Drive (scope: {e(app['scope'])}). Data stays on {n}'s own devices and is never shared, sold or used for advertising. Use of information received from Google APIs adheres to the Google API Services User Data Policy, including the Limited Use requirements. Privacy policy: {link(s['base_url'] + '/datenschutz/')}</p>"""


def render(base, cfg, title, body, bodyclass="page"):
    s = cfg["site"]
    return Template(base).substitute(lang=e(s["lang"]), title=e(title), project_name=e(s["project_name"]),
                                     body=body, bodyclass=bodyclass, emblem=e(s["emblem"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "site.toml"))
    ap.add_argument("--out", default=str(HERE / "docs"))
    a = ap.parse_args()
    cfg = load(a.config)
    base = (HERE / "templates" / "base.html").read_text(encoding="utf-8")
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    pages = {"": (cfg["site"]["project_name"], page_index(cfg)),
             "impressum": ("Impressum – " + cfg["site"]["project_name"], page_impressum(cfg)),
             "datenschutz": ("Datenschutzerklärung – " + cfg["site"]["project_name"], page_datenschutz(cfg))}
    for app in cfg.get("apps", []):
        pages[app["id"]] = (app["title"], page_app(app, cfg))
    for rel, (title, body) in pages.items():
        d = out / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render(base, cfg, title, body, "home" if rel == "" else "page"), encoding="utf-8")
    emblem = HERE / cfg["site"]["emblem"]
    if not emblem.is_file():
        die(f"Emblem {emblem} fehlt")
    (out / emblem.parent.name).mkdir(parents=True, exist_ok=True)
    shutil.copy2(emblem, out / cfg["site"]["emblem"])
    verify = HERE / "verify"
    for f in (sorted(verify.glob("google*.html")) if verify.is_dir() else []):
        shutil.copy2(f, out / f.name)
    print(f"ok: {len(pages)} Seiten nach {out}")


if __name__ == "__main__":
    main()
