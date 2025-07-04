#!/usr/bin/env python3
"""
Stream users from the ALX_prodev database using a generator.
This module provides a memory-efficient way to stream user data row by row.
"""

import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, Generator, Optional


def connect_to_prodev() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Connect to the ALX_prodev database.
    
    Returns:
        MySQLConnection: A connection to the ALX_prodev database if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # In production, use environment variables or config file
            database="ALX_prodev"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
    return None


def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Stream users from the user_data table one row at a time.
    
    Yields:
        Dict[str, Any]: A dictionary containing user data with keys:
            - user_id (str): The user's unique identifier
            - name (str): The user's full name
            - email (str): The user's email address
            - age (int/float): The user's age
            
    Example:
        >>> for user in stream_users():
        ...     print(user)
        {'user_id': '...', 'name': '...', 'email': '...', 'age': ...}
    """
    connection = None
    cursor = None
    
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            raise ConnectionError("Failed to connect to the database")
            
        # Use a server-side cursor to fetch rows one by one
        cursor = connection.cursor(dictionary=True, buffered=False)
        
        # Execute the query to fetch all users
        query = """
        SELECT user_id, name, email, age 
        FROM user_data
        """
        cursor.execute(query)
        
        # Stream rows one by one
        for row in cursor:
            yield {
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': float(row['age'])  # Convert Decimal to float for consistency
            }
            
    except Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    # Example usage when run directly
    from itertools import islice
    
    print("First 6 users from the database:")
    for user in islice(stream_users(), 6):
        print(user)
