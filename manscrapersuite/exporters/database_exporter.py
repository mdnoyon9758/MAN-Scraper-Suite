#!/usr/bin/env python3
"""
Database Exporter
Handles exporting data to MySQL, PostgreSQL, and MongoDB
"""

from typing import Dict, List, Any, Optional
import pymongo
import mysql.connector
import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd

class DatabaseExporter:
    """Export data to various databases"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_config = config["database"]
        self.connection = None
        self.engine = None
        
        if self.db_config["type"]:
            self._connect()
    
    def _connect(self):
        """Connect to the configured database"""
        db_type = self.db_config["type"].lower()
        
        try:
            if db_type == "mysql":
                self._connect_mysql()
            elif db_type == "postgresql":
                self._connect_postgresql()
            elif db_type == "mongodb":
                self._connect_mongodb()
            else:
                print(f"Unsupported database type: {db_type}")
                
        except Exception as e:
            print(f"Failed to connect to {db_type}: {e}")
    
    def _connect_mysql(self):
        """Connect to MySQL database"""
        connection_string = (
            f"mysql+mysqlconnector://{self.db_config['username']}:"
            f"{self.db_config['password']}@{self.db_config['host']}:"
            f"{self.db_config.get('port', 3306)}/{self.db_config['database']}"
        )
        
        self.engine = create_engine(connection_string)
        self.connection = mysql.connector.connect(
            host=self.db_config["host"],
            port=self.db_config.get("port", 3306),
            user=self.db_config["username"],
            password=self.db_config["password"],
            database=self.db_config["database"]
        )
        print("Connected to MySQL database")
    
    def _connect_postgresql(self):
        """Connect to PostgreSQL database"""
        connection_string = (
            f"postgresql://{self.db_config['username']}:"
            f"{self.db_config['password']}@{self.db_config['host']}:"
            f"{self.db_config.get('port', 5432)}/{self.db_config['database']}"
        )
        
        self.engine = create_engine(connection_string)
        self.connection = psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config.get("port", 5432),
            user=self.db_config["username"],
            password=self.db_config["password"],
            database=self.db_config["database"]
        )
        print("Connected to PostgreSQL database")
    
    def _connect_mongodb(self):
        """Connect to MongoDB database"""
        if self.db_config["username"] and self.db_config["password"]:
            connection_string = (
                f"mongodb://{self.db_config['username']}:"
                f"{self.db_config['password']}@{self.db_config['host']}:"
                f"{self.db_config.get('port', 27017)}/{self.db_config['database']}"
            )
        else:
            connection_string = (
                f"mongodb://{self.db_config['host']}:"
                f"{self.db_config.get('port', 27017)}/{self.db_config['database']}"
            )
        
        self.connection = pymongo.MongoClient(connection_string)
        self.db = self.connection[self.db_config["database"]]
        print("Connected to MongoDB database")
    
    def export_to_sql_table(self, data: List[Dict[str, Any]], table_name: str, 
                           if_exists: str = "append") -> bool:
        """Export data to SQL table (MySQL/PostgreSQL)"""
        if not self.engine:
            print("No SQL database connection available")
            return False
        
        try:
            df = pd.DataFrame(data)
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            print(f"Data exported to table '{table_name}' successfully")
            return True
            
        except Exception as e:
            print(f"Failed to export data to SQL table: {e}")
            return False
    
    def export_to_mongodb_collection(self, data: List[Dict[str, Any]], 
                                   collection_name: str) -> bool:
        """Export data to MongoDB collection"""
        if not hasattr(self, 'db'):
            print("No MongoDB connection available")
            return False
        
        try:
            collection = self.db[collection_name]
            
            if data:
                if len(data) == 1:
                    collection.insert_one(data[0])
                else:
                    collection.insert_many(data)
                
                print(f"Data exported to collection '{collection_name}' successfully")
                return True
            else:
                print("No data to export")
                return False
                
        except Exception as e:
            print(f"Failed to export data to MongoDB: {e}")
            return False
    
    def export_data(self, data: List[Dict[str, Any]], table_or_collection: str) -> bool:
        """Export data to the configured database"""
        if not data:
            print("No data to export")
            return False
        
        db_type = self.db_config["type"].lower()
        
        if db_type in ["mysql", "postgresql"]:
            return self.export_to_sql_table(data, table_or_collection)
        elif db_type == "mongodb":
            return self.export_to_mongodb_collection(data, table_or_collection)
        else:
            print(f"Export not implemented for database type: {db_type}")
            return False
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """Create a table in SQL database"""
        if not self.connection or self.db_config["type"].lower() == "mongodb":
            print("Table creation only supported for SQL databases")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            column_definitions = []
            for col_name, col_type in columns.items():
                column_definitions.append(f"{col_name} {col_type}")
            
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(column_definitions)},
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_sql)
            self.connection.commit()
            cursor.close()
            
            print(f"Table '{table_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"Failed to create table: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                print("Database connection closed")
        except Exception as e:
            print(f"Error closing database connection: {e}")
    
    def __del__(self):
        """Cleanup database connection on object destruction"""
        self.close_connection()
