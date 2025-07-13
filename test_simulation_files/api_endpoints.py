#!/usr/bin/env python3
import os
import subprocess
from functools import wraps
import requests
from flask import Flask, jsonify, request, abort
from markupsafe import escape
from werkzeug.utils import secure_filename

app = Flask(__name__)

# A05: Security Misconfiguration - Debug mode enabled
app.config["DEBUG"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "a-secure-default-key")  # Hardcoded secret


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Authorization" not in request.headers:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/search", methods=["GET"])
def search():
    """Search endpoint with multiple vulnerabilities"""
    # A03: Injection - XSS vulnerability, no input sanitization
    query = request.args.get("q", "")

    # A03: Injection - Command injection vulnerability
    if "file:" in query:
        filename = query.split("file:")[1]
        try:
            with open(filename, "r") as f:
                return jsonify({"result": f.read()})
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404

    # A10: Server-Side Request Forgery (SSRF)
    if query.startswith("http"):
        # No validation of URL, allows internal network access
        response = requests.get(query)
        return jsonify({"content": response.text})

    # Return search results without output encoding
    return f"<h1>Search Results for: {escape(query)}</h1>"


@app.route("/api/admin", methods=["GET"])
@require_auth
def admin_panel():
    """Admin panel with broken access control"""
    # A01: Broken Access Control - No authentication check
    # Anyone can access admin functionality
    action = request.args.get("action")

    if action == "delete_user":
        user_id = request.args.get("user_id")
        # Performs privileged action without authorization
        return jsonify({"status": "User deleted", "user_id": user_id})

    return jsonify({"status": "Admin panel"})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """File upload with security issues"""
    # A05: Security Misconfiguration - No file type validation
    file = request.files.get("file")
    if file:
        # Saves any file type to server
        filename = secure_filename(file.filename)
        file.save(os.path.join("/tmp", filename))

        # A03: Path traversal vulnerability
        return jsonify({"status": "File uploaded", "path": f"/tmp/{filename}"})

    return jsonify({"error": "No file provided"})


# A06: Vulnerable and Outdated Components
# Using old Flask version with known vulnerabilities (hypothetical)
# requirements.txt: Flask==0.12.2 (known security issues)

if __name__ == "__main__":
    # A05: Security Misconfiguration - Running on all interfaces
    app.run(host="127.0.0.1", port=5000, debug=False)
