import snowflake.connector
from snowflake.connector import DictCursor
from app.core.config import settings
from app.utils.logger import logger
from typing import List, Dict, Any, Optional
import json

class SnowflakeService:
    def __init__(self):
        """Initialize Snowflake connection with secure settings"""
        try:
            self.conn = snowflake.connector.connect(
                user=settings.SNOWFLAKE_USER,
                password=settings.SNOWFLAKE_PASSWORD,
                account=settings.SNOWFLAKE_ACCOUNT,
                warehouse=settings.SNOWFLAKE_WAREHOUSE,
                database=settings.SNOWFLAKE_DATABASE,
                schema=settings.SNOWFLAKE_SCHEMA,
                autocommit=False,  # Explicit transaction control
                client_session_keep_alive=True,
                # Remove private_key unless you've implemented key-pair auth
            )
            logger.info("Successfully connected to Snowflake")
        except Exception as e:
            logger.error(f"Snowflake connection failed: {str(e)}")
            raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a parameterized query safely"""
        cursor = None
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute(query, params) if params else cursor.execute(query)
            return cursor.fetchall()
        except snowflake.connector.Error as e:
            logger.error(f"Snowflake query failed: {str(e)}\nQuery: {query}")
            self.conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def log_wellness_session(self, session_data: dict):
        """Securely log wellness session using parameterized queries"""
        query = """
        INSERT INTO wellness_sessions (
            session_id,
            user_id,
            timestamp,
            wellness_score,
            mood_level
        ) VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            session_data['session_id'],
            session_data['user_id'],
            session_data['timestamp'],
            session_data.get('wellness_score'),  # Handles None safely
            session_data['mood_level']
        )
        self.execute_query(query, params)

    def get_wellness_trends(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get wellness trends with parameterized query"""
        query = """
        SELECT DATE_TRUNC('DAY', timestamp) as date,
               AVG(wellness_score) as avg_score
        FROM wellness_sessions
        WHERE user_id = %s
          AND timestamp >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
        GROUP BY 1
        ORDER BY 1
        """
        return self.execute_query(query, (user_id, days))

    def __enter__(self):
        """Support for context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper connection cleanup"""
        self.close()

    def close(self):
        """Explicit connection closure"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logger.info("Snowflake connection closed")

    def __del__(self):
        """Destructor for fallback cleanup"""
        self.close()