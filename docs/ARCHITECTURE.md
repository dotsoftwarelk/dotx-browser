# Architecture

- `desktop/dotx/__main__.py`: Qt browser window, shared persistent WebEngine profile, UI interactions and workspace web shortcuts.
- `desktop/dotx/core.py`: address/search normalization and atomic local JSON storage.
- `desktop/tests`: UI-independent unit tests. `scripts/smoke_desktop.py` exercises a local web server and Qt on a suitable environment.
- `site/`: generated, static, relative-link website. `scripts/build_site.py` generates HTML; `assets/` contains authored CSS and SVG.
- `.github/workflows/`: unit checks and a proposed Pages workflow; neither has run on GitHub.

The WebEngine profile stores cookies/cache locally. Bookmarks, history and search settings are in application data. Profile and browser state are not encrypted. No OAuth or remote backend exists. Design future integration modules per provider, with explicit state machines, minimum scopes, token storage outside settings and async I/O. Do not infer support for a common OAuth flow across providers.

## Design tokens

The website CSS defines navy `#09111e`, surface `#111e30`, border `#26374e`, text `#eff6ff`, muted `#a5b6cd`, accent `#7cd6fa`, 1160px max content width, 8–14px radii, responsive breakpoints at 850px and 540px, system sans-serif typography and reduced-motion handling. The desktop uses a related dark theme but does not yet share a token library or offer light/system themes. SVG mark is original; no Windows `.ico` is available yet.
