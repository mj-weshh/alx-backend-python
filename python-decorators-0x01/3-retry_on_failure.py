import time 
import sqlite3 
import functools

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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that retries the decorated function on failure.
    
    Args:
        retries (int): Maximum number of retry attempts (default: 3).
        delay (int): Delay in seconds between retries (default: 2).
        
    Returns:
        A decorator that adds retry behavior to the wrapped function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retries:
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
            
            # If we've exhausted all retries, raise the last exception
            print(f"All {retries} attempts failed. Raising exception...")
            raise last_exception
        
        return wrapper
    
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempt to fetch users with automatic retry on failure
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)
