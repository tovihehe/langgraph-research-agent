from connectors.db_connectors.postgre_connector import PostgreConnector
from connectors.db_connectors.redis_connector import RedisConnector

class DatabaseInterface():
    """Class to handle database connection."""
    def __init__(self, database_type):
        self.database_type = database_type

    def get_db_connector(self):
        """Returns the database connector based on the database type."""
        if self.database_type == 'postgresql':
            return PostgreConnector()

        elif self.database_type == 'redis':
            return RedisConnector()