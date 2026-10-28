# Architecture

- `desktop/dotx/__main__.py`: Qt browser window, shared persistent WebEngine profile, UI interactions and workspace web shortcuts.
- `desktop/dotx/core.py`: address/search normalization and atomic local JSON storage.
- `desktop/dotx/theme.py`: centralized desktop light/dark/system appearance tokens.
- `desktop/tests`: UI-independent unit tests. `scripts/smoke_desktop.py` exercises a local web server and Qt on a suitable environment.
- `site/`: generated, static, relative-link website. `scripts/build_site.py` generates HTML; `assets/` contains authored CSS and SVG.
- `.github/workflows/`: unit checks and a proposed Pages workflow; neither has run on GitHub.

The WebEngine profile stores cookies/cache locally. Bookmarks, history, search settings and opt-in restored-tab URLs are in application data. Profile and browser state are not encrypted. An experimental, mock-tested GitHub device authorization flow verifies identity and keeps the token only in process memory. It is not yet live-account tested and no remote backend is integrated. A separate existing Supabase project was inspected; see `SUPABASE_AUDIT.md`. Design future integration modules per provider, with explicit state machines, minimum scopes, token storage outside settings and async I/O. Do not infer support for a common OAuth flow across providers.

## Design tokens

The website CSS defines dark navy `#091320`, surface `#101f2f`, text `#f2f7fc` and accent `#8fdcf7`, plus light and system color palettes; 1160px max content width; 8–10px card radii; breakpoints at 850px and 540px; system sans-serif typography; and reduced-motion handling. Desktop chrome uses related light/dark palettes from `desktop/dotx/theme.py`. Browser webpage content is not recolored by these settings. The original SVG mark is shared by the site; no Windows `.ico` is available yet.
