# Baseline audit and delivery evidence

## Starting state

The workspace contained no project or Git repository. The requested GitHub connector reported `unsupported`; no repository URL or archive was supplied. A new local Git repository was initialized on `main`. There were no existing commits, branches, release evidence, UI, workflow, changes or tests to audit. No prior DOTX version can be inferred.

## Work performed

A small PySide6/Qt WebEngine prototype and static multipage site were created from scratch. The site is a conceptual design, not a screenshot; its download page distinguishes the temporary unsigned development installer from a stable release. An unauthenticated GitHub public-repository search adapter now exists. An experimental GitHub device authorization flow exists with session-only memory token handling and mock tests, but no real account acceptance test. There is no persistent token store, integrated Supabase backend, cloud account, or automatic update system. A pre-existing connected DOTX Supabase project was discovered separately and had a targeted privilege-hardening migration applied; it is not connected to this app. Workspace website shortcuts are not account connections.

## Local verification (Linux sandbox)

- `PYTHONPATH=desktop python -m unittest discover -s desktop/tests -v`: 19 tests passed (address normalization, malformed state, state persistence and GitHub search parsing/error mapping).
- `python scripts/build_site.py` and `python scripts/check_site.py`: 11 pages generated; relative local paths and basic metadata passed.
- `python -m compileall -q desktop scripts`: passed.
- `QT_QPA_PLATFORM=offscreen QTWEBENGINE_DISABLE_SANDBOX=1 QTWEBENGINE_CHROMIUM_FLAGS='--disable-gpu' PYTHONPATH=desktop python scripts/smoke_desktop.py`: passed local HTTP navigation, window construction, tab creation/closure, bookmark, history, tab duplication, zoom, state file and an off-the-record private profile. Sandboxing was disabled **only for this container test**, not in product code. Graphics fallback warnings occurred in this headless environment.

Also tested locally: a Qt download with contents verification, a live unauthenticated public GitHub search through the Qt UI, opt-in session restoration, bookmark editing/import/export, settings controls and user-initiated/unsolicited popup behavior. The exact new source changes require their own Windows CI run; the earlier Windows build predates these features.

Not tested: real-provider authorization, website in a full browser or mobile layouts, accessibility audit, certificate failure behavior, permission handling, multi-tab load/performance, recovery, interactive Windows 10/11 behavior, upgrade behavior and security review. Automated Windows runner source-level download, installation and uninstallation tests passed; live Pages deployment and page URLs returned HTTP 200. Static checks do not prove visual correctness or runtime behavior.

## Priority gaps

1. A threat model and independent security review; explicit per-origin permission UI; additional private-browsing verification and comprehensive data deletion.
2. Provider-specific OAuth, token lifecycle handling, OS credential storage where persistence is needed, and real-account tests. GitHub has an experimental session-only device flow with mock tests; the other providers do not have OAuth implementations.
3. Browser completeness: more extensive session and bookmark management, a complete download manager, site permission settings, accessibility and robust failure handling.
4. Stable Windows release, code signing or clear unsigned status, interactive acceptance, upgrade testing, and sustained performance testing.
5. Link the site to actual stable release metadata when available and add a verified support/security contact.
6. Decide whether optional Supabase sync is justified; design schema, RLS, retention and opt-in only if implemented.

## Delivery state

Development prototype and temporary unsigned build, not a release candidate. A GitHub repository, `dotsoftwarelk/dotx-browser`, was created and the prototype was pushed to `main`. After the owner authorized public visibility, GitHub Pages was enabled, and a Pages workflow for commit `984e311` succeeded; the homepage returned HTTP 200 at https://dotsoftwarelk.github.io/dotx-browser/. No pull request or stable release has been made. Windows development CI for commit `03af4f6` succeeded on a Windows x64 runner and produced an unsigned, temporary artifact; see `WINDOWS_BUILD.md`. Acceptance criteria for stable release readiness, authenticated provider APIs and production security remain unmet.

## Connected Supabase security review

An existing DOTX project had six RLS-enabled tables. Excess authenticated-role TRUNCATE, TRIGGER and REFERENCES privileges were revoked and verified; see `SUPABASE_AUDIT.md`. Owner isolation has not been exercised using two real user accounts and history-sync consent is not yet enforced by this app.
