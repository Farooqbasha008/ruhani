from dotenv import load_dotenv
from pathlib import Path
import os
import snowflake.connector

# Load the .env file from backend/.env
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

# Print loaded user for confirmation
user = os.getenv("SNOWFLAKE_USER")
print(f"✅ ENV Loaded. User: {user}")

try:
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=user,
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        authenticator=os.getenv("SNOWFLAKE_AUTHENTICATOR")
    )

    print("⏳ Connected. Running test query...")

    cur = conn.cursor()
    cur.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
    result = cur.fetchone()

    if result is not None and all(x is not None for x in result):
        print("✅ Connection Successful!")
        print(f"👤 User: {result[0]}")
        print(f"🛡️ Role: {result[1]}")
        print(f"🏭 Warehouse: {result[2]}")
        print(f"📚 Database: {result[3]}")
    else:
        print("⚠️ Query ran, but no results returned or some values are None.")
        print(f"Result: {result}")

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed:", e)
    print("Please check your Snowflake credentials, network, and that your account/warehouse/database/schema are correct.")
