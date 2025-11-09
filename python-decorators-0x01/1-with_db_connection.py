#!/usr/bin/env python3
import sqlite3 
import functools
from typing import Callable, Any
import sys

def with_db_connection(func: Any) -> Callable:
    """
    Opens a database, pass it to a function and then closes it
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            return func(conn, *args, **kwargs)   
        except sqlite3.Error as e:
            print(f"Databse error: {func.__name__}:{e}", file=sys.stderr)
            return None
        finally:
            if conn:
                conn.close()
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 
#### Fetch user by ID with automatic connection handling 
if __name__ == '__main__':
    user = get_user_by_id(user_id=1)
    print(user)