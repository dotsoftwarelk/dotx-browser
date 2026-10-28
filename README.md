# DOTX Browser — development prototype

DOTX is a new browser prototype by dotsoftwarelk, accompanied by a static product website. **This is not a release candidate.** No existing repository was available for inspection; the project was initialized from scratch and pushed to the public GitHub repository `dotsoftwarelk/dotx-browser`. The website is published on GitHub Pages. No Windows installer or native API integration has been verified.

## Run from source

Use Python 3.10–3.13 in a virtual environment. Qt for Python/WebEngine platform dependencies are required; see `docs/DEVELOPMENT.md`. From the project root:

```sh
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
cd desktop
python -m dotx
```

The prototype supports multiple reorderable tabs, tab duplication and session-only reopen, address/search input, back/forward/reload, find in page, zoom, bookmarks, history, a download save prompt, search selection and workspace website shortcuts. An experimental private window uses an off-the-record profile and does not save DOTX history or bookmarks; downloads remain on disk. It does not implement account connections, secure token storage, automatic updates, or complete permission controls. The shortcuts are not API connections. It is not yet suitable for sensitive browsing.

Generate and check the site:

```sh
python scripts/build_site.py
python scripts/check_site.py
PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v
```

On Windows PowerShell set `$env:PYTHONPATH = 'desktop'` for the final command. The website is in `site/`. See `docs/BASELINE_AUDIT.md` for evidence and limitations, and `docs/WEBSITE_DEPLOYMENT.md` for deployment.

## Licensing

No project license has been selected by the owner. Do not assume permission to redistribute. Qt for Python and WebEngine have their own licensing obligations; review Qt and bundled Chromium licenses before distributing builds.
