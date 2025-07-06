import logging
import snowflake.connector
from typing import List, Dict, Any, Optional, Union, Tuple

from ..core.config import settings

logger = logging.getLogger("ruhani")

class SnowflakeClient:
    def __init__(self):
        try:
            self.conn = snowflake.connector.connect(
                user=settings.SNOWFLAKE_USER,
                password=settings.SNOWFLAKE_PASSWORD,
                account=settings.SNOWFLAKE_ACCOUNT,
                warehouse=settings.SNOWFLAKE_WAREHOUSE,
                database=settings.SNOWFLAKE_DATABASE,
                schema=settings.SNOWFLAKE_SCHEMA,
                role=settings.SNOWFLAKE_ROLE
            )
            logger.info("Successfully connected to Snowflake")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[snowflake.connector.cursor.SnowflakeCursor]:
        """Execute a single SQL query and return the cursor"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor
        except Exception as e:
            logger.error(f"Error executing query: {e}\nQuery: {query}\nParams: {params}")
            return None
    
    def execute_many(self, queries: List[str]) -> List[Tuple[bool, Optional[str]]]:
        """Execute multiple SQL queries and return success status for each"""
        results = []
        for query in queries:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
                results.append((True, None))
            except Exception as e:
                error_msg = f"Error executing query: {e}\nQuery: {query}"
                logger.error(error_msg)
                results.append((False, error_msg))
        return results
    
    def close(self) -> None:
        """Close the Snowflake connection"""
        try:
            if self.conn:
                self.conn.close()
                logger.info("Snowflake connection closed")
        except Exception as e:
            logger.error(f"Error closing Snowflake connection: {e}")
            
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()
