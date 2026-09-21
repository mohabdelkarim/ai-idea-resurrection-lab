# RFC: feat: LDAP User management

1. Summary
Add LDAP authentication and user management to Open WebUI. The proposal introduces an LDAPAuthProvider that implements the existing AuthProvider interface, a Fastify plugin to hook into the login flow, a Zod‑based configuration schema, and a periodic sync job to reconcile LDAP groups with Open‑WebUI roles. The implementation uses the pure‑JavaScript ldapjs v3 client (TypeScript typed) and integrates with the fastify-auth ecosystem introduced in 2026.

2. Motivation
Open WebUI is increasingly adopted in enterprise environments where a single source of truth for user identities is required. Currently the platform only supports local password login and OAuth providers, forcing enterprises to maintain duplicate credential stores or to build ad‑hoc integrations. Adding first‑class LDAP support will:
- Reduce operational overhead by leveraging existing directory services (Active Directory, OpenLDAP, FreeIPA).
- Enable role‑based access control (RBAC) through LDAP groups, aligning with corporate policies.
- Improve security posture by eliminating password reuse and centralising authentication audits.
- Position Open WebUI as a viable component in zero‑trust architectures that mandate directory‑based identity.
The recent maturation of ldapjs (v3, pure‑JS, full TS typings) and the fastify-auth LDAP strategy remove previous technical blockers (native bindings, lack of typings). Additionally, Zod now offers robust schema validation for complex connection objects, simplifying secure configuration handling.

3. Detailed Design
**3.1. Configuration**
- Add a new section `ldap` to the existing `config.yaml` with fields: `host` (string, URL), `bindDN` (string), `bindPassword` (string, secret), `searchBase` (string), `searchFilter` (string, default `(uid={{username}})`), `groupBase` (optional), `groupFilter` (optional), `roleMapping` (map of LDAP group DN to Open‑WebUI role).
- Validate the section at startup using a Zod schema; reject the process if validation fails.

**3.2. LDAPAuthProvider**
- Create `src/auth/ldapAuthProvider.ts` implementing `AuthProvider` with methods:
  * `initialize(): Promise<void>` – creates an ldapjs client, binds with service credentials, and caches the connection.
  * `authenticate(username: string, password: string): Promise<User>` – searches for the user DN using `searchFilter`, attempts a bind with the supplied password, and on success maps LDAP attributes (`cn`, `mail`, `memberOf`) to the Open‑WebUI `User` model. Throws on failure.
  * `syncUsers(): Promise<void>` – walks `searchBase` (and optionally `groupBase`) to fetch all users and groups, updates/creates corresponding records in the Open‑WebUI database, and applies `roleMapping`.
- All I/O uses async/await; errors are wrapped in a custom `LDAPError` for consistent handling.

**3.3. Fastify Plugin**
- File `src/plugins/ldapAuthPlugin.ts` registers a pre‑handler on the `/login` route. If the request body contains `authMethod: "ldap"`, the handler invokes `LDAPAuthProvider.authenticate` and, on success, creates a session token via the existing session manager.
- The plugin also registers the background job using `fastify-cron` with a default interval of 6 hours to call `syncUsers`.

**3.4. Role Mapping**
- During `syncUsers`, each LDAP group DN found in `memberOf` is looked up in `roleMapping`. Corresponding Open‑WebUI roles are assigned to the user record. Unmapped groups are ignored but logged for audit.

**3.5. Security Considerations**
- Service bind credentials are stored only in environment variables and never written to logs.
- LDAP connections are forced to use TLS (`ldaps://` or StartTLS) unless explicitly overridden for testing.
- Rate‑limit login attempts per IP using the existing fastify-rate-limit plugin to mitigate brute‑force attacks.

4. Drawbacks
- Introduces a new runtime dependency (`ldapjs`) and additional configuration surface, increasing the maintenance burden.
- LDAP sync jobs can be heavy on large directories; careful indexing and pagination are required to avoid performance degradation.
- Misconfiguration (e.g., overly permissive search filters) could expose the entire directory to enumeration attacks.
- Enterprises must ensure network connectivity to the LDAP server, which may involve firewall changes.

5. Alternatives
- **External Reverse Proxy Authentication**: Deploy an Nginx or Traefik layer that performs LDAP auth and forwards a signed JWT to Open WebUI. This removes LDAP code from the repo but adds operational complexity and reduces tight integration with role mapping.
- **OAuth2 Bridge**: Use Azure AD or Keycloak as an OAuth provider that fronts LDAP. Simpler for organizations already using those services, but it requires additional infrastructure and does not cover on‑prem LDAP deployments.
- **Custom Scripted Sync Only**: Provide a CLI tool that periodically imports LDAP users into the local database without runtime authentication. This would lack real‑time login capability and be less seamless.

6. Unresolved Questions
- How should we handle LDAP password policies (e.g., password expiration) that might affect login attempts? Should we surface specific error codes to the UI?
- What is the optimal pagination strategy for very large directories (e.g., >100k users) to keep sync jobs within the typical 30‑second request timeout?
- Should we support multiple LDAP providers simultaneously (e.g., primary AD and secondary OpenLDAP) and how would conflict resolution be defined?
- Are there any compliance requirements (e.g., GDPR) that dictate how LDAP‑derived personal data must be stored or purged within Open WebUI?
- Finally, we need to decide on a version‑gate: expose the feature behind a `--enable-ldap` flag until sufficient testing in production environments validates stability.

---

*RFC generated by Resurrection Bot 🧬*
