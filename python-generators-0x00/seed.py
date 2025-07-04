#!/usr/bin/env python3
"""
Database seeding utility for ALX_prodev database.
Handles database creation, table setup, and data import from CSV.
"""

import os
import uuid
import logging
import csv
import mysql.connector
from mysql.connector import Error
from typing import Optional, Generator, Tuple, Any
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_db() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Connect to the MySQL server.
    
    Returns:
        MySQLConnection: A connection to the MySQL server if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""  # In production, use environment variables or config file
        )
        if connection.is_connected():
            logger.info("Successfully connected to MySQL server")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
    return None

def create_database(connection: mysql.connector.connection.MySQLConnection) -> None:
    """
    Create the ALX_prodev database if it doesn't exist.
    
    Args:
        connection: A connection to the MySQL server.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        connection.commit()
        logger.info("Database ALX_prodev created or already exists")
    except Error as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()

def connect_to_prodev() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Connect to the ALX_prodev database.
    
    Returns:
        MySQLConnection: A connection to the ALX_prodev database if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # In production, use environment variables or config file
            database="ALX_prodev"
        )
        if connection.is_connected():
            logger.info("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        logger.error(f"Error connecting to ALX_prodev database: {e}")
    return None

def create_table(connection: mysql.connector.connection.MySQLConnection) -> None:
    """
    Create the user_data table if it doesn't exist.
    
    Args:
        connection: A connection to the ALX_prodev database.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(10, 2) NOT NULL,
        UNIQUE KEY unique_email (email)
    )
    """
    
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        logger.info("Table user_data created or already exists")
        print("Table user_data created successfully")
    except Error as e:
        logger.error(f"Error creating table: {e}")
        raise
    finally:
        if cursor:
            cursor.close()

def read_csv_data(csv_filename: str) -> Generator[Tuple[str, str, str, Decimal], None, None]:
    """
    Read user data from a CSV file and yield rows one by one.
    
    Args:
        csv_filename: Path to the CSV file containing user data.
        
    Yields:
        Tuple containing (user_id, name, email, age) for each row.
    """
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    user_id = str(uuid.uuid4())  # Generate new UUID for each user
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    age = Decimal(row.get('age', 0))
                    
                    if not all([name, email]):
                        logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                        
                    yield (user_id, name, email, age)
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing row {row}: {e}")
                    continue
                    
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_filename}")
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise

def insert_data(connection: mysql.connector.connection.MySQLConnection, csv_filename: str) -> None:
    """
    Insert data from CSV file into the user_data table.
    
    Args:
        connection: A connection to the ALX_prodev database.
        csv_filename: Path to the CSV file containing user data.
    """
    if not os.path.exists(csv_filename):
        logger.error(f"CSV file not found: {csv_filename}")
        raise FileNotFoundError(f"CSV file not found: {csv_filename}")
    
    insert_query = """
    INSERT IGNORE INTO user_data (user_id, name, email, age)
    VALUES (%s, %s, %s, %s)
    """
    
    cursor = None
    try:
        cursor = connection.cursor()
        batch_size = 100
        batch = []
        
        for row in read_csv_data(csv_filename):
            batch.append(row)
            if len(batch) >= batch_size:
                cursor.executemany(insert_query, batch)
                connection.commit()
                logger.info(f"Inserted {len(batch)} records")
                batch = []
        
        # Insert any remaining records
        if batch:
            cursor.executemany(insert_query, batch)
            connection.commit()
            logger.info(f"Inserted final batch of {len(batch)} records")
            
        logger.info(f"Completed data import from {csv_filename}")
        
    except Error as e:
        connection.rollback()
        logger.error(f"Error inserting data: {e}")
        raise
    finally:
        if cursor:
            cursor.close()

def main():
    """Main function to execute the database setup and data import."""
    # First, connect to MySQL server and create the database
    connection = connect_db()
    if not connection:
        logger.error("Failed to connect to MySQL server")
        return
    
    try:
        create_database(connection)
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        return
    finally:
        connection.close()
    
    # Now connect to the ALX_prodev database
    prodev_connection = connect_to_prodev()
    if not prodev_connection:
        logger.error("Failed to connect to ALX_prodev database")
        return
    
    try:
        # Create the table
        create_table(prodev_connection)
        
        # Insert data from CSV
        csv_file = "user_data.csv"  # Assuming the file is in the same directory
        if os.path.exists(csv_file):
            insert_data(prodev_connection, csv_file)
            logger.info("Data import completed successfully")
        else:
            logger.warning(f"CSV file '{csv_file}' not found. Database and table created, but no data was imported.")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if prodev_connection and prodev_connection.is_connected():
            prodev_connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()
