from enum import Enum
from functools import lru_cache


class DatabaseType(Enum):
    """An enum containing the different types of databases."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    REDSHIFT = "redshift"
    MYSQL = "mysql"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"


class DBUtils:
    """A class containing utility functions for working with SQLite databases."""

    def __init__(self, conn, db_type: DatabaseType = DatabaseType.SQLITE):
        self.conn = conn
        if db_type != DatabaseType.SQLITE:
            raise NotImplementedError("Only SQLite databases are currently supported.")

    def get_table_names(self):
        """Return a list of table names."""
        table_names = []
        tables = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in tables.fetchall():
            table_names.append(table[0])
        return table_names

    def get_column_names(self, table_name):
        """Return a list of column names."""
        column_names = []
        columns = self.conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        for col in columns:
            column_names.append(col[1])
        return column_names

    @lru_cache()
    def get_database_info(self):
        """Return a list of dicts containing the table name and columns for each table in the database."""
        table_dicts = []
        for table_name in self.get_table_names():
            columns_names = self.get_column_names(table_name)
            table_dicts.append(
                {"table_name": table_name, "column_names": columns_names}
            )
        return table_dicts

    @lru_cache()
    def get_database_string(self):
        database_schema_dict = self.get_database_info()
        database_schema_string = "\n".join(
            [
                f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
                for table in database_schema_dict
            ]
        )
        return database_schema_string
