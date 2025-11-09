#!/usr/bin/env python3
"""
0-databaseconnection.py
Class-based context manager: DatabaseConnection
Automatically opens and closes SQLite connection.
"""

import sqlite3
import sys
from typing import Optional


class DatabaseConnection:
    """
    Custom context manager for SQLite database connections.
    Opens connection in __enter__, closes in __exit__.
    """
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        """
        Called when entering 'with' block.
        Returns the active database connection.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"[DB] Connected to {self.db_path}", file=sys.stderr)
            return self.conn
        except sqlite3.Error as e:
            print(f"[DB] Failed to connect to {self.db_path}: {e}", file=sys.stderr)
            raise

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Always called on exit – closes the connection.
        Returns False → let exceptions propagate.
        """
        if self.conn:
            try:
                self.conn.close()
                print(f"[DB] Connection to {self.db_path} closed.", file=sys.stderr)
            except Exception:
                pass
        return False  # Do not suppress exceptions


# ------------------------------------------------------------------
# DEMO: Use with 'with' statement to run SELECT * FROM users
# ------------------------------------------------------------------
if __name__ == "__main__":
    with DatabaseConnection() as conn:
        cursor = conn.cursor()          
        cursor.execute("SELECT * FROM users")  
        rows = cursor.fetchall()

        print("\nAll users:")
        for row in rows:
            print(f"  {row}")