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

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

# Fetch user by ID with automatic connection handling 
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
