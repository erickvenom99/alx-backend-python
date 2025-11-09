#!/usr/bin/env python3
"""
Fixed: with_db_connection + retry_on_failure
Uses existing users.db — NO DB CREATION
"""

import time
import sqlite3
import functools
import sys
from typing import Callable, Any, List


def with_db_connection(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            return func(conn, *args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error: {func.__name__}: {e}", file=sys.stderr)
            return None
        finally:
            if conn:
                conn.close()
    return wrapper


def retry_on_failure(retries: int = 3, delay: int = 2) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            remaining = retries
            last_exc = None
            while remaining > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    remaining -= 1
                    if remaining > 0:
                        print(f"Operation failed: {e}. Retrying in {delay}s... ({remaining} left)", file=sys.stderr)
                        time.sleep(delay)
                    else:
                        print("All retries failed.", file=sys.stderr)
                        raise last_exc
            return None
        return wrapper
    return decorator


# CORRECT: conn is injected by with_db_connection → DO NOT accept it
@with_db_connection
@retry_on_failure(retries=4, delay=1)
def fetch_users_with_retry(conn: sqlite3.Connection) -> List[tuple]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # CORRECT CALL: NO conn needed!
    users = fetch_users_with_retry()
    print("Users:")
    for user in users:
        print(f"  {user}")