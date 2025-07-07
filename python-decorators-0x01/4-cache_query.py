import time 
import sqlite3 
import functools

# Global cache dictionary to store query results
query_cache = {}

def with_db_connection(func):
    """
    Decorator that handles database connection lifecycle for the decorated function.
    
    Opens a connection to the SQLite database, passes it as the first argument
    to the decorated function, and ensures the connection is properly closed
    after the function completes, even if an error occurs.
    
    Args:
        func: The function to be decorated. The first parameter should be 'conn'.
        
    Returns:
        The decorated function with automatic connection management.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a new database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the original function with the connection as first argument
            return func(conn, *args, **kwargs)
        finally:
            # Ensure the connection is always closed
            conn.close()
    
    return wrapper

def cache_query(func):
    """
    Decorator that caches the results of database queries.
    
    Uses the SQL query string as the cache key. If the same query is made again,
    returns the cached result instead of hitting the database.
    
    Args:
        func: The function to be decorated. Should accept a 'query' parameter.
        
    Returns:
        The decorated function with query caching.
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Use the query as the cache key
        cache_key = query.strip()  # Remove any extra whitespace for consistent keys
        
        # Check if the result is already in the cache
        if cache_key in query_cache:
            print(f"Cache hit for query: {cache_key}")
            return query_cache[cache_key]
        
        # If not in cache, execute the query and store the result
        print(f"Cache miss for query: {cache_key}")
        result = func(conn, query, *args, **kwargs)
        query_cache[cache_key] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetch users from the database with query result caching.
    
    Args:
        conn: Database connection (provided by with_db_connection)
        query: SQL query string to execute
        
    Returns:
        List of user records from the database
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    # First call will execute the query and cache the result
    print("First call (should miss cache):")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users) if users else 0} users")
    
    # Second call with the same query will use the cached result
    print("\nSecond call (should hit cache):")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Fetched {len(users_again) if users_again else 0} users from cache")
