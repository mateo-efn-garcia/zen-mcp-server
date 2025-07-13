#!/usr/bin/env python3
import hashlib
import json
import sqlite3
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

class AuthenticationManager:
    def __init__(self, db_path="users.db"):
        # A01: Broken Access Control - No proper session management
        self.db_path = db_path
        self.sessions = {}  # In-memory session storage
        self.password_reset_requests = {}

    def login(self, username, password):
        """User login with various security vulnerabilities"""
        # A03: Injection - SQL injection vulnerability
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT id, password_hash FROM users WHERE username = ?"
        cursor.execute(query, (username,))

        user = cursor.fetchone()
        if not user:
            return {"status": "failed", "message": "User not found"}

        # A02: Cryptographic Failures - Weak hashing algorithm
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if user[1] == password_hash:
            # A07: Identification and Authentication Failures - Weak session generation
            session_id = os.urandom(16).hex()
            self.sessions[session_id] = {"user_id": user[0], "username": username}

            return {"status": "success", "session_id": session_id}
        else:
            return {"status": "failed", "message": "Invalid password"}

    def reset_password(self, email):
        """Password reset with security issues"""
        # A04: Insecure Design - No rate limiting or validation
        now = datetime.now()
        if email in self.password_reset_requests and self.password_reset_requests[email] > now - timedelta(minutes=1):
            logging.warning(f"Rate limit exceeded for password reset for email: {email}")
            return {"status": "failed", "message": "Rate limit exceeded. Try again in a minute."}

        reset_token = os.urandom(16).hex()
        self.password_reset_requests[email] = now

        # A09: Security Logging and Monitoring Failures - No security event logging
        logging.info(f"Password reset initiated for email: {email}")
        return {"reset_token": reset_token, "url": f"/reset?token={reset_token}"}

    def deserialize_user_data(self, data):
        """Unsafe deserialization"""
        # A08: Software and Data Integrity Failures - Insecure deserialization
        return json.loads(data)

    def get_user_profile(self, user_id, current_user_id):
        """Get user profile with authorization issues"""
        # A01: Broken Access Control - No authorization check
        if user_id != current_user_id:
            logging.warning(f"User {current_user_id} attempted to access profile of user {user_id}")
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Fetches any user profile without checking permissions
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
