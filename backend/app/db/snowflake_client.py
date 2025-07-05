import os
from dotenv import load_dotenv
from pathlib import Path
import snowflake.connector

# Load env from ../../.env
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

class SnowflakeClient:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            authenticator=os.getenv("SNOWFLAKE_AUTHENTICATOR")
        )

    def execute(self, query: str, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params or {})
            return cur.fetchall()
