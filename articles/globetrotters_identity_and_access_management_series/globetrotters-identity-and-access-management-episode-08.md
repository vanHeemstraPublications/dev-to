---
title: "Globetrotters IAM 🌍 Ep.8"
part: 8
published: false
description: "Episode 8: All series roads lead here — the Test Factory Secure Interface Enablement solution arriving at LDAP LB-T. Two authentication paths: direct LDAPS bind and OAuth via RWT. The complete entry flow, the implementation decisions, the operational runbook, and the security controls that keep test traffic in its lane."
tags: [iam, ldap, security, testing]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/globetrotters_identity_and_access_management_series/globetrotters-identity-and-access-management-episode-08.png"
series: "Globetrotters Identity and Access Management Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: The Dedicated Test Lane

> *“The freight inspection lane exists so that commercial shipments can be processed systematically, without disrupting the flow of passenger traffic. Every border has one. Every well-designed IAM topology has the equivalent.”*

-----

## Everything Converges Here 🏁

Seven episodes have mapped every layer of ACME’s IAM stack — the immigration ministry (SailPoint), the border kiosk (RWT), the border officer (IDV), the filing cabinet (LDAP), the checkpoint dispatcher (LDAP LB-T), and the sealed diplomatic pouches (PKI/TLS/mTLS).

This episode is the arrival. The Test Factory Secure Interface Enablement solution approaches the checkpoint. LDAP LB-T — explicitly marked as the **Starting Point** in ACME’s SVG — is the dedicated test lane. This episode explains exactly how we use it: the connection flow, the two authentication paths, the implementation requirements, and the operational runbook that keeps the lane open.

-----

## 🗂️ SIPOC — The Dedicated Test Lane

|**Suppliers**           |**Inputs**                                              |**Process**                                                                       |**Outputs**                                                    |**Customers**                                              |
|------------------------|--------------------------------------------------------|----------------------------------------------------------------------------------|---------------------------------------------------------------|-----------------------------------------------------------|
|Secrets vault           |Service account password for `svc-testfactory-prod`     |Retrieve credential at runtime → use for LDAP bind → discard from memory after use|An authenticated LDAP session                                  |Test execution logic — can now perform directory lookups   |
|ACME Root CA trust store|`acme-root-ca.crt` installed in the container image     |TLS validation of LDAP LB-T’s server certificate during handshake                 |Verified, encrypted LDAPS channel                              |LDAP bind + search operations                              |
|SailPoint PRD           |Provisioned group memberships for `svc-testfactory-prod`|Group objects in `ou=groups,dc=gmf,dc=acme,dc=com` contain our service account DN |`memberOf: grp-testfactory`, `memberOf: grp-ldap-bind-t`       |Every authorisation decision based on this account’s groups|
|LDAP LB-T (GMF PRD)     |Incoming LDAPS connection from Test Factory             |TLS termination → backend selection → proxy to city-a or city-b                   |Directory query responses: bind success/failure, search results|Test Factory — receives identity resolution results        |

-----

## The Two Authentication Paths: A Decision at the Checkpoint 🛤️

ACME’s IAM topology and our solution’s architecture support two paths from the Test Factory to the identity infrastructure. They serve different purposes and are used in different scenarios.

### Path A: Direct LDAP Bind (Primary Path)

```
┌──────────────────┐  LDAPS :636  ┌──────────────────┐  LDAP  ┌──────────────────┐
│  Test Factory    │ ────────────► │  GMF PRD         │ ──────► │  AUTH GMF PRD    │
│  Scenario Exec   │              │  LDAP LB-T       │        │  city-a / city-b │
│  Container       │              │  ★ START HERE    │        │  (gds-city-a/b)  │
└──────────────────┘              └──────────────────┘        └──────────────────┘

Steps:
  1. Retrieve service account password from secrets vault
  2. Open LDAPS connection to LDAP LB-T on port 636
  3. Verify LDAP LB-T certificate against ACME Root CA trust store
  4. Bind: DN=uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
           Password=[from vault]
  5. Perform LDAP searches as needed for test setup/verification
  6. Unbind and close the session
```

**When to use Path A:**

- Service account authentication for test execution infrastructure
- Group membership lookups for test data setup
- Any operation requiring direct directory access as a machine identity
- The default path for all test infrastructure authentication

**Advantages:** Simpler, lower latency, no token management overhead, well-understood failure modes.

### Path B: OAuth Bearer Token (Secondary Path, Future)

