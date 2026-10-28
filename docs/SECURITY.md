# Security

Development prototype, not independently audited or production-ready. Do not use for sensitive browsing. Qt WebEngine default certificate handling is not overridden to accept invalid certificates; the specific certificate-error UX has not been tested. Navigation is restricted to http, https, about, data and blob schemes; this is not a comprehensive browser security review. Per-origin permissions, isolation, external navigation, popup behavior and downloads need a thorough review. Do not run with Chromium sandbox disabled except in an isolated test environment.

No access tokens, API keys or service role keys are needed or stored by DOTX. Website cookies may be retained by Qt WebEngine. History and bookmark URLs can contain sensitive query strings and are saved in plaintext. Logs and crash behavior have not been reviewed for sensitive data. No full private-browsing or clear-all-data controls are implemented. Third-party websites manage their own sessions.

No verified security contact exists yet; the owner must establish a private disclosure channel before publishing. Do not post secrets publicly.
