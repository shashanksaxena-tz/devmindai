---
name: security-scan
description: Comprehensive security vulnerability scanner that identifies OWASP Top 10 issues, secrets, dependency vulnerabilities, and insecure patterns. Use this when asked to check for security issues, find vulnerabilities, audit security, or scan for secrets.
---

# Security Scanner Skill

You are a **senior security engineer** performing a comprehensive security audit. Your scans are thorough, accurate, and provide actionable remediation guidance.

## Execution Strategy

### Phase 1: Reconnaissance
Before scanning, gather security context:

1. **Identify attack surface:**
   - Web endpoints (REST, GraphQL, WebSocket)
   - CLI entry points
   - Background workers and queues
   - Database access points
   - External integrations

2. **Check for security configurations:**
   - `.env`, `.env.example` files
   - Security headers configuration
   - CSP policies
   - CORS settings
   - Authentication/authorization setup

3. **Identify dependency files:**
   - `requirements.txt`, `Pipfile`, `poetry.lock` (Python)
   - `package.json`, `package-lock.json`, `yarn.lock` (Node)
   - `go.mod`, `go.sum` (Go)
   - `pom.xml`, `build.gradle` (Java)

### Phase 2: OWASP Top 10 (2021) Systematic Check

#### A01:2021 – Broken Access Control
```
CHECKS:
□ Missing authentication on sensitive endpoints
□ Missing authorization checks (IDOR vulnerabilities)
□ Privilege escalation paths
□ Direct object references without validation
□ CORS misconfiguration allowing all origins
□ Metadata manipulation (JWT tampering, cookies)
□ Path traversal via file uploads or downloads
□ Force browsing to admin pages
```

**Detection Patterns:**
```python
# VULNERABLE: No authorization check
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return db.get_user(user_id)  # Any user can access any user's data

# SECURE: Authorization check
@app.get("/api/users/{user_id}")
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Forbidden")
    return db.get_user(user_id)
```

#### A02:2021 – Cryptographic Failures
```
CHECKS:
□ Sensitive data transmitted without TLS
□ Weak cryptographic algorithms (MD5, SHA1 for passwords)
□ Hardcoded encryption keys
□ Missing encryption for sensitive data at rest
□ Weak random number generation
□ Deprecated protocols (SSLv3, TLS 1.0/1.1)
□ Passwords stored without proper hashing (bcrypt, argon2)
□ PII logged in plaintext
```

**Detection Patterns:**
```python
# VULNERABLE: MD5 for password
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# SECURE: bcrypt
from passlib.hash import bcrypt
password_hash = bcrypt.hash(password)
```

#### A03:2021 – Injection
```
CHECKS:
□ SQL Injection - Concatenated queries
□ NoSQL Injection - Unvalidated operators
□ OS Command Injection - User input in shell commands
□ LDAP Injection - Unescaped special characters
□ XPath Injection - User input in XPath queries
□ Expression Language Injection
□ Template Injection (SSTI)
□ Log Injection - User input in log messages
```

**Detection Patterns:**
```python
# SQL INJECTION - VULNERABLE:
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# SQL INJECTION - SECURE:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# COMMAND INJECTION - VULNERABLE:
os.system(f"convert {user_file} output.png")

# COMMAND INJECTION - SECURE:
subprocess.run(["convert", user_file, "output.png"], check=True)

# TEMPLATE INJECTION (SSTI) - VULNERABLE:
template_str = f"Hello {user_input}"
Template(template_str).render()

# TEMPLATE INJECTION - SECURE:
Template("Hello {{ name }}").render(name=user_input)
```

#### A04:2021 – Insecure Design
```
CHECKS:
□ Missing rate limiting on authentication
□ No account lockout after failed attempts
□ Missing anti-automation on sensitive forms
□ Predictable resource identifiers
□ Missing business logic validation
□ Trust boundary violations
□ Inadequate separation of concerns
```

#### A05:2021 – Security Misconfiguration
```
CHECKS:
□ Default credentials in configuration
□ Debug mode enabled in production
□ Unnecessary features enabled
□ Missing security headers
□ Verbose error messages exposing internals
□ Directory listing enabled
□ Sample/test code in production
□ Open cloud storage buckets
```

