# mutual-roots.github.io

The small public website for **Mutual Roots**: home, legal notice, privacy policy
and app information for `fordiverse-rclone` and `Fordiverse Mail`. Project pages such
as `/nvidia-legacy-580-installer/` can be supplied by their own repositories.

## How it works

- **All operator and project information lives in `site.toml`.** `build.py` and
  `templates/` contain no personal details; a test checks this.
- `python3 build.py` generates `docs/`; GitHub Pages serves that directory.
- English is the default at the existing URLs. Complete German editions live under
  `/de/`, with equivalent-page language links and `hreflang` metadata. There is no
  script or automatic language redirect. The existing `/impressum/`,
  `/datenschutz/` and `/datenschutz/#fordiverse-mail` URLs remain usable.
- Configurable English text is held alongside the German text in `[...english]`
  tables. Both editions share factual identifiers, scopes, contact details and assets.
- Missing required configuration, including English app text, fails the build rather
  than generating an incomplete page.
- No cookies, tracking, scripts or resources from other servers. Fonts and their
  licences are included locally. Checks: `python3 -m unittest discover -s tests`.
- A Google Search Console verification file (`google….html`) goes in `verify/`;
  the builder copies it to the site root.

`/fordiverse-mail/` describes the existing “Google MI Auth Gate” Gmail connection,
Pimalaya and local Mox/Cypht mirrors. Drive and Mail content remain separate.
Publishing this website does not change Google's branding, publication or
verification status.

## Reusing the site

Copy the repository, replace the details in `site.toml` with your own (including the
operator's full name and service address under § 18 MStV), run `python3 build.py`,
and run the checks. This is not legal advice; each operator must assess whether the
information meets their own requirements.

## How it is made

Mutual Roots is a collaboration: Simon Moritz Reichard provides direction,
decisions and corrections; AI agents write, review and maintain the code.
The original implementation was authored by Kassiopeia (Claude Code, Claude Opus 5.5)
on behalf of Simon Moritz Reichard. The Mail addition and English/German editions
are by Kassiopeia (native Codex instance; OpenAI, Codex harness). These origins
remain separately identified. There is no conventional human maintainer; every
publication goes through automated checks. Use at your own risk.

The wolf emblem (`assets/wolf-1024.png`, web edition `assets/wolf.webp`) comes from
Simon Moritz Reichard: created with Google's image model (Nano Banana), with a
lightly revised version made using OpenAI image generation in Codex.

## Licences

Rights holder: Simon Moritz Reichard.

| Part | Licence |
|---|---|
| Code (`build.py`, `templates/`, `tests/`) | MIT; see `LICENSE` |
| Page text and this README | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Fonts (`assets/fonts/`) | SIL Open Font License 1.1; each includes `OFL.txt`, with sources in `assets/fonts/HERKUNFT.md` |
| Wolf emblem (`assets/wolf*`) | All rights reserved; excluded from the licences above |
| Details in `site.toml` (name, address, email) | Personal data, not licensed for reuse; replace with your own details |
