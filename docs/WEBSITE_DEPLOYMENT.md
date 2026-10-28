# GitHub Pages deployment

The public repository `dotsoftwarelk/dotx-browser` exists and the prototype was pushed to `main`. After owner approval to make the repository public, Pages was enabled and deployed at https://dotsoftwarelk.github.io/dotx-browser/. Do not change repository visibility without owner approval. Select a project license before public distribution. Do not place a token in a Git URL, source file, shell history or chat.

The proposed `.github/workflows/pages.yml` builds and checks the static site, uploads only `site/`, and deploys with GitHub Pages Actions. It runs on pushes to `main` and manual dispatch; change the branch if the actual publishing branch differs. In repository Settings → Pages, select GitHub Actions as source. Enable the appropriate Actions permissions, run the workflow, and check its actual deployment URL. Relative asset/page links are designed to work for a project subpath, but direct navigation, refresh and nested 404 behavior must be verified on the actual host. No custom domain or sitemap is assumed.

Before deployment review every generated asset, metadata and link; add genuine release links and contact details only once verified. GitHub Pages is not a secret store, database, OAuth token exchange or backend. Check GitHub Actions for the current run result; a workflow file or queued run is not proof of deployment.

## Static subpath and build status

`scripts/build_site.py` generates all HTML; edit the generator and rebuild rather than editing generated pages only. The generated custom 404 has an absolute base chosen from `GITHUB_REPOSITORY` during Actions, so deep missing paths resolve under the correct project Pages subpath. For other hosts set `DOTX_PAGES_BASE_PATH` to an absolute directory such as `/project/`. For local root serving the default is `/`.

The download page reads public GitHub Actions run and artifact metadata in the visitor’s browser and selects a successful main-branch run with an unexpired development artifact. GitHub sign-in is required to download the artifact. This is not a stable Release link and is not a backend. If JavaScript, GitHub, or its rate limit prevents the check, the page shows an honest fallback and workflow link. No credentials are included.

The browser screenshot is a real Qt window captured on Linux with a locally staged sample page and temporary test data. See `scripts/capture_screenshot.py`; it is not a Windows screenshot.
