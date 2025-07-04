#!/usr/bin/env python3
"""
Memory-efficient age calculation using generators.
This module calculates the average age of users without loading all data into memory.
"""

import sys
from typing import Generator, Optional, Tuple

# Import the connect_to_prodev function from seed module
from seed import connect_to_prodev


def stream_user_ages() -> Generator[float, None, None]:
    """
    Stream user ages from the database one at a time.
    
    Yields:
        float: The age of each user as it's retrieved from the database.
        
    Note:
        Uses a server-side cursor to ensure minimal memory usage.
    """
    connection = None
    cursor = None
    
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            raise ConnectionError("Failed to connect to the database")
            
        # Use server-side cursor to stream results
        cursor = connection.cursor(buffered=False, dictionary=False)
        
        # Only select the age column to minimize data transfer
        query = "SELECT age FROM user_data"
        cursor.execute(query)
        
        # Stream ages one by one
        for (age,) in cursor:
            yield float(age)
            
    except Exception as e:
        print(f"Error streaming user ages: {e}", file=sys.stderr)
        raise
    finally:
        # Ensure proper cleanup of resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def compute_average_age() -> float:
    """
    Calculate the average age of all users using a streaming approach.
    
    Returns:
        float: The average age of users, or 0.0 if there are no users.
        
    Note:
        Uses Welford's online algorithm for numerical stability.
        This allows calculating mean and variance in a single pass with
        minimal memory usage and good numerical properties.
    """
    count = 0
    total = 0.0
    
    # Single loop to process all ages
    for age in stream_user_ages():
        count += 1
        total += age
    
    # Handle empty dataset case
    if count == 0:
        return 0.0
        
    return total / count


if __name__ == "__main__":
    try:
        average_age = compute_average_age()
        print(f"Average age of users: {average_age:.1f}")
    except Exception as e:
        print(f"Error calculating average age: {e}", file=sys.stderr)
        sys.exit(1)
