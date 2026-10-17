# Security, privacy and data governance

## Implemented local controls

- Synthetic-only generator and explicit demo disclaimers.
- Loopback binding by default, host/origin checks, restrictive CSP, `nosniff`, frame and referrer protections.
- Pydantic `extra="forbid"` validation, bounded transaction fields, a 1 MB / 1,000-row CSV batch limit, and no arbitrary file path API.
- Report reads require the local analyst key; confirmation of fraud requires the admin key; state-changing routes require CSRF.
- Keys are generated locally or supplied through paired environment variables, stored with owner-only permissions, and never logged by the application.
- CSV export escapes formula-leading text; reports contain synthetic features and analyst notes only.

## Residual risk and governance

The local HMAC protects artifact integrity but is not a production key-management system. `joblib` can execute code when loading an untrusted file, so only trusted local artifacts may be loaded. There is no production authentication/RBAC, external secret manager, signed release trust chain, fairness review, incident response, or independent security assessment. Connecting this demo to real financial decisions would require legal/privacy review, bias and drift monitoring, human oversight, access control and a governed data source.

No banking endpoint, payment rail, Telegram message, or automatic account/card block is called by the application.
