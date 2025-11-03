#!/usr/bin/python3
"""
 a generator to fetch and process data in batches from the users database
"""
import os
import mysql.connector
from mysql.connector import Error
from typing import Generator, List, Dict
from dotenv import load_dotenv

load_dotenv()

def stream_users_in_batches(batch_size: int) -> Generator[List[Dict], None, None]:
    """
    Return a list of Dictionary from user_data in batches
    """
    conn = None
    cur = None
    try:
        conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        buffered=False  # Unbuffered cursor for streaming
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id")
        while True:
            batch = cur.fetchmany(batch_size)
            if not batch:
                break
            yield batch
    except Error as e:
        print(f"Database error in stream_users_in_batches:{e}", file=os.stderr)
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

#filters batches and yield accepted batches
def batch_processing(batch_size: int) -> Generator[Dict, None, None]:
    """
    Consume the batch generator, keep only users with age > 25 and
    yield them one-by-one for the caller
    """
    process_batch = stream_users_in_batches(batch_size)
    # iterate over batches
    for batch in process_batch:
        #iterate over rows
        for user in batch:
            if user.get('age', 0) > 25:
                print(user)
