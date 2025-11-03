"""
seed.py

This script initializes the MySQL database environment for the ALX_prodev project.
It performs the following tasks:
- Connects to the MySQL server using credentials from environment variables.
- Creates the ALX_prodev database if it does not already exist.
- Connects to the ALX_prodev database.
- Creates the user_data table with required fields and constraints.
- Seeds the user_data table with records from a CSV file, avoiding duplicate emails.

Environment variables required:
- DB_HOST: Hostname of the MySQL server.
- DB_USER: Username for MySQL authentication.
- DB_PASSWORD: Password for MySQL authentication.
- DB_NAME: Target database name (should be 'ALX_prodev').

Usage:
    Run this script to set up the database and populate initial user data.
"""

import os
import csv
import uuid
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file
load_dotenv()

def connect_db():
    """Connect to MySQL server (without selecting a database)."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD', '')
        )
        if connection.is_connected():
            print("Connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Create the ALX_prodev database if it doesn't exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created successfully")
        cursor.close()
        return True
    except Error as e:
        print(f"Database creation failed: {e}")
        return False

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Create user_data table with required fields if it doesn't exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS user_data")
        create_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        cursor.execute(create_query)
        print("Table user_data created successfully")
        cursor.close()
        return True
    except Error as e:
        print(f"Failed to create user_data table: {e}")
        return False

def insert_data(connection, data):
    """Insert data from CSV file into user_data table."""
    try:
        cursor = connection.cursor()
        with open(data, 'r') as file:
            csv_reader = csv.reader(file, quotechar='"')
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                if len(row) == 3:
                    name, email, age = [x.strip() for x in row]
                    user_id = str(uuid.uuid4())
                    age = int(age)
                    # Check for duplicate email
                    cursor.execute("SELECT user_id FROM user_data WHERE email = %s", (email,))
                    if cursor.fetchone() is None:
                        insert_query = """
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (user_id, name, email, age))

        connection.commit()
        print("Data inserted successfully")
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    except FileNotFoundError:
        print(f"Error: File {data} not found")