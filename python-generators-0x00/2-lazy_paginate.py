#!/usr/bin/env python3
"""
Lazy pagination for user data using generators.
This module implements memory-efficient pagination for large datasets.
"""

import sys
from typing import List, Dict, Any, Generator

# Import the connect_to_prodev function from seed module
from seed import connect_to_prodev


def paginate_users(page_size: int, offset: int) -> List[Dict[str, Any]]:
    """
    Fetch a page of users from the database.
    
    Args:
        page_size: Number of records to fetch per page.
        offset: Starting position of the page.
        
    Returns:
        List[Dict[str, Any]]: A list of user dictionaries.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            raise ConnectionError("Failed to connect to the database")
            
        cursor = connection.cursor(dictionary=True)
        
        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))
        
        # Convert Decimal to float for consistency
        rows = []
        for row in cursor:
            rows.append({
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': float(row['age'])
            })
        
        return rows
        
    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def lazy_pagination(page_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    A generator function that yields pages of user data lazily.
    
    Args:
        page_size: Number of records per page.
        
    Yields:
        List[Dict[str, Any]]: A page of user data as a list of dictionaries.
    """
    offset = 0
    while True:
        # Fetch the next page of users
        page = paginate_users(page_size, offset)
        
        # If no more users, stop the generator
        if not page:
            break
            
        # Yield the current page
        yield page
        
        # Move to the next page
        offset += page_size
        
        # If we got fewer users than the page size, we've reached the end
        if len(page) < page_size:
            break


if __name__ == "__main__":
    # Example usage when run directly
    page_size = 10
    print(f"Lazy pagination with page size {page_size}:")
    
    # Process and print users page by page
    for page_num, page in enumerate(lazy_pagination(page_size), 1):
        print(f"\n--- Page {page_num} ---")
        for user in page:
            print(user)
