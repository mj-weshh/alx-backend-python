# Database Seeding Utility

This project implements a Python-based database seeding utility that sets up a MySQL database, creates necessary tables, and populates them with data from a CSV file.

## Features

- **Database Management**: Creates and manages MySQL database connections
- **Table Creation**: Sets up the required database schema
- **Data Import**: Efficiently imports data from CSV files
- **Error Handling**: Comprehensive error handling and logging
- **Idempotent Operations**: Safe to run multiple times without duplicating data

## Prerequisites

- Python 3.6 or higher
- MySQL Server 5.7 or higher
- `mysql-connector-python` package

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mj-weshh/alx-backend-python.git
   cd alx-backend-python/python-generators-0x00
   ```

2. Install the required Python package:
   ```bash
   pip install mysql-connector-python
   ```

## Configuration

Before running the script, ensure your MySQL server is running and accessible. The script uses the following default connection parameters:

- Host: `localhost`
- User: `root`
- Password: (empty)
- Database: `ALX_prodev`

You can modify these parameters directly in the `seed.py` file if needed.

## Usage

1. **Prepare your data**:
   Create a `user_data.csv` file in the same directory as `seed.py` with the following columns:
   - `name` (string): User's full name
   - `email` (string): User's email address
   - `age` (decimal): User's age

   Example `user_data.csv`:
   ```csv
   name,email,age
   John Doe,john@example.com,28
   Jane Smith,jane@example.com,34
   ```

2. **Run the script**:
   ```bash
   python seed.py
   ```

3. **Verify the data**:
   The script will create the database, table, and import the data. You can verify the data by querying the database:
   ```sql
   USE ALX_prodev;
   SELECT * FROM user_data LIMIT 5;
   ```

## Functions

### `connect_db() -> MySQLConnection | None`
Establishes a connection to the MySQL server.

### `create_database(connection: MySQLConnection) -> None`
Creates the ALX_prodev database if it doesn't exist.

### `connect_to_prodev() -> MySQLConnection | None`
Connects to the ALX_prodev database.

### `create_table(connection: MySQLConnection) -> None`
Creates the user_data table with the following schema:
- `user_id` (UUID, PRIMARY KEY)
- `name` (VARCHAR, NOT NULL)
- `email` (VARCHAR, NOT NULL, UNIQUE)
- `age` (DECIMAL, NOT NULL)

### `insert_data(connection: MySQLConnection, csv_filename: str) -> None`
Reads data from a CSV file and inserts it into the user_data table.

## Error Handling

The script includes comprehensive error handling and logging:
- Failed database connections
- Missing or invalid CSV files
- Data validation errors
- Duplicate entries (skipped automatically)

## Logging

Logs are printed to the console and include timestamps and log levels. The script logs:
- Successful operations
- Warnings for skipped records
- Errors for critical failures

## Best Practices

- Uses parameterized queries to prevent SQL injection
- Implements proper resource cleanup using context managers
- Includes type hints for better code maintainability
- Follows PEP 8 style guidelines
- Implements batch processing for efficient data insertion

## Acknowledgments

- ALX School for the project requirements
- Python and MySQL communities for their excellent documentation