```
┌──────────────────┐  HTTPS    ┌──────────────────┐
│  Test Factory    │ ─────────► │  RWT PRD         │
│  Scenario Exec   │ POST /token│  (OAuth Server)  │
│  Container       │ ◄───────── │                  │
│                  │  JWT token └──────────────────┘
│                  │
│                  │  HTTPS + Bearer token
│                  │ ─────────────────────────────────────►  Protected SUT API
│                  │                                         │
│                  │                                         ▼
│                  │                                      IDV PRD validates token
│                  │                                      against LDAP
└──────────────────┘
```

**When to use Path B:**

- SUT interfaces that require Bearer token authentication (not mTLS or direct LDAP)
- When ACME mandates OAuth for machine-to-machine communication
- If the JWT authorisation layer is expanded to integrate with RWT

**Prerequisites for Path B:**

1. OAuth client registration in RWT (client_id + secret, provisioned by SailPoint)
1. “Test Factory Operator” role includes the required OAuth scopes (`test:execute`, `vault:read`)
1. Token acquisition and refresh logic implemented in the test framework
1. IDV reachable from the SUT’s network segment

-----

## The Complete Entry Flow: Path A Step by Step 🔄

This is the authoritative flow for our primary authentication path:

```
Test Factory Container Startup
│
├── Step 1: Load trust store
│   ACME Root CA certificate loaded from /etc/ssl/acme/acme-root-ca.crt
│   (baked into container image; must be kept current with CA rotations)
│
├── Step 2: Retrieve service account credential
│   HTTP GET https://vault.acme.com/v1/secret/testfactory/ldap-bind
│   Response: { "username": "svc-testfactory-prod", "password": "..." }
│   Store in memory only — do not write to filesystem or environment variable
│
├── Step 3: Establish LDAPS connection to LDAP LB-T
│   DNS: ldap-lb-t.gmf.acme.com → 10.x.x.x
│   TCP connect → port 636
│   TLS handshake:
│     Server presents: ldap-lb-t.gmf.acme.com cert → Keyfactor CA → ACME Root CA
│     Client verifies: chain valid ✓, not expired ✓, hostname match ✓
│   TLS session established
│
├── Step 4: LDAP bind
│   BIND request:
│     DN:       uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com
│     Password: [from vault, presented over TLS]
│   LDAP LB-T proxies bind to AUTH GMF PRD city-a (or city-b)
│   AUTH GMF PRD verifies credential against stored password hash
│   Response: resultCode=0 (Success)
│   Credential cleared from memory immediately after bind
│
├── Step 5: Test-time LDAP operations (as required)
│   SEARCH (uid=test-user-001) → verify target user exists and has correct groups
│   SEARCH (cn=grp-testfactory) → verify our service account is still a member
│   Additional searches per test scenario requirements
│
└── Step 6: Unbind and close
    UNBIND request sent
    TCP connection closed
    LDAP LB-T session terminated
```

-----

## Implementation: Code That Respects the Architecture 💻

The following patterns apply to any language. Python with `ldap3` is shown as the reference implementation.

### Secure LDAP connection with trust store validation

```python
import ssl
import ldap3
from pathlib import Path

LDAP_LB_T_HOST     = "ldap-lb-t.gmf.acme.com"
LDAP_LB_T_PORT     = 636
LDAP_BASE_DN       = "dc=gmf,dc=acme,dc=com"
LDAP_SERVICE_DN    = "uid=svc-testfactory-prod,ou=services,dc=gmf,dc=acme,dc=com"
ACME_ROOT_CA_PATH  = "/etc/ssl/acme/acme-root-ca.crt"


def create_ldap_connection(password: str) -> ldap3.Connection:
    """
    Establish an authenticated LDAPS connection to GMF PRD LDAP LB-T.

    The connection:
    - Verifies the server certificate against ACME Root CA
    - Binds using the Test Factory service account
    - Never persists the password beyond this function scope
    """
    if not Path(ACME_ROOT_CA_PATH).exists():
        raise RuntimeError(
            f"ACME Root CA certificate not found at {ACME_ROOT_CA_PATH}. "
            "Container image may be missing the trust bundle."
        )

    tls_config = ldap3.Tls(
        ca_certs_file=ACME_ROOT_CA_PATH,
        validate=ssl.CERT_REQUIRED,        # mandatory — no skipping verification
        version=ssl.PROTOCOL_TLS_CLIENT,
        check_hostname=True,               # mandatory — hostname must match cert SAN
    )

    server = ldap3.Server(
        LDAP_LB_T_HOST,
        port=LDAP_LB_T_PORT,
        use_ssl=True,
        tls=tls_config,
        connect_timeout=10,               # 10s TCP connect timeout
        get_info=ldap3.NONE,              # do not fetch server schema on connect
    )

    conn = ldap3.Connection(
        server,
        user=LDAP_SERVICE_DN,
        password=password,
        authentication=ldap3.SIMPLE,
        receive_timeout=15,               # 15s per operation timeout
        raise_exceptions=True,            # raise LDAPException on failure
    )

    conn.bind()   # raises ldap3.core.exceptions.LDAPBindError on failure
    return conn


def verify_service_account_groups(conn: ldap3.Connection) -> list[str]:
    """
    After binding, verify our service account has the expected group memberships.
    Returns the list of groups found.
    """
    conn.search(
        search_base=LDAP_BASE_DN,
        search_filter="(uid=svc-testfactory-prod)",
        search_scope=ldap3.SUBTREE,
        attributes=["memberOf", "accountStatus"],
    )

    if not conn.entries:
        raise RuntimeError("Service account not found in directory — provisioning issue.")

    entry = conn.entries[0]

    if str(entry.accountStatus) != "active":
        raise RuntimeError(
            f"Service account is not active: {entry.accountStatus}. "
            "Contact operations to check SailPoint deprovisioning status."
        )

    member_of = [str(g) for g in entry.memberOf]
    return member_of
```

