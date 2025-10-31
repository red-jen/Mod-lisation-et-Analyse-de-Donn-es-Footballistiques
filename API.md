# API Documentation

## DatabaseManager

### Methods

#### `__init__(host, port, database, user, password)`
Initialize database manager with connection parameters.

**Parameters:**
- `host` (str): PostgreSQL host address (default: 'localhost')
- `port` (int): PostgreSQL port (default: 5432)
- `database` (str): Database name (default: 'foot_ball')
- `user` (str): Database user (default: 'postgres')
- `password` (str): Database password

#### `connect()`
Establish connection to PostgreSQL.

**Returns:**
- SQLAlchemy engine object or None if failed

#### `insert_data(df, table_name)`
Insert DataFrame into specified table.

**Parameters:**
- `df` (pd.DataFrame): Data to insert
- `table_name` (str): Target table name

**Returns:**
- bool: True if successful, False otherwise

#### `get_count(table_name)`
Get row count from table.

**Parameters:**
- `table_name` (str): Table name

**Returns:**
- int: Number of rows in table

## Data Cleaning Functions

### `clean_players(df)`
Clean players DataFrame.

**Operations:**
- Remove duplicates
- Remove empty rows
- Standardize column names
- Remove rows without player name

### `clean_matches(df)`
Clean matches DataFrame.

**Operations:**
- Remove duplicates
- Remove empty rows
- Standardize column names
- Convert date to datetime
- Convert numeric columns

### `standardize_columns(df)`
Standardize all column names to lowercase with underscores.

## Usage Examples

```python
from db_manager import DatabaseManager
from data_cleaner import clean_players, clean_matches

# Connect to database
db = DatabaseManager()
db.connect()

# Insert data
db.insert_data(players_df, 'joueur')

# Get table count
count = db.get_count('joueur')
print(f"Players: {count}")
```
