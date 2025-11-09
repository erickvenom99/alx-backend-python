#!/usr/bin/env python3
import sqlite3 
import functools
from typing import Callable, Any
import sys

def with_db_connection(func: Any) -> Callable:
    """
    """
    @functools.wraps(func)
    def wrapper(*arg: Any, **kwargs: Any):
        conn = None
        try: 
            conn = sqlite3.connect('users.db')
            result = func(conn, *arg, **kwargs)
            return result
        except sqlite3.Error as e:
            print(f"Databse error: {func.__name__}:{e}")
            return None
        finally:
            if conn:
                conn.close()
    return wrapper
    
def transactional(func: Any) -> Callable:
    """
    The transaction decorator function raises on error rollback otherwise 
    it commit the transaction
    """
    @functools.wraps(func)
    def wrapper(conn: sqlite3.Connection, *args: Any, **kwargs: Any) -> int:
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"[TRANSACTION] COMMIT successful for {func.__name__}.")
            return result

        except Exception as e:
            conn.rollback()
            print(f"[TRANSACTION] ROLLBACK executed for {func.__name__} due to error: {e}", file=sys.stderr)
            return None
    return wrapper



@with_db_connection 
@transactional 
def update_user_email(conn: sqlite3.Connection, user_id: int, new_email: str): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

if __name__ == "__main__":
#### Update user's email with automatic transaction handling 
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')