### Retrieving the credential from the vault (never hardcoded)

```python
import httpx


def retrieve_ldap_password(vault_url: str, vault_token: str) -> str:
    """
    Retrieve the LDAP service account password from the secrets vault.

    The password is never stored in:
    - Source code
    - Configuration files committed to source control
    - Environment variables (visible in process listings)
    - Logs (redact before logging)
    """
    response = httpx.get(
        f"{vault_url}/v1/secret/testfactory/ldap-bind",
        headers={"X-Vault-Token": vault_token},
        timeout=10.0,
        verify=ACME_ROOT_CA_PATH,          # vault also uses ACME CA-signed cert
    )
    response.raise_for_status()
    return response.json()["data"]["password"]
```

### LDAP error handling

```python
import ldap3.core.exceptions as ldap_exc


def safe_ldap_bind(host: str, password: str) -> ldap3.Connection:
    try:
        return create_ldap_connection(password)

    except ldap_exc.LDAPSocketOpenError as e:
        # TCP connection failed — LB-T may be unreachable
        raise RuntimeError(
            f"Cannot connect to LDAP LB-T at {host}:636. "
            f"Check network connectivity and that LDAP LB-T is operational. "
            f"Details: {e}"
        ) from e

    except ldap_exc.LDAPCertificateError as e:
        # TLS certificate validation failed
        raise RuntimeError(
            f"LDAP LB-T certificate validation failed. "
            f"Check that ACME Root CA at {ACME_ROOT_CA_PATH} is current. "
            f"Details: {e}"
        ) from e

    except ldap_exc.LDAPBindError as e:
        # Authentication failed — wrong password, account disabled, or DN wrong
        raise RuntimeError(
            f"LDAP bind failed for {LDAP_SERVICE_DN}. "
            f"Verify: 1) credential is current in vault, "
            f"2) account is not disabled in directory, "
            f"3) account DN is correct. "
            f"Details: {e}"
        ) from e
```

-----

## Security Controls for the Test Lane 🔒

The following controls must be in place before our solution connects to LDAP LB-T in any environment:

|Control                 |Requirement                                                                                                         |Verification                                      |
|------------------------|--------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
|**Credential storage**  |Service account password stored in secrets vault only — never in source code, environment variables, or config files|Code review + secrets scanning in CI pipeline     |
|**TLS validation**      |`CERT_REQUIRED` + `check_hostname=True` — no exceptions                                                             |Automated test with expired/invalid cert must fail|
|**Trust store currency**|ACME Root CA certificate current and not expired                                                                    |Certificate expiry monitoring alert               |
|**Read-only LDAP**      |Service account has no write permissions on the directory                                                           |ACL review by ACME operations team                |
|**Group membership**    |`grp-ldap-bind-t` membership confirms we are authorised to bind via the T lane                                      |Post-bind group verification in health check      |
|**Session cleanup**     |LDAP sessions unbound and TCP connections closed when not in use                                                    |Connection pool max-idle settings                 |
|**Credential rotation** |Service account password rotated on schedule                                                                        |SailPoint / Keyfactor automation                  |

-----

