# Python Security Vulnerabilities

## Injection Vulnerabilities

### 1. SQL Injection

**Problem**: User input concatenated directly into SQL queries

```python
# CRITICAL: SQL Injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Attacker input: "admin' OR '1'='1"
# Results in: SELECT * FROM users WHERE username = 'admin' OR '1'='1'

# Good: Use parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))

# Good: Use ORM
def get_user(username):
    return db.query(User).filter_by(username=username).first()
```

### 2. Command Injection

**Problem**: User input passed to shell commands

```python
# CRITICAL: Command injection
import os
import subprocess

# Bad
def ping_host(hostname):
    os.system(f"ping -c 1 {hostname}")

# Attacker input: "google.com; rm -rf /"

# Good: Avoid shell=True, use list arguments
def ping_host(hostname):
    subprocess.run(["ping", "-c", "1", hostname], check=True, capture_output=True)

# Better: Validate input against allowlist
import re

def ping_host(hostname):
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        raise ValueError("Invalid hostname")
    subprocess.run(["ping", "-c", "1", hostname], check=True, capture_output=True)
```

### 3. Path Traversal

**Problem**: User-controlled file paths without validation

```python
# CRITICAL: Path traversal vulnerability
import os

# Bad
def read_user_file(filename):
    path = f"/var/data/{filename}"
    with open(path) as f:
        return f.read()

# Attacker input: "../../etc/passwd"
# Reads: /var/data/../../etc/passwd -> /etc/passwd

# Good: Use pathlib and validate
from pathlib import Path

def read_user_file(filename):
    base_dir = Path("/var/data")
    file_path = (base_dir / filename).resolve()

    # Ensure the resolved path is within base_dir
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid file path")

    return file_path.read_text()
```

### 4. Code Injection (eval/exec)

**Problem**: Using `eval()` or `exec()` on user input

```python
# CRITICAL: Code injection
# Bad
def calculate(expression):
    return eval(expression)

# Attacker input: "__import__('os').system('rm -rf /')"

# Good: Use ast.literal_eval for safe evaluation of literals only
import ast

def calculate(expression):
    # Only allows literals like numbers, strings, lists, dicts
    return ast.literal_eval(expression)

# Better: Use a proper expression parser or restricted environment
# For math expressions, use a library like sympy or numexpr
```

## Deserialization Vulnerabilities

### 5. Unsafe Pickle Usage

**Problem**: Unpickling untrusted data can execute arbitrary code

```python
# CRITICAL: Arbitrary code execution
import pickle

# Bad
def load_data(data):
    return pickle.loads(data)

# Attacker can craft malicious pickle data to execute code

# Good: Use JSON for untrusted data
import json

def load_data(data):
    return json.loads(data)

# If you must use pickle, sign the data
import hmac
import hashlib

SECRET_KEY = b"your-secret-key"

def safe_pickle_loads(data):
    signature = data[:32]
    pickled_data = data[32:]
    expected_sig = hmac.new(SECRET_KEY, pickled_data, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    return pickle.loads(pickled_data)
```

### 6. YAML Unsafe Loading

**Problem**: `yaml.load()` can execute arbitrary Python code

```python
# CRITICAL: Arbitrary code execution
import yaml

# Bad
def load_config(yaml_string):
    return yaml.load(yaml_string)

# Attacker input: "!!python/object/apply:os.system ['rm -rf /']"

# Good: Use safe_load
def load_config(yaml_string):
    return yaml.safe_load(yaml_string)
```

## Cryptography Issues

### 7. Weak or No Encryption

**Problem**: Using weak algorithms or not encrypting sensitive data

```python
# Bad: Weak hash for passwords
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Bad: Weak hash with salt (still too fast)
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Good: Use bcrypt or argon2 for passwords
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
```

### 8. Hardcoded Secrets

**Problem**: Secrets in source code

```python
# CRITICAL: Exposed credentials
# Bad
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# Good: Use environment variables
import os

API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

# Better: Use a secrets manager
# from cloud_secrets import get_secret
# API_KEY = get_secret("api_key")
```

### 9. Insecure Random Number Generation

**Problem**: Using `random` module for security-sensitive operations

```python
# Bad: Predictable tokens
import random
import string

def generate_token():
    return ''.join(random.choices(string.ascii_letters, k=32))

# Good: Use secrets module
import secrets

def generate_token():
    return secrets.token_urlsafe(32)
```

## Web Application Vulnerabilities

### 10. Cross-Site Scripting (XSS)

**Problem**: Rendering untrusted data without escaping

```python
# Bad: Flask without auto-escaping
from flask import Flask

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return f"<h1>Results for: {query}</h1>"

# Attacker input: "<script>alert('XSS')</script>"

# Good: Use template engine with auto-escaping (Jinja2)
from flask import render_template_string

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return render_template_string("<h1>Results for: {{ query }}</h1>", query=query)
```

### 11. Open Redirect

**Problem**: Redirecting to user-controlled URLs

```python
# Bad: Open redirect
from flask import redirect, request

@app.route("/redirect")
def redirect_user():
    url = request.args.get("url")
    return redirect(url)

# Attacker: /redirect?url=http://evil.com

# Good: Validate redirect URL against allowlist
from urllib.parse import urlparse

ALLOWED_HOSTS = ["example.com", "www.example.com"]

@app.route("/redirect")
def redirect_user():
    url = request.args.get("url")
    parsed = urlparse(url)
    if parsed.netloc not in ALLOWED_HOSTS:
        return "Invalid redirect", 400
    return redirect(url)
```

