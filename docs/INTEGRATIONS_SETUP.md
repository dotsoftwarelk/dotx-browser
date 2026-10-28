# Integration status

The workspace opens the seven official websites. GitHub public repository search also uses the official REST API without authentication; no user account is connected. Other provider API operations are not implemented. There are no client IDs, callbacks, scopes, provider credentials, data operations, account status indicators or token storage in this prototype. No setup can enable authenticated provider connections yet. GitHub public search requires no app registration or account; searches and your IP address are sent to GitHub and are subject to its rate limits.

| Service | Current behavior | Planned research before implementation |
|---|---|---|
| Dropbox | Website shortcut | Official OAuth/app registration, minimal scopes, file APIs and revocation. |
| Google Drive | Website shortcut | Official Google OAuth, Drive API scopes, verification and access model. |
| Google Docs | Website shortcut | Official Docs API and Google consent; use the official editor where appropriate. |
| Linear | Website shortcut | Official OAuth, GraphQL, scopes and rate limits. |
| Notion | Website shortcut | Official public integration OAuth and explicitly shared resources. |
| GitHub | Website shortcut; public repository search via REST, unauthenticated | Official device or OAuth flow, minimum permissions and rate limits. |
| Supabase | Website shortcut | Optional backend only; verify current Free plan and implement RLS and explicit opt-in if justified. |

Before coding, confirm each provider's current documentation and supported desktop authorization; use PKCE/state/redirect validation where supported. Where confidential credentials are required, implement an appropriately secured backend or leave the feature unimplemented. Do not paste credentials into source or chats. Provider-specific approval and verification may be required. GitHub public search was tested with mock response/unit tests and an unauthenticated live query; no provider account authorization has been implemented or verified. Official documentation: https://docs.github.com/en/rest/search/search and https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api.
