#!/usr/bin/env python3
"""
demo.py
Runs the log_queries decorator from log_queries.py
"""
from log_queries import fetch_all_users


print("=== All Users ===")
users = fetch_all_users("SELECT * FROM users")
for u in users:
    print(u)

print("\n=== Users > 40 ===")
older = fetch_all_users(query="SELECT name, age FROM users WHERE age > 40")
for u in older:
    print(u)

import sys
sys.modules[__name__] = log_queries