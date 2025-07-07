#!/usr/bin/env python3
"""
Concurrent Asynchronous SQLite Queries with aiosqlite.

This module demonstrates concurrent database operations using asyncio and aiosqlite.
It runs multiple queries in parallel and prints the results.
"""

import asyncio
import aiosqlite
from typing import List, Tuple, Any

async def async_fetch_users() -> None:
    """
    Fetch all users from the database asynchronously.
    
    Connects to the SQLite database, executes a SELECT query to fetch all users,
    and prints the results.
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                print("\nAll Users:")
                for row in rows:
                    print(row)
    except aiosqlite.Error as e:
        print(f"Error fetching all users: {e}")

async def async_fetch_older_users() -> None:
    """
    Fetch users older than 40 from the database asynchronously.
    
    Connects to the SQLite database, executes a parameterized SELECT query
    to fetch users older than 40, and prints the results.
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
                rows = await cursor.fetchall()
                print("\nUsers Older Than 40:")
                for row in rows:
                    print(row)
    except aiosqlite.Error as e:
        print(f"Error fetching older users: {e}")

async def fetch_concurrently() -> None:
    """
    Execute multiple database queries concurrently using asyncio.gather.
    
    This function demonstrates running multiple async database operations
    in parallel, which can significantly improve performance for I/O-bound tasks.
    """
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

def main() -> None:
    """Entry point for the script."""
    try:
        asyncio.run(fetch_concurrently())
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