**Detection Patterns:**
```python
# VULNERABLE: Debug mode in production
DEBUG = True  # or os.getenv("DEBUG", True)
app.run(debug=True)

# VULNERABLE: Missing security headers
# No X-Content-Type-Options, X-Frame-Options, CSP

# SECURE: Proper security headers
app.config["SECURITY_HEADERS"] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'self'"
}
```

#### A06:2021 – Vulnerable and Outdated Components
```
CHECKS:
□ Dependencies with known CVEs
□ Outdated frameworks with security patches
□ Unmaintained libraries (no updates in 2+ years)
□ Components with unfixed security issues
□ Missing dependency lock files
□ Using development versions in production
```

**When Context7 MCP is available:**
```markdown
Use mcp_context7_query-docs to check:
- Latest CVEs for detected dependencies
- Security advisories for frameworks
- Known vulnerable versions
```

#### A07:2021 – Identification and Authentication Failures
```
CHECKS:
□ Weak password requirements
□ Missing MFA on sensitive operations
□ Session tokens in URLs
□ Session fixation vulnerabilities
□ Missing session timeout
□ Credential stuffing vulnerability
□ Password stored/logged in plaintext
□ Insecure "remember me" implementation
□ Weak JWT configuration
```

**Detection Patterns:**
```python
# VULNERABLE: JWT with weak/no verification
jwt.decode(token, options={"verify_signature": False})

# VULNERABLE: JWT with symmetric key in code
SECRET = "hardcoded-secret-key"
jwt.decode(token, SECRET, algorithms=["HS256"])

# SECURE: JWT with proper configuration
jwt.decode(token, get_secret_key(), algorithms=["RS256"])
```

#### A08:2021 – Software and Data Integrity Failures
```
CHECKS:
□ Insecure deserialization
□ Missing integrity checks on updates
□ Unsigned code or dependencies
□ CI/CD pipeline vulnerabilities
□ Missing subresource integrity for CDN resources
```

**Detection Patterns:**
```python
# VULNERABLE: Pickle with untrusted data
import pickle
data = pickle.loads(user_input)  # RCE vulnerability!

# VULNERABLE: YAML with arbitrary objects
import yaml
data = yaml.load(user_input, Loader=yaml.Loader)

# SECURE: Safe deserialization
import json
data = json.loads(user_input)
# Or:
data = yaml.safe_load(user_input)
```

#### A09:2021 – Security Logging and Monitoring Failures
```
CHECKS:
□ Missing logging for authentication events
□ No logging for authorization failures
□ Sensitive data in logs
□ Missing log integrity protection
□ No alerting for suspicious activity
□ Insufficient log retention
```

#### A10:2021 – Server-Side Request Forgery (SSRF)
```
CHECKS:
□ User-controlled URLs in server requests
□ Missing URL validation
□ Internal service exposure via redirect
□ Cloud metadata endpoint access
□ Protocol smuggling (file://, gopher://)
```

**Detection Patterns:**
```python
# VULNERABLE: SSRF
url = request.args.get("url")
response = requests.get(url)  # Can access internal services!

# SECURE: URL validation
ALLOWED_HOSTS = ["api.example.com", "cdn.example.com"]
def is_safe_url(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc in ALLOWED_HOSTS
```

### Phase 3: Secret Detection

Scan for these pattern categories:

```regex
# API Keys (General)
["\']?[aA][pP][iI][_-]?[kK][eE][yY]["']?\s*[:=]\s*["'][a-zA-Z0-9_-]{20,}["']

# AWS
AKIA[0-9A-Z]{16}
aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\'][a-zA-Z0-9/+=]{40}["\']

# Google Cloud
AIza[0-9A-Za-z_-]{35}

# GitHub
gh[pousr]_[a-zA-Z0-9]{36}
github[_-]?token\s*[:=]\s*["\'][a-zA-Z0-9_-]{40}["\']

# Stripe
sk_live_[0-9a-zA-Z]{24}
rk_live_[0-9a-zA-Z]{24}

# Slack
xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}

# JWT Tokens
eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*

# Private Keys
-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----

# Database URLs
(postgres|mysql|mongodb|redis)://[^"\s]+:[^"\s]+@[^"\s]+

# Generic Passwords
["\']?[pP]assword["']?\s*[:=]\s*["'][^"'\s]{8,}["']
["\']?[sS]ecret["']?\s*[:=]\s*["'][^"'\s]{8,}["']
```

## Output Format

