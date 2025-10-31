"""
Database utility module for PostgreSQL operations
"""

from sqlalchemy import create_engine
import pandas as pd

class DatabaseManager:
    def __init__(self, host='localhost', port=5432, database='foot_ball', 
                 user='postgres', password='Ren-ji24'):
        self.connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_url)
            connection = self.engine.connect()
            print("✓ Connected to PostgreSQL")
            connection.close()
            return self.engine
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return None
    
    def insert_data(self, df, table_name):
        """Insert DataFrame into table"""
        try:
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            print(f"✓ Inserted {len(df)} rows into {table_name}")
            return True
        except Exception as e:
            print(f"✗ Error inserting into {table_name}: {e}")
            return False
    
    def get_count(self, table_name):
        """Get row count from table"""
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn)
                return result['count'][0]
        except Exception as e:
            print(f"✗ Error: {e}")
            return 0
