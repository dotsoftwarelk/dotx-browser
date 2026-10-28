# UI audit and implementation baseline

Baseline: `063e8019e379e476e4dd1feecb88d8ec6c5c112e` on `main`, inspected 2026-10-28. Working tree clean. The public GitHub API listed only `main` and no open pull requests at inspection. Pages is deployed through `.github/workflows/pages.yml`; the public Pages-settings API returned 404 without credentials, but the published site and successful workflow were verified independently.

## Architecture and build

The actual browser is Python/PySide6/Qt WebEngine, launched by `desktop/run.py` or `python -m dotx` from `desktop`. `requirements.txt` pins PySide6 6.10.3 and `requirements-build.txt` additionally pins PyInstaller 6.22.3; transitive dependencies and system inputs are not fully locked. CI uses Python 3.12; local baseline was Python 3.13.16 on Linux. Normal windows use a persistent WebEngine profile and JSON state; private windows use off-the-record profiles. History recording defaults on; session restore is opt-in. `theme.py` owns light/dark/system desktop styling. `scripts/build_site.py` generates 11 HTML pages in `site/`; CSS, SVG, JS and the real staged screenshot are separate assets. Pages regenerates and deploys on main; Windows CI builds and smoke-tests unsigned artifacts.

## Baseline results

- `python -m compileall -q desktop scripts`: pass.
- `python scripts/build_site.py && python scripts/check_site.py`: 11 pages generated and checked; clean tree afterward.
- `PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v`: 23 pass.
- `node scripts/test_download_js.js`: pass, mocked metadata.
- `python scripts/test_website_browser.py`: pass, Chromium desktop/mobile, theme, mocked download metadata, project 404, no-JS fallback.
- Qt smoke: desktop, download, session, settings, bookmarks, popup and history privacy all passed; GitHub device flow mock passed. Linux container only: `QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu PYTHONPATH=desktop`; disabling the sandbox is a container test exception, not application configuration or release guidance.
- Baseline GitHub Tests, Pages and Windows development workflows at `063e801` completed successfully. Windows CI is not interactive Windows 10/11 acceptance.

## Findings from source and actual Qt smoke runs

1. The main toolbar uses Unicode glyphs and wide text buttons; address space and affordance suffer at small widths. Actions have tooltips but icon-only accessible names and enabled-state accuracy need explicit testing.
2. Back/forward are always enabled; the current loading indicator can become stale when switching tabs. Theme-independent inline HTTP/HTTPS colors have poor light-theme contrast.
3. The tab bar has selected/inactive colors but limited keyboard-focus treatment and fixed large tab minimum width. Real website icons are displayed when supplied by WebEngine.
4. History/bookmark lists have no empty-state message; deletion and settings descriptions need to remain precise. Settings mixes multiple actions in a single relatively small dialog.
5. Workspace opens existing external sites, with public GitHub search and a separately mock-tested account flow. These are existing features, not a reason to add new provider integrations. No provider integrations or backend are added by this work.
6. Download pause/resume/cancel and destinations have automated coverage only in part; cancelled/invalid destination, accessibility, long sessions, manual Windows 10/11 behavior and device-flow real accounts remain unverified.
7. Current appearance uses centralized palettes but lacks a documented icon convention, pressed/focus states and thorough contrast/keyboard checks. No independent security audit or accessibility certification exists.
8. The site is already responsive, theme-aware, static and truthful about development artifacts; the screenshot is a real Linux window with a staged local page. The website must not be changed to claim new production capabilities. Architecture documentation incorrectly says CI has never run.

This is an engineering audit of the available source and test environment, not a full interactive Windows or independent security review.

## Changes and remaining verification

The review branch addresses findings 1–4 with original Qt-rendered icons, accessible names, menu fallback for narrow widths, theme-aware scheme indicators, real back/forward enabled state, per-tab progress and empty-state messages. `smoke_chrome.py` tests local navigation, action states, themes, labels, Ctrl+L and widths of 1180/760/540 pixels; `smoke_empty_states.py` checks actual empty and filtered management dialogs. A genuine Linux screenshot with a local sample page replaced the previous screenshot. This does not establish production readiness, screen-reader compatibility, interactive Windows behavior, complete contrast coverage or a performance improvement. Windows PR CI was added to test the PR head; consult its actual result rather than inferring success. No provider features or backend have been added.
