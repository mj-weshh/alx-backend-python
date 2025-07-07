#!/usr/bin/env python3
"""
Database connection context manager for SQLite operations.

This module provides a DatabaseConnection class that can be used as a context manager
to handle SQLite database connections with automatic resource cleanup.
"""

import sqlite3

class DatabaseConnection:
    """
    A context manager for handling SQLite database connections.
    
    This class ensures that database connections are properly closed
    when the context is exited, even if an exception occurs.
    
    Args:
        db_name (str): The name of the SQLite database file.
    """
    def __init__(self, db_name):
        """Initialize the DatabaseConnection with the database name."""
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """
        Enter the runtime context and return the database connection.
        
        Returns:
            sqlite3.Connection: A connection to the SQLite database.
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context and close the database connection.
        
        This method is called when exiting the 'with' block and ensures
        the connection is properly closed, even if an exception occurred.
        
        Args:
            exc_type: The exception type if an exception was raised in the 'with' block.
            exc_val: The exception value if an exception was raised.
            exc_tb: The traceback if an exception was raised.
        """
        if self.conn:
            self.conn.close()

# Example usage of the DatabaseConnection context manager
if __name__ == "__main__":
    try:
        with DatabaseConnection('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            for row in results:
                print(row)
    except sqlite3.Error as e:
        # Silently handle any database errors (as per requirements)
        pass
