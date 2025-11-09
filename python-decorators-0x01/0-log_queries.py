#!/usr/bin/env python3
"""
0-log_queries.py
Reusable decorator that logs every SQL query to stderr.
"""

import sqlite3
import functools
import sys
from typing import Callable, Any


def log_queries(func: Callable) -> Callable:
    """
    Decorator: prints the SQL query before executing the wrapped function.
    The query can be passed as:
      - the first positional argument, or
      - a keyword argument named ``query``.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        query = None

        # Look in kwargs first
        if 'query' in kwargs:
            query = kwargs['query']

        # Then in positional args (first one)
        elif args:
            query = args[0]

        # Log it
        if query:
            print(f"[SQL LOG] Executing query: {query}", file=sys.stderr)

        # Run the original function
        return func(*args, **kwargs)

    return wrapper


@log_queries
def fetch_all_users(query: str):
    """
    Execute any SELECT query and return the rows.
    """
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

#### fetch users while logging the query
if __name__ == '__main__':
    print("--- Running 0_log_queries.py Demo ---")
    
    # Test 1: Query passed as a positional argument
    print("\n=== Test 1: All Users ===")
    # This query will be logged to stderr
    users = fetch_all_users("SELECT * FROM users")
    for u in users:
        print(u)

    # Test 2: Query passed as a keyword argument
    print("\n=== Test 2: Users > 40 ===")
    # This query will also be logged to stderr
    older = fetch_all_users(query="SELECT name, age, email FROM users WHERE age > 40")
    for u in older:
        print(u)