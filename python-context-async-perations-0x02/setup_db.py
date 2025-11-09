#!/usr/bin/env python3
"""
setup_db.py
Creates users.db with sample data for testing
"""

import sqlite3

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email VARCHAR(250) NOT NULL
            )
    """)

    # Insert sample data
    users = [
        ('Alice', 30, 'alice@email.com'),
        ('Bob', 45, 'bob@email.com'),
        ('Charlie', 17, 'charlie@email.com'),
        ('Diana', 52, 'Diana@email.com'),
        ('Eve', 38, 'eve@email.com')
    ]
    cursor.executemany("INSERT OR IGNORE INTO users (name, age, email) VALUES (?, ?, ?)", users)

    conn.commit()
    conn.close()
    print("users.db created with 5 test users.")

if __name__ == "__main__":
    create_db()