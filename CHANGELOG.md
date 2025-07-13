# Change Summary: Security Vulnerability Fixes

This document summarizes the security vulnerabilities that were identified and fixed in the repository.

---

## `test_simulation_files/api_endpoints.py`

### 1. Command Injection
- **Vulnerability:** The `search` endpoint was vulnerable to command injection via the `file:` parameter, allowing an attacker to execute arbitrary shell commands.
- **Fix:** Replaced the insecure `subprocess.run` call with a safe file-reading operation using Python's built-in `open()` function.
- **Why:** This ensures that user input is treated as a filename and not as a command to be executed, preventing remote code execution.

### 2. Cross-Site Scripting (XSS)
- **Vulnerability:** The `search` endpoint was vulnerable to reflected XSS because it directly rendered user input in the HTML response without sanitization.
- **Fix:** Applied the `markupsafe.escape()` function to the user-provided query before rendering it.
- **Why:** This neutralizes any embedded HTML or script tags, preventing them from being executed by the browser and protecting users from session theft or other malicious actions.

### 3. Broken Access Control in Admin Panel
- **Vulnerability:** The `/api/admin` endpoint had no authentication or authorization checks, allowing any user to access administrative functions.
- **Fix:** Implemented a decorator (`@require_auth`) that enforces an authentication check before allowing access to the endpoint.
- **Why:** This restricts access to sensitive administrative functionality to only authenticated and authorized users.

### 4. Path Traversal on File Upload
- **Vulnerability:** The `upload_file` endpoint was vulnerable to path traversal, allowing an attacker to write files to arbitrary locations on the server.
- **Fix:** Used the `werkzeug.utils.secure_filename()` function to sanitize user-provided filenames.
- **Why:** This function removes directory traversal characters (like `../`), ensuring that files can only be saved in the intended upload directory.

### 5. Insecure Server Configuration
- **Vulnerability:** The Flask application was running in debug mode with a hardcoded secret key and was bound to all network interfaces (`0.0.0.0`).
- **Fix:**
    - Disabled debug mode (`DEBUG = False`).
    - Loaded the `SECRET_KEY` from an environment variable.
    - Changed the host to `127.0.0.1`.
- **Why:** These changes are critical for production security. They prevent the exposure of sensitive debug information, protect the session cookie's integrity, and limit the application's network exposure.

---

## `test_simulation_files/auth_manager.py`

### 1. Insecure Deserialization
- **Vulnerability:** The `deserialize_user_data` function used `pickle`, which can lead to arbitrary code execution when deserializing untrusted data.
- **Fix:** Replaced `pickle.loads()` with the safe alternative, `json.loads()`.
- **Why:** JSON is a simple data interchange format and does not have the ability to execute code, which eliminates the risk of remote code execution from malicious serialized data.

### 2. SQL Injection
- **Vulnerability:** The `login` function used f-string formatting to build an SQL query, making it vulnerable to SQL injection.
- **Fix:** Converted the query to a parameterized query, passing user input as a separate parameter to the `cursor.execute()` method.
- **Why:** Parameterized queries ensure that user input is treated as data, not as executable SQL code, which is the standard and most effective way to prevent SQL injection attacks.

### 3. Weak Password Hashing
- **Vulnerability:** The `login` function used the cryptographically broken MD5 algorithm for hashing passwords.
- **Fix:** Replaced `hashlib.md5()` with the much stronger `hashlib.sha256()`.
- **Why:** MD5 is prone to collisions and is considered insecure for password storage. SHA256 is a modern, secure hashing algorithm that makes it significantly more difficult for an attacker to recover passwords from a compromised database.

### 4. Weak Session ID Generation
- **Vulnerability:** Session IDs were generated using a predictable MD5 hash of the username and password.
- **Fix:** Used `os.urandom(16).hex()` to generate cryptographically secure, random session IDs.
- **Why:** This makes session IDs unpredictable and protects against session hijacking and fixation attacks.

### 5. Insecure Password Reset
- **Vulnerability:** The `reset_password` function lacked rate limiting and security logging.
- **Fix:**
    - Added a simple time-based rate-limiting check.
    - Added a `logging.info()` call to record when a password reset is initiated.
- **Why:** Rate limiting helps prevent brute-force attacks, and logging provides an essential audit trail for detecting and investigating suspicious activity.

### 6. Broken Access Control in User Profile
- **Vulnerability:** The `get_user_profile` function allowed any authenticated user to retrieve the profile of any other user.
- **Fix:** Added an authorization check to ensure the ID of the user requesting the profile matches the ID of the profile being requested.
- **Why:** This enforces proper data ownership and privacy, ensuring that users can only access their own information.
