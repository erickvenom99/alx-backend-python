#!/usr/bin/python3
"""
This module provides functions for paginating user data from the database.
"""
# seed.py contains the connect_to_prodev() function
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a single page of user data from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    
    # The f-string formats the SQL query with the correct LIMIT and OFFSET
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    A generator that lazily fetches pages of user data.
    
    It yields one page (a list of user dicts) at a time,
    only fetching the next page when requested by the caller.
    """
    # Start at the beginning of the database
    offset = 0
    
    # The "one loop" required by the prompt
    while True:
        # 1. Fetch the *current* page
        page_data = paginate_users(page_size, offset)
        
        # 2. Check if the page is empty (i.e., we've reached the end)
        #    If paginate_users returns an empty list, `not page_data` is True.
        if not page_data:
            break  # Exit the loop, stopping the generator
            
        # 3. "Pause" and send the current page back to the main script
        yield page_data
        
        # 4. If we are here, the main script is asking for the *next* page.
        #    Update the offset to get the next chunk of data.
        offset += page_size