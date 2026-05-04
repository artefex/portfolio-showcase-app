# Sanitization Summary

This repository is a sanitized public portfolio version of a private
implementation.

Removed or replaced:

- Client/project identifiers.
- Private brief/process documents.
- Brand assets and default template assets.
- `.env` files and generated caches.
- Private deployment/analytics references.

Verified:

- No committed `.env` files.
- No hardcoded API keys or credentials.
- No private domains or client-identifying copy.
- No client-identifying or secret material in retained screenshots.
- Backend tests pass.
- Frontend lint, typecheck, tests, and build pass.

Remaining notes:

- API keys are required only through local environment variables.
- Frontend transitive dependency audit warnings were documented but not
  auto-fixed during sanitization to avoid broad dependency churn in this
  portfolio version.
- Screenshots should be regenerated if the UI changes.
- No open-source license is included.
