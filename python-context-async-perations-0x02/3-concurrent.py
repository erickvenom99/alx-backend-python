#!/usr/bin/env python3
"""
3-concurrent.py
Run two async SQLite queries concurrently using aiosqlite + asyncio.gather
"""

import aiosqlite
import asyncio
from typing import List, Tuple


async def async_fetch_users() -> List[Tuple]:
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT id, name, age, email FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users() -> List[Tuple]:
    async with aiosqlite.connect("users.db") as db:
        async with db.execute(
            "SELECT id, name, age, email FROM users WHERE age > ?", (40,)
        ) as cursor:
            return await cursor.fetchall()

async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return all_users, older_users

if __name__ == "__main__":
    all_users, older_users = asyncio.run(fetch_concurrently())

    print("=== ALL USERS ===")
    for user in all_users:
        print(f"  {user}")

    print("\n=== USERS OLDER THAN 40 ===")
    for user in older_users:
        print(f"  {user}")