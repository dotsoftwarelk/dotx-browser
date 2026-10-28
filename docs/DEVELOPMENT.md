# Development

Install a supported Python version and `requirements.txt`. Qt WebEngine has substantial native dependencies, which vary by OS and desktop environment. Run from `desktop` with `python -m dotx`. Test UI-independent logic with `PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v`. Generate and validate the site using the commands in README.

The headless smoke test requires PySide6, Qt native system libraries, and a working WebEngine environment. A restricted Linux container may need `QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu PYTHONPATH=desktop python scripts/smoke_desktop.py`. Disabling Chromium sandbox protections is **only** for isolated CI testing, not regular use or release builds.

Dependencies are constrained but not lockfile-pinned. Establish a tested lock strategy and security update process before release.
