#!/usr/bin/env python3
"""
Batch processing of user data from MySQL using generators.
This module provides memory-efficient batch processing of user data with filtering.
"""

import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any, Generator, Optional


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


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Stream users from the database in batches of specified size.
    
    Args:
        batch_size: Number of records to fetch in each batch.
        
    Yields:
        List[Dict[str, Any]]: A list of user dictionaries, each containing:
            - user_id (str)
            - name (str)
            - email (str)
            - age (float)
    """
    connection = None
    cursor = None
    
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            raise ConnectionError("Failed to connect to the database")
            
        # Use server-side cursor with buffered=True for fetchmany()
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        # Execute the query to fetch all users
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        
        while True:
            # Fetch a batch of rows
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
                
            # Convert Decimal to float for consistency
            batch = [
                {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'age': float(row['age'])
                }
                for row in rows
            ]
            
            yield batch
            
    except Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def batch_processing(batch_size: int) -> Generator[Dict[str, Any], None, None]:
    """
    Process users in batches and filter those over 25 years old.
    
    Args:
        batch_size: Number of records to process in each batch.
        
    Yields:
        Dict[str, Any]: User dictionary for users over 25 years old.
    """
    for batch in stream_users_in_batches(batch_size):
        # Filter users over 25 and yield them one by one
        for user in batch:
            if user['age'] > 25:
                yield user


if __name__ == "__main__":
    # Example usage when run directly
    batch_size = 50
    print(f"Processing users in batches of {batch_size}. Showing users over 25:")
    
    # Process and print users over 25
    for user in batch_processing(batch_size):
        print(user)
