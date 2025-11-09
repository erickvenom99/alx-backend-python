#!/usr/bin/env python
from execute_query import ExecuteQuery

print("=== TEST 1: Fetch all users ===")
with ExecuteQuery("users.db", "SELECT * FROM users") as users:
    for user in users:
        print(user)

print("\n=== TEST 2: Users older than 40 ===")
with ExecuteQuery("users.db", "SELECT name, age FROM users WHERE age > ?", 40) as older:
    for user in older:
        print(user)

print("\n=== TEST 3: Invalid query (should show error) ===")
try:
    with ExecuteQuery("users.db", "SELECT * FROM nonexistent_table") as result:
        print(result)
except Exception as e:
    print(f"Caught expected error: {e}")