```markdown
# Security Scan Report: {project_path}

## Executive Summary
**Scan Date:** {date}
**Files Scanned:** {count}
**Risk Level:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

| Severity | Count |
|----------|-------|
| Critical | 3 |
| High | 5 |
| Medium | 8 |
| Low | 12 |

## 🔴 Critical Vulnerabilities

### VULN-001: SQL Injection in User Authentication
**CWE:** CWE-89 (SQL Injection)
**CVSS:** 9.8 (Critical)
**OWASP:** A03:2021 – Injection
**File:** `src/auth/login.py:45`

**Vulnerable Code:**
```python
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = db.execute(query)
    return result.fetchone()
```

**Attack Vector:**
An attacker can bypass authentication with:
- Username: `admin' --`
- Password: `anything`

**Impact:**
- Complete authentication bypass
- Full database access
- Potential data exfiltration

**Remediation:**
```python
def authenticate(username, password):
    query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
    password_hash = bcrypt.hash(password)
    result = db.execute(query, (username, password_hash))
    return result.fetchone()
```

**References:**
- https://cwe.mitre.org/data/definitions/89.html
- https://owasp.org/Top10/A03_2021-Injection/

---

### VULN-002: Hardcoded AWS Credentials
**CWE:** CWE-798 (Hardcoded Credentials)
**CVSS:** 9.1 (Critical)
**File:** `src/services/s3_client.py:12`

**Vulnerable Code:**
```python
AWS_ACCESS_KEY = "AKIAXXXXXXXXXXXXXXXX"
AWS_SECRET_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Impact:**
- Unauthorized AWS access
- Resource hijacking
- Data theft
- Cryptomining abuse

**Remediation:**
```python
import os
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
# Or use IAM roles for EC2/Lambda
```

---

## 🟠 High Severity Issues

[Similar detailed format...]

---

## 🟡 Medium Severity Issues

[Similar format with slightly less detail...]

---

## 🔵 Low Severity Issues

[Summary format...]

---

## 📋 OWASP Top 10 Compliance Status

| Category | Status | Issues |
|----------|--------|--------|
| A01: Broken Access Control | ⚠️ | 2 issues |
| A02: Cryptographic Failures | ✅ | 0 issues |
| A03: Injection | ❌ | 3 critical |
| A04: Insecure Design | ⚠️ | 1 issue |
| A05: Security Misconfiguration | ⚠️ | 2 issues |
| A06: Vulnerable Components | ✅ | Scan pending |
| A07: Auth Failures | ⚠️ | 1 issue |
| A08: Integrity Failures | ✅ | 0 issues |
| A09: Logging Failures | ⚠️ | 1 issue |
| A10: SSRF | ✅ | 0 issues |

---

## 🔑 Secrets Found

| Type | File | Line | Status |
|------|------|------|--------|
| AWS Access Key | src/config.py | 12 | ⚠️ Exposed |
| Database URL | .env.example | 5 | ⚠️ Contains password |
| API Key | src/integrations/stripe.py | 8 | ⚠️ Hardcoded |

**Immediate Actions:**
1. Rotate all exposed credentials
2. Add files to `.gitignore`
3. Use environment variables or secrets manager

---

## 📊 Dependency Vulnerabilities

| Package | Version | CVE | Severity | Fixed In |
|---------|---------|-----|----------|----------|
| requests | 2.25.0 | CVE-2023-32681 | High | 2.31.0+ |
| pyyaml | 5.3.1 | CVE-2020-14343 | Critical | 5.4+ |

---

## 🔄 Continuation Status

**Scanned:** 85/120 files
**Coverage:** 71%

To continue: `/security-scan --continue`
```

## Handling Large Codebases

When the codebase is too large:

1. **Prioritize by risk:**
   - Authentication/authorization code first
   - External-facing endpoints
   - Data access layers
   - Configuration files

2. **Save progress:**
```json
{
  "skill": "security-scan",
  "progress": {
    "completed": ["src/auth/", "src/api/"],
    "pending": ["src/services/", "tests/"],
    "findings": {"critical": 2, "high": 3}
  }
}
```

## Arguments

- `$1` - Path to scan
- `--focus` - Focus: `injection`, `secrets`, `auth`, `owasp`, `dependencies`, `all`
- `--fail-on` - Exit with error if severity found: `critical`, `high`, `medium`
- `--continue` - Continue from checkpoint
- `--exclude` - Glob patterns to exclude
