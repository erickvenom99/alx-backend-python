#!/usr/bin/env python3
"""
Reusable context manager
"""
import sys
import sqlite3
from typing import Optional, List, Any, Tuple

class ExecuteQuery:
    """
    Reusable custom context manager that accepts query and param
    and returns query result
    Args:
        db_name: string - database name
        query: string - SQL commands string
        param: Any - parameter for the query
    Return: list of result
    """
    def __init__(self, db_name: str, query: str, param: Any = None):
        self.db_name = db_name
        self.query = query
        self.param = (param,) if param is not None else ()
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.result: Optional[List[Tuple]] = None

    def __enter__(self) -> List[Tuple]:
        try:
            self.conn = sqlite3.connect(self.db_name)
            print(f"[DB] Connected to Database {self.db_name}", file=sys.stderr)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.query, self.param)
            self.result = self.cursor.fetchall()
            return self.result
        except sqlite3.Error as e:
            print(f"[DBERROR] Request failed: {self.query}, {self.param} {e}", file=sys.stderr)
            self.__exit__(None, e, None)
            raise

    def __exit__(self, ex_type, ex_value, traceback):
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.conn:
            try:
                self.conn.close()
                print(f"[DB] Database {self.db_name} closed", file=sys.stderr)
            except Exception:
                pass
        return False