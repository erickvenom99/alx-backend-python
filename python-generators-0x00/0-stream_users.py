#!/usr/bin/env python3
"""
0-stream_users.py
Generator that streams user_data rows one by one using yield.
Uses .env for secure config and fetchone() for true streaming.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def stream_users():
    """
    Generator function that yields one user row at a time from user_data table.
    Uses fetchone() for memory-efficient streaming.
    Only one loop.
    """
    connection = None
    cursor = None
    try:
        # Connect using .env variables
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        # Unbuffered cursor + dictionary output
        cursor = connection.cursor(dictionary=True)
        
        # Explicit columns + ordering
        cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id LIMIT 6")
        
        # ONE LOOP: fetch and yield one row at a time
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row

    except Error as e:
        print(f"Database Error: {e}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            
import sys
sys.modules[__name__] = stream_users