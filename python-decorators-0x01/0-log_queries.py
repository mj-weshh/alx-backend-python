import sqlite3
import functools

def log_queries(func):
    """
    Decorator that logs the SQL query before executing the decorated function.
    
    Args:
        func: The function to be decorated, which should accept a 'query' parameter.
        
    Returns:
        The decorated function that will log the query before execution.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from either args or kwargs
        query = kwargs.get('query', args[0] if args else None)
        
        # Log the query
        print(f"Executing query: {query}")
        
        # Call the original function with all arguments
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the database based on the provided query.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        list: A list of tuples representing the query results.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    # This will print the query before executing it
    users = fetch_all_users(query="SELECT * FROM users")
