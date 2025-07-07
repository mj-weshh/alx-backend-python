#!/usr/bin/env python3
"""
ExecuteQuery - A reusable context manager for SQLite query execution.

This module provides a context manager for executing parameterized SQL queries
with automatic resource management.
"""

import sqlite3
from typing import Any, List, Optional, Tuple

class ExecuteQuery:
    """
    A context manager for executing parameterized SQLite queries.
    
    This class handles the full lifecycle of database connections and cursors,
    ensuring proper resource cleanup even if an error occurs during execution.
    
    Args:
        query (str): The SQL query to execute (parameterized).
        params (tuple): The parameters to use with the query.
    """
    
    def __init__(self, query: str, params: Tuple[Any, ...] = ()):
        """Initialize the ExecuteQuery with a query and parameters."""
        self.query = query
        self.params = params
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def __enter__(self) -> List[Tuple[Any, ...]]:
        """
        Execute the query and return the results.
        
        Returns:
            List[Tuple[Any, ...]]: The query results as a list of tuples.
            
        Raises:
            sqlite3.Error: If there is an error executing the query.
        """
        try:
            self.conn = sqlite3.connect('users.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.query, self.params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self._close_resources()
            raise e
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Ensure all resources are properly closed.
        
        This method is called when exiting the 'with' block and ensures that
        both the cursor and connection are properly closed, even if an
        exception was raised.
        """
        self._close_resources()
    
    def _close_resources(self) -> None:
        """Helper method to close cursor and connection if they exist."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None

# Example usage
if __name__ == "__main__":
    try:
        with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
            for user in results:
                print(user)
    except sqlite3.Error as e:
        # In a real application, you might want to log this error
        pass
