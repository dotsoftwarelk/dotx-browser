# Baseline audit and delivery evidence

## Starting state

The workspace contained no project or Git repository. The requested GitHub connector reported `unsupported`; no repository URL or archive was supplied. A new local Git repository was initialized on `main`. There were no existing commits, branches, release evidence, UI, workflow, changes or tests to audit. No prior DOTX version can be inferred.

## Work performed

A small PySide6/Qt WebEngine prototype and static multipage site were created from scratch. The site is a conceptual design, not a screenshot; its download page states that no installer is available. There is no provider API adapter, OAuth, token store, Supabase backend, database migration, cloud account, or automatic update system. Workspace actions are ordinary website links, not connections.

## Local verification (Linux sandbox)

- `PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v`: 7 tests passed (address normalization, malformed state and local state persistence).
- `python scripts/build_site.py` and `python scripts/check_site.py`: 11 pages generated; relative local paths and basic metadata passed.
- `python -m compileall -q desktop scripts`: passed.
- `QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 QTWEBENGINE_CHROMIUM_FLAGS='--disable-gpu' PYTHONPATH=desktop python scripts/smoke_desktop.py`: passed local HTTP navigation, window construction, tab creation/closure, bookmark, history, tab duplication, zoom, state file and an off-the-record private profile. Sandboxing was disabled **only for this container test**, not in product code. Graphics fallback warnings occurred in this headless environment.

Not tested: real-provider authorization, website in a full browser or mobile layouts, live external links, deployment, accessibility audit, certificate failure behavior, downloads on Windows, permission handling, multi-tab load/performance, recovery, or Windows installation and uninstallation. Static checks do not prove visual correctness or runtime behavior.

## Priority gaps

1. A threat model and independent security review; explicit per-origin permission UI; additional private-browsing verification and comprehensive data deletion.
2. Secure, provider-specific OAuth implementation with official documented flows, OS credential storage and mock/real-account tests. None currently exists.
3. Browser completeness: startup/session restoration, bookmark folders, complete download manager, popup/window handling, more settings, accessibility and robust failure handling.
4. Windows CI, actual installer, signed or clearly unsigned release, checksums, clean-install/upgrade/uninstall testing.
5. Link the site to real release metadata and a verified support/security contact. Configure and verify Pages deployment.
6. Decide whether optional Supabase sync is justified; design schema, RLS, retention and opt-in only if implemented.

## Delivery state

Development source only. A GitHub repository, `dotsoftwarelk/dotx-browser`, was created and the prototype was pushed to `main`. After the owner authorized public visibility, GitHub Pages was enabled, and a Pages workflow for commit `984e311` succeeded; the homepage returned HTTP 200 at https://dotsoftwarelk.github.io/dotx-browser/. No pull request or release has been made. All acceptance checkboxes requiring Windows, provider API, or production verification remain unmet.
