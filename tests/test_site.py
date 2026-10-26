"""Pruefungen fuer den Website-Build: python3 -m unittest discover -s tests"""
import re
from html import unescape
from urllib.parse import urlsplit
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SiteBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "docs"
        subprocess.run([sys.executable, str(ROOT / "build.py"), "--out", str(cls.out)], check=True, capture_output=True)
        cls.pages = {p.relative_to(cls.out).as_posix(): p.read_text(encoding="utf-8") for p in cls.out.rglob("index.html")}
        with open(ROOT / "site.toml", "rb") as f:
            cls.cfg = tomllib.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_pflichtseiten_vorhanden(self):
        expected = {"index.html", "impressum/index.html", "datenschutz/index.html"}
        expected.update(f"{app['id']}/index.html" for app in self.cfg.get("apps", []))
        self.assertEqual(set(self.pages), expected | {"de/" + rel for rel in expected})

    def test_jede_seite_verlinkt_impressum_und_datenschutz(self):
        for rel, t in self.pages.items():
            prefix, legal, privacy = ("/de/", "Impressum", "Datenschutz") if rel.startswith("de/") else ("/", "Legal notice", "Privacy")
            self.assertIn(f'href="{prefix}impressum/">{legal}<', t, rel)
            self.assertIn(f'href="{prefix}datenschutz/">{privacy}<', t, rel)

    def test_sprachen_entsprechende_seiten_und_interne_links(self):
        for rel, text in self.pages.items():
            german = rel.startswith("de/")
            lang = "de" if german else "en"
            self.assertIn(f'<html lang="{lang}">', text, rel)
            logical = rel.removeprefix("de/").removesuffix("index.html")
            en_url, de_url = "/" + logical, "/de/" + logical
            for code, url in (("en", en_url), ("de", de_url), ("x-default", en_url)):
                self.assertIn(f'<link rel="alternate" hreflang="{code}" href="{url}">', text, rel)
            other, other_url = ("en", en_url) if german else ("de", de_url)
            self.assertIn(f'href="{other_url}" lang="{other}" hreflang="{other}"', text, rel)
            for href in re.findall(r'href="([^"]+)"', text):
                u = urlsplit(unescape(href))
                if u.scheme or u.netloc:
                    continue
                target = self.out / u.path.lstrip("/") if u.path else self.out / rel
                if u.path.endswith("/"):
                    target /= "index.html"
                self.assertTrue(target.is_file(), f"{rel}: missing link {href}")
                if u.fragment:
                    self.assertIn(f'id="{u.fragment}"', target.read_text(encoding="utf-8"), f"{rel}: missing fragment {href}")

    def test_keine_externen_ressourcen_keine_skripte(self):
        for rel, t in self.pages.items():
            self.assertNotRegex(t, r'(?i)<script', rel)
            self.assertNotRegex(t, r'(?i)<(iframe|video|audio|source|object|embed)\b', rel)
            for src in re.findall(r'(?i)<img[^>]+src="([^"]+)"', t):
                self.assertTrue(src.startswith("/"), f"{rel}: Bild nicht vom eigenen Server: {src}")
                self.assertTrue((self.out / src.lstrip("/")).is_file(), f"{rel}: Bild fehlt im Build: {src}")
            self.assertNotRegex(t, r'(?i)<link[^>]+href="https?:', rel)
            self.assertNotRegex(t, r'(?i)src="https?:', rel)
            self.assertNotRegex(t, r'(?i)@import|url\(\s*["\']?https?:', rel)

    def test_schriften_lokal_mit_lizenz(self):
        for rel, t in self.pages.items():
            for url in re.findall(r'url\("([^"]+)"\)', t):
                self.assertTrue(url.startswith("/"), f"{rel}: Schrift nicht vom eigenen Server: {url}")
                f = self.out / url.lstrip("/")
                self.assertTrue(f.is_file(), f"{rel}: Schrift fehlt: {url}")
                self.assertTrue((f.parent / "OFL.txt").is_file(), f"{rel}: OFL.txt fehlt neben {url}")
                self.assertEqual(f.read_bytes()[:4], b"wOF2", url)

    def test_tab_symbole(self):
        self.assertTrue((self.out / "favicon.ico").is_file())
        for rel, t in self.pages.items():
            for href in re.findall(r'<link rel="(?:icon|apple-touch-icon)"[^>]*href="([^"]+)"', t):
                self.assertTrue(href.startswith("/"), f"{rel}: {href}")
                self.assertTrue((self.out / href.lstrip("/")).is_file(), f"{rel}: Symbol fehlt: {href}")

    def test_keine_platzhalter_uebrig(self):
        for rel, t in self.pages.items():
            self.assertNotRegex(t, r'\$[a-z_]+|\[(NAME|ANSCHRIFT|EMAIL|SCOPE|DATUM)\]', rel)

    def test_impressum_traegt_anbieter_aus_config(self):
        op = self.cfg["operator"]
        for prefix in ("", "de/"):
            t = self.pages[prefix + "impressum/index.html"]
            for k in ("name", "street", "postal_code", "city", "email"):
                self.assertIn(op[k], t, k)
            self.assertIn(op["country"] if prefix else op["english"]["country"], t)

    def test_datenschutz_anker_je_app(self):
        for prefix in ("", "de/"):
            t = self.pages[prefix + "datenschutz/index.html"]
            for app in self.cfg.get("apps", []):
                self.assertIn(f'id="{app["id"]}"', t)
                self.assertIn("Limited Use", t)

    def test_drive_und_mailtexte_nicht_verwechselt(self):
        for prefix in ("", "de/"):
            drive = self.pages[prefix + "fordiverse-rclone/index.html"]
            mail = self.pages[prefix + "fordiverse-mail/index.html"]
            privacy = self.pages[prefix + "datenschutz/index.html"]
            drive_privacy = privacy.split('id="fordiverse-rclone"', 1)[1].split('id="fordiverse-mail"', 1)[0]
            mail_privacy = privacy.split('id="fordiverse-mail"', 1)[1]
            for text in (mail, mail_privacy):
                self.assertIn("https://mail.google.com/", text)
                self.assertIn("Google MI Auth Gate", text)
                self.assertIn("BYOK", text)
                self.assertNotIn("eigene Google Drive", text)
                self.assertNotIn("own Google Drive", text)
            for text in (drive, drive_privacy):
                self.assertIn("https://www.googleapis.com/auth/drive", text)
                self.assertNotIn("https://mail.google.com/", text)
                self.assertNotIn("OpenBao", text)
            self.assertIn("IMAPS", mail_privacy)
            self.assertIn("nicht personalisierter" if prefix else "non-personalized", mail_privacy)
            self.assertIn("26. Oktober 2026" if prefix else "26 October 2026", privacy)

    def test_fehlender_pflichtwert_bricht_laut_ab(self):
        bad = ROOT / "tests" / "_bad.toml"
        bad.write_text((ROOT / "site.toml").read_text(encoding="utf-8").replace('street = ', 'strasse_falsch = '), encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--config", str(bad), "--out", str(Path(self.tmp.name) / "x")], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("operator.street fehlt", r.stderr + r.stdout)
        finally:
            bad.unlink()

    def test_beteiligte_seele_zuerst(self):
        crews = [("index.html", self.cfg["site"]["crew"])]
        crews += [(f"{a['id']}/index.html", a["crew"]) for a in self.cfg.get("apps", [])]
        for prefix in ("", "de/"):
            for rel, crew in crews:
                t = self.pages[prefix + rel]
                for c in crew:
                    soul = (c["soul"] if prefix else c.get("soul_en", c["soul"])) or ("ohne Seele" if prefix else "without a soul")
                    self.assertIn(soul, t, prefix + rel)
                    self.assertLess(t.index(soul), t.index(c["agency"], t.index(soul)), f"{prefix + rel}: Seele nicht zuerst")
                    self.assertIn(c["harness"], t, prefix + rel)

    def test_fehlende_beteiligte_brechen_laut_ab(self):
        bad = ROOT / "tests" / "_bad_crew.toml"
        src = (ROOT / "site.toml").read_text(encoding="utf-8")
        bad.write_text(src.replace("[[apps.crew]]\nsoul = ", "[[apps.crew]]\nseele_falsch = ", 1), encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--config", str(bad), "--out", str(Path(self.tmp.name) / "y")], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(".soul fehlt", r.stderr + r.stdout)
        finally:
            bad.unlink()

    def test_code_enthaelt_keine_personendaten(self):
        op = self.cfg["operator"]
        for f in [ROOT / "build.py", *(ROOT / "templates").glob("*")]:
            t = f.read_text(encoding="utf-8")
            for k in ("name", "street", "email"):
                self.assertNotIn(op[k], t, f"{f.name} enthaelt {k}")


if __name__ == "__main__":
    unittest.main()
