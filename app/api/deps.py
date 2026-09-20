"""
API Dependencies and Security Injections.
"""
from typing import Generator
import sqlite3
from app.core.database import db

def get_db_read():
    """Provides a thread-safe read-only connection to the WAL database."""
    conn = db.get_read_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_db():
    """Provides access to the global high-concurrency database instance."""
    return db
