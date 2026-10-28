# Development

Install a supported Python version and `requirements.txt`. Qt WebEngine has substantial native dependencies, which vary by OS and desktop environment. Run from `desktop` with `python -m dotx`. Test UI-independent logic with `PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v`. Generate and validate the site using the commands in README.

The headless smoke test requires PySide6, Qt native system libraries, and a working WebEngine environment. A restricted Linux container may need `QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu PYTHONPATH=desktop python scripts/smoke_desktop.py`. Disabling Chromium sandbox protections is **only** for isolated CI testing, not regular use or release builds.

Direct runtime and build dependencies are version-pinned, but transitive dependencies and system inputs are not fully locked. Establish a tested lock strategy and security update process before release.

## Optional browser-based website QA

With Playwright for Python and its Chromium runtime installed, run a local server (`python -m http.server 8001 --directory site`) and then `python scripts/test_website_browser.py`. This tests desktop/mobile, theme preference, mock download metadata, the mobile menu and a project-subpath 404. Run `node scripts/test_download_js.js` for deterministic download metadata logic. These optional tests are separate from the desktop suite.