## Operational Runbook: When Things Go Wrong 📋

### LDAP bind failure (LDAP ResultCode 49)

```
Symptom:  LDAPBindError: invalidCredentials (49)
Cause:    1) Service account password in vault is stale (SailPoint rotated it)
          2) Account was disabled by SailPoint deprovisioning
          3) Wrong DN in configuration
Immediate: Check vault for current credential. Compare DN against directory.
Escalate:  Contact ACME operations if account is disabled — SailPoint may have
           triggered deprovisioning; requires re-provisioning event.
```

### TLS certificate error

```
Symptom:  LDAPCertificateError: certificate verify failed
Cause:    1) ACME Root CA certificate in container image is expired or wrong CA
          2) LDAP LB-T server certificate has expired
          3) Hostname mismatch (connect to IP, cert expects hostname)
Immediate: Check acme-root-ca.crt in container against current CA cert.
           Verify connection uses hostname, not IP address.
Escalate:  If LDAP LB-T cert is expired — ACME operations, Keyfactor team.
```

### Cannot connect to LDAP LB-T (TCP timeout)

```
Symptom:  LDAPSocketOpenError: connection refused / timeout
Cause:    1) Network path from container to LDAP LB-T blocked (firewall)
          2) LDAP LB-T offline (both city-a and city-b down)
          3) Wrong hostname / port in configuration
Immediate: Verify connectivity: nc -zv ldap-lb-t.gmf.acme.com 636
           Check DNS resolves to correct IP.
Escalate:  If both DC backends down — ACME infrastructure team, P1 incident.
```

### Group membership missing after bind

```
Symptom:  grp-ldap-bind-t not in memberOf after successful bind
Cause:    SailPoint provisioning has not completed for our service account
          OR access certification campaign revoked the group membership
Immediate: Verify current group memberships in LDAP directly.
           Check SailPoint for recent provisioning events on this account.
Escalate:  ACME IAM operations team to re-provision or re-certify access.
```

-----

## The Complete Series: Every Layer Connected 🗺️

Looking back across all eight episodes through the lens of our Test Factory solution:

|Episode|IAM layer                                             |Our solution’s dependency                                   |
|-------|------------------------------------------------------|------------------------------------------------------------|
|1      |ACME topology overview                                |Understanding the full stack before we connect              |
|2      |SailPoint: provisioning, deprovisioning, certification|Our service account lifecycle; certification cycle awareness|
|3      |RWT: OAuth tokens, bearer token lifecycle             |Future OAuth path if SUT requires Bearer auth               |
|4      |IDV: token-to-LDAP bridge, attribute resolution       |In our OAuth path; validates our token against LDAP         |
|5      |LDAP directories: objects, groups, LDAPS              |The directory our service account lives in                  |
|6      |LDAP LB-T: load balancing, HA, test isolation         |**Our starting point** — the door we walk through           |
|7      |PKI: TLS, mTLS, certificates, trust chains            |Prerequisite for every secure connection we make            |
|8      |*This one* — Test Factory entry                       |The complete integrated picture                             |

-----

## There and Back Again: The Globetrotter’s Journey Complete 🌍

A traveller crossing a border does not think about the visa database, the CA that signed the stamp, the load balancer that selected the immigration officer, or the token service that backs the officer’s terminal. They see: queue, desk, check, stamp, through.

The seamlessness is the point. Every layer we have examined exists to make the crossing fast, secure, and reliable — so that the traveller (our Test Factory solution) can present its credentials and be waved through, every time, with confidence on both sides.

The dedicated test lane is open. The filing cabinet is accurate. The seals are genuine. The dispatcher knows the way. The officer has the record.

**The Test Factory is cleared for entry.**

-----

**🔗 Resources**

- **ldap3 Python library**: [ldap3.readthedocs.io](https://ldap3.readthedocs.io)
- **LDAP connection security (RFC 4513)**: [rfc-editor.org/rfc/rfc4513](https://www.rfc-editor.org/rfc/rfc4513)
- **Secrets management (HashiCorp Vault)**: [developer.hashicorp.com/vault/docs](https://developer.hashicorp.com/vault/docs)
- **OAuth 2.0 Client Credentials (machine-to-machine)**: [rfc-editor.org/rfc/rfc6749#section-4.4](https://www.rfc-editor.org/rfc/rfc6749#section-4.4)

-----

*🌍 Globetrotters Identity and Access Management Series — crossing the IAM border one checkpoint at a time, using ACME’s SailPoint, RWT, IDV, and LDAP topology as the map.*