### 12. Missing Authentication/Authorization

**Problem**: Endpoints without proper access controls

```python
# Bad: No authentication
@app.route("/admin/delete_user/<user_id>")
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    return "Deleted"

# Good: Require authentication and authorization
from functools import wraps
from flask import session

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return "Unauthorized", 401
        user = User.query.get(session["user_id"])
        if not user or not user.is_admin:
            return "Forbidden", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/delete_user/<user_id>")
@require_admin
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    return "Deleted"
```

### 13. Server-Side Request Forgery (SSRF)

**Problem**: Making requests to user-controlled URLs

```python
# Bad: SSRF vulnerability
import requests

def fetch_url(url):
    response = requests.get(url)
    return response.text

# Attacker input: "http://localhost/admin" or "http://169.254.169.254/metadata"

# Good: Validate URL and block private IPs
import ipaddress
from urllib.parse import urlparse

BLOCKED_SCHEMES = ["file", "gopher", "data"]
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
]

def fetch_url(url):
    parsed = urlparse(url)

    # Block dangerous schemes
    if parsed.scheme in BLOCKED_SCHEMES:
        raise ValueError("Invalid URL scheme")

    # Resolve hostname and check if it's private
    import socket
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValueError("Private IP address not allowed")
    except socket.gaierror:
        raise ValueError("Invalid hostname")

    response = requests.get(url, timeout=5)
    return response.text
```

## Race Conditions

### 14. Time-of-Check to Time-of-Use (TOCTOU)

**Problem**: File operations with check-then-use pattern

```python
# Bad: Race condition
import os

def write_user_file(filename, content):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(content)

# Between exists() and open(), file could be created by attacker

# Good: Use atomic operations
def write_user_file(filename, content):
    # Use 'x' mode to fail if file exists (atomic)
    try:
        with open(filename, "x") as f:
            f.write(content)
    except FileExistsError:
        raise ValueError("File already exists")
```

## Information Disclosure

### 15. Verbose Error Messages

**Problem**: Exposing internal details in error messages

```python
# Bad: Leaking implementation details
from flask import jsonify

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc()
    }), 500

# Good: Generic error messages in production
import os

@app.errorhandler(Exception)
def handle_error(e):
    # Log the full error internally
    app.logger.error(f"Error: {e}", exc_info=True)

    # Return generic message to user
    if os.environ.get("ENV") == "production":
        return jsonify({"error": "Internal server error"}), 500
    else:
        # Show details in development only
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
```

### 16. Logging Sensitive Data

**Problem**: Logging passwords, tokens, or PII

```python
# Bad: Logging sensitive data
import logging

def login(username, password):
    logging.info(f"Login attempt: {username} / {password}")
    # ...

def process_payment(card_number, cvv):
    logging.info(f"Processing card: {card_number}, CVV: {cvv}")
    # ...

# Good: Redact sensitive data
def login(username, password):
    logging.info(f"Login attempt: {username}")
    # ...

def process_payment(card_number, cvv):
    masked = f"{card_number[:4]}...{card_number[-4:]}"
    logging.info(f"Processing card: {masked}")
    # ...
```

## Denial of Service

### 17. Regex Denial of Service (ReDoS)

**Problem**: Regular expressions with catastrophic backtracking

```python
# Bad: Vulnerable to ReDoS
import re

def validate_input(text):
    # This regex has catastrophic backtracking on inputs like "aaaaaaaaaaaaaaaaaaX"
    pattern = r"^(a+)+$"
    return re.match(pattern, text) is not None

# Good: Use simpler regex or set timeout
import regex  # Third-party regex module with timeout support

def validate_input(text):
    pattern = r"^a+$"  # Simpler, equivalent pattern
    return re.match(pattern, text) is not None

# Or with timeout
def validate_input_safe(text):
    pattern = r"^(a+)+$"
    try:
        return regex.match(pattern, text, timeout=1) is not None
    except TimeoutError:
        return False
```

### 18. Unbounded Resource Consumption

**Problem**: No limits on user-controlled resource usage

```python
# Bad: No size limit on upload
@app.route("/upload", methods=["POST"])
def upload_file():
    file_data = request.data
    # Attacker can upload multi-GB file
    with open("upload.bin", "wb") as f:
        f.write(file_data)

# Good: Set limits
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

@app.route("/upload", methods=["POST"])
def upload_file():
    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return "File too large", 413
    file_data = request.data
    with open("upload.bin", "wb") as f:
        f.write(file_data)
```

## Review Checklist

When reviewing code, check for:

- [ ] No user input concatenated into SQL, shell commands, or file paths
- [ ] Parameterized queries or ORM for database access
- [ ] No `eval()`, `exec()`, `pickle.loads()`, or `yaml.load()` on untrusted data
- [ ] Secrets loaded from environment variables or secrets manager
- [ ] `secrets` module used for security tokens, not `random`
- [ ] bcrypt/argon2 used for password hashing, not MD5/SHA
- [ ] Input validation on all user-controlled data
- [ ] Authentication and authorization on sensitive endpoints
- [ ] Template engines with auto-escaping for HTML output
- [ ] URL validation for redirects and SSRF prevention
- [ ] Resource limits on uploads and operations
- [ ] Generic error messages in production
- [ ] No sensitive data in logs
- [ ] Atomic operations instead of check-then-use patterns
