# Integration status

The workspace opens the seven official websites. GitHub public repository and issue search uses the official REST API without authentication. An experimental GitHub OAuth device flow can verify account identity after external OAuth app configuration. It has mock tests only and has not been verified with a real account. Other provider API operations and connections are not implemented. GitHub public search requires no app registration or account; searches and your IP address are sent to GitHub and are subject to its rate limits.

| Service | Current behavior | Planned research before implementation |
|---|---|---|
| Dropbox | Website shortcut | Official OAuth/app registration, minimal scopes, file APIs and revocation. |
| Google Drive | Website shortcut | Official Google OAuth, Drive API scopes, verification and access model. |
| Google Docs | Website shortcut | Official Docs API and Google consent; use the official editor where appropriate. |
| Linear | Website shortcut | Official OAuth, GraphQL, scopes and rate limits. |
| Notion | Website shortcut | Official public integration OAuth and explicitly shared resources. |
| GitHub | Website shortcut; unauthenticated public repository and issue search; experimental session-only device authorization and identity verification (mock-tested, external configuration required) | Official device or OAuth flow, minimum permissions and rate limits. |
| Supabase | Website shortcut | Optional backend only; verify current Free plan and implement RLS and explicit opt-in if justified. |

Before coding, confirm each provider's current documentation and supported desktop authorization; use PKCE/state/redirect validation where supported. Where confidential credentials are required, implement an appropriately secured backend or leave the feature unimplemented. Do not paste credentials into source or chats. Provider-specific approval and verification may be required. GitHub public search was tested with mock response/unit tests and an unauthenticated live query. GitHub device authorization was tested only with mocked responses; no real account authorization has been verified. Official documentation: https://docs.github.com/en/rest/search/search and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api.

## GitHub experimental device authorization

1. The project owner registers a GitHub OAuth app and enables its device flow in GitHub developer settings. Review the [official device flow instructions](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps).
2. Set the **public client ID**, not a client secret or personal token, as `DOTX_GITHUB_CLIENT_ID` in the process environment before launching DOTX. For PowerShell use `$env:DOTX_GITHUB_CLIENT_ID = '<public client ID>'`. `.env.example` is documentation only and is not loaded automatically.
3. In Workspace → GitHub account, select Connect. Open the official verification page, enter the displayed code and explicitly consent to `read:user`. DOTX verifies the account with GitHub before showing it as connected.
4. Tokens are session-only in process memory: they are not saved to ordinary settings, the cloud, logs, or a credential store. Users must reauthorize after exit. No refresh-token or persistent-account support exists. Select Disconnect locally to forget the session; revoke the grant separately via GitHub account settings.

Known limitations: the flow was tested with mocked Qt network responses only. It has not been verified with a real GitHub OAuth registration or account, and it exposes no private repositories, writes, or account sync. If GitHub rejects or revokes a token, reauthorize; rate limits and network errors are reported. Do not put client secrets or tokens in the environment file or source.
