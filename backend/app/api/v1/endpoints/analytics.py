from fastapi import APIRouter, Depends
from app.services.snowflake_service import SnowflakeService

router = APIRouter()

@router.get("/wellness-trends")
async def get_wellness_trends(
    days: int = 30,
    snowflake: SnowflakeService = Depends()
):
    query = f"""
    SELECT 
        DATE_TRUNC('DAY', timestamp) as day,
        AVG(wellness_score) as avg_score
    FROM wellness_sessions
    WHERE timestamp >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
    GROUP BY 1
    ORDER BY 1
    """
    return {"trends": snowflake.execute_query(query)}