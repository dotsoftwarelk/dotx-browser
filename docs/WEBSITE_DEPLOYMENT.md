# GitHub Pages deployment

No remote repository or deployment has been verified. The owner should create an empty GitHub repository through GitHub, initialize an appropriate license, review the files, commit, configure an authorized Git remote, and push according to the repository's security policy. Do not place a token in a Git URL, source file, shell history or chat.

The proposed `.github/workflows/pages.yml` builds and checks the static site, uploads only `site/`, and deploys with GitHub Pages Actions. It runs on pushes to `main` and manual dispatch; change the branch if the actual publishing branch differs. In repository Settings → Pages, select GitHub Actions as source. Enable the appropriate Actions permissions, run the workflow, and check its actual deployment URL. Relative asset/page links are designed to work for a project subpath, but direct navigation, refresh and nested 404 behavior must be verified on the actual host. No custom domain or sitemap is assumed.

Before deployment review every generated asset, metadata and link; add genuine release links and contact details only once verified. GitHub Pages is not a secret store, database, OAuth token exchange or backend. This workflow has not been run on GitHub.
