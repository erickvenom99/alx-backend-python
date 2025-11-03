#!/usr/bin/env python3
"""
A generator to compute a memory-efficient aggregate function, i.e., average age for a large dataset.
"""

# seed.py contains the connect_to_prodev() function
import sys
from decimal import Decimal
from mysql.connector import Error
import seed  # assuming seed.py is in the same directory

def stream_user_ages():
    """
    Yields user ages one by one.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT age FROM user_data")
        for row in cursor:
            yield row['age']
    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def calculate_average_age():
    """
    Calculate the average age without loading the entire dataset into memory.
    """
    total_age = Decimal('0.0')
    age_count = 0
    for age in stream_user_ages():
        total_age += Decimal(age)
        age_count += 1
    if age_count > 0:
        total_average = total_age / age_count
        print(f"Average age of users: {total_average}")
    else:
        print("No age data found.")

if __name__ == "__main__":
    calculate_average_age()