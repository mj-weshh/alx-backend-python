#!/usr/bin/env python3
"""
Concurrent Asynchronous SQLite Queries with aiosqlite.

This module demonstrates concurrent database operations using asyncio and aiosqlite.
It runs multiple queries in parallel and prints the results.
"""

import asyncio
import aiosqlite
from typing import List, Tuple, Any

async def async_fetch_users() -> List[Tuple[Any, ...]]:
    """
    Fetch all users from the database asynchronously.
    
    Returns:
        List[Tuple[Any, ...]]: A list of tuples containing user data.
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("SELECT * FROM users") as cursor:
                return await cursor.fetchall()
    except aiosqlite.Error as e:
        print(f"Error fetching all users: {e}")
        return []

async def async_fetch_older_users() -> List[Tuple[Any, ...]]:
    """
    Fetch users older than 40 from the database asynchronously.
    
    Returns:
        List[Tuple[Any, ...]]: A list of tuples containing user data for users older than 40.
    """
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
                return await cursor.fetchall()
    except aiosqlite.Error as e:
        print(f"Error fetching older users: {e}")
        return []

async def fetch_concurrently() -> Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]:
    """
    Execute multiple database queries concurrently using asyncio.gather.
    
    Returns:
        Tuple containing:
        - List of all users
        - List of users older than 40
    """
    users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return users, older_users

def main() -> None:
    """Entry point for the script."""
    try:
        users, older_users = asyncio.run(fetch_concurrently())
        
        print("\nAll Users:")
        for user in users:
            print(user)
            
        print("\nUsers Older Than 40:")
        for user in older_users:
            print(user)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
