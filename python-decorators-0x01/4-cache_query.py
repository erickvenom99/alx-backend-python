#!/usr/bin/env python3
import time
import sqlite3 
import functools
from typing import Callable, Any
import sys



query_cache = {}



def cache_query(func: Any) -> Callable:
    @functools.wraps(func)
    def wrapper(conn: Any, query: Any, *args: Any, **kwargs: Any):
        global query_cache
        if query in query_cache:
            print(f"[CACHE HIT] Returning cached result for query: '{query[:40]}...'", file=sys.stderr)
            return query_cache[query]
        print(f"[CACHE MISS] Executing query: '{query[:40]}...'", file=sys.stderr)
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


def with_db_connection(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript(
                """
                CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
                INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');
                """
            )
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()
if __name__ == "__main__":
    #### First call will cache the result
    users = fetch_users_with_cache(query="SELECT * FROM users")

    #### Second call will use the cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")