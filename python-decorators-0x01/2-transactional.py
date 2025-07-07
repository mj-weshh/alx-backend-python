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

def transactional(func):
    """
    Decorator that wraps a function in a database transaction.
    
    The decorated function must take a database connection as its first argument.
    The transaction will be committed if the function completes successfully,
    or rolled back if an exception is raised.
    
    Args:
        func: The function to be wrapped in a transaction.
        
    Returns:
        The decorated function with transaction management.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # SQLite starts transactions implicitly, but we'll be explicit
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

# Update user's email with automatic transaction handling 
if __name__ == "__main__":
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
