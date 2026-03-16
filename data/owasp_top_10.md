# OWASP Top 10 - 2021 Security Guidelines

## A01:2021 - Broken Access Control
Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of all data or performing a business function outside the user's limits.

### Common Vulnerabilities
- Violation of the principle of least privilege or deny by default, where access should only be granted for particular capabilities, roles, or users, but is available to anyone.
- Bypassing access control checks by modifying the URL (parameter tampering or force browsing), internal application state, or the HTML page, or by using an attack tool modifying API requests.
- Permitting viewing or editing someone else's account, by providing its unique identifier (insecure direct object references - IDOR).

### Secure Coding Example
**Vulnerable Python Code (Flask):**
```python
@app.route('/user/<int:user_id>/profile')
def get_profile(user_id):
    # Vulnerable: No check if the logged-in user is authorized to view this user_id
    user = db.session.query(User).get(user_id)
    return render_template('profile.html', user=user)
```

**Secure Python Code (Flask):**
```python
@app.route('/user/<int:user_id>/profile')
@login_required
def get_profile(user_id):
    # Secure: Verify the requested user_id matches the logged-in user's ID
    if current_user.id != user_id and not current_user.is_admin:
        abort(403) # Forbidden
    user = db.session.query(User).get(user_id)
    return render_template('profile.html', user=user)
```

---

## A03:2021 - Injection
Injection flaws, such as SQL, NoSQL, OS command, Object Relational Mapping (ORM), LDAP, and Expression Language (EL) or Object Graph Navigation Library (OGNL) injection, occur when untrusted data is sent to an interpreter as part of a command or query.

### Common Vulnerabilities
- User-supplied data is not validated, filtered, or sanitized by the application.
- Dynamic queries or non-parameterized calls without context-aware escaping are used directly in the interpreter.
- Hostile data is used within object-relational mapping (ORM) search parameters to extract additional, sensitive records.

### Secure Coding Example
**Vulnerable Python Code (sqlite3):**
```python
def get_user_by_name(username):
    # Vulnerable: String concatenation allows SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "';"
    cursor.execute(query)
    return cursor.fetchall()
```

**Secure Python Code (sqlite3):**
```python
def get_user_by_name(username):
    # Secure: Use parameterized queries to prevent SQL Injection
    query = "SELECT * FROM users WHERE username = ?;"
    cursor.execute(query, (username,))
    return cursor.fetchall()
```

---

## A07:2021 - Identification and Authentication Failures
Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks.

### Common Vulnerabilities
- Permits brute force or credential stuffing attacks.
- Permits default, weak, or well-known passwords, such as "Password123" or "admin/admin".
- Uses weak or ineffective credential recovery and forgotten-password processes.
- Exposes session identifiers in the URL or does not rotate session IDs after successful login.

### Secure Coding Example
**Vulnerable Python Code (Password Hashing):**
```python
import hashlib

def hash_password(password):
    # Vulnerable: MD5 is not mathematically secure for passwords and lacks a salt
    return hashlib.md5(password.encode()).hexdigest()
```

**Secure Python Code (Password Hashing):**
```python
import bcrypt

def hash_password(password):
    # Secure: bcrypt automatically generates a salt and is designed to be computationally expensive
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)
```

---

## A02:2021 - Cryptographic Failures
Failures related to cryptography (or lack thereof) often lead to exposing sensitive data. This includes transmitting unencrypted sensitive data over the internet or using weak/deprecated cryptographic algorithms (e.g., MD5, SHA1).
*   **Fix:** Always use TLS (Transport Layer Security) for transmitting data and use strong encryption algorithms like AES-GCM (Advanced Encryption Standard).

## A04:2021 - Insecure Design
Focuses on risks related to design flaws. If an application is designed without security in mind (e.g., missing threat modeling or missing secure architectural patterns), perfect implementation will not save it.
*   **Fix:** Implement shift-left security, threat modeling, and reference architectures during project planning, not just coding.

## A05:2021 - Security Misconfiguration
Security misconfiguration is the most common vulnerability. It happens when default settings are used, verbose error messages are displayed to users, or unnecessary features/ports are enabled.
*   **Fix:** Ensure hardening across all layers (network, OS, application) and use automated deployment pipelines to enforce secure configurations (such as disabling debug mode in production).

## A06:2021 - Vulnerable and Outdated Components
Occurs when software uses older versions of libraries, frameworks, and other modules that have known vulnerabilities (e.g., Log4Shell). 
*   **Fix:** Continuously monitor dependencies using tools like `dependabot` or OpenVAS, and regularly patch/update packages.

## A08:2021 - Software and Data Integrity Failures
Relates to software getting deployed or updated without verifying its integrity, such as unverified CI/CD pipelines or deserializing untrusted data.
*   **Fix:** Ensure software signatures are verified, and use safe serialization formats (like JSON) instead of unsafe ones (like Python `pickle`).

## A09:2021 - Security Logging and Monitoring Failures
When an attacker breaches an application, a lack of logging means the security team won't find out until it's too late. The average time to detect a breach is over 200 days due to missing logs.
*   **Fix:** Ensure all login access, failures, and high-value transactions are logged, and that logs are stored securely (e.g., using a centralized SIEM tool like Splunk or ELK).

## A10:2021 - Server-Side Request Forgery (SSRF)
Occurs when a web application fetches a remote resource without validating the user-supplied URL. It allows an attacker to force the application to send a crafted request to an unexpected destination (like the internal AWS metadata API at `169.254.169.254`).
*   **Fix:** Use an allow-list of approved URLs/domains and enforce network segmentation to prevent the app from reaching internal-only networks.
