import uuid
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from .snowflake_client import SnowflakeClient
from ..core.config import settings
from datetime import datetime, timedelta
import random

logger = logging.getLogger("ruhani")

def init_snowflake_tables() -> bool:
    """Initialize Snowflake tables if they don't exist"""
    try:
        client = SnowflakeClient()
        
        # Create employees table
        employee_result = client.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            github_url VARCHAR(255),
            linkedin_url VARCHAR(255),
            team VARCHAR(255),
            stressors TEXT,
            onboarding_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """)
        
        if not employee_result:
            logger.error("Failed to create employees table")
            return False
        
        # Create sessions table
        session_result = client.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id VARCHAR(36) PRIMARY KEY,
            employee_id VARCHAR(36) NOT NULL,
            session_time TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            mood VARCHAR(50),
            summary TEXT,
            llm_response TEXT,
            risk_level VARCHAR(20),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        """)
        
        if not session_result:
            logger.error("Failed to create sessions table")
            return False
        
        # Create hr_insights table
        insight_result = client.execute("""
        CREATE TABLE IF NOT EXISTS hr_insights (
            id VARCHAR(36) PRIMARY KEY,
            employee_id VARCHAR(36) NOT NULL,
            weekly_summary TEXT,
            flags TEXT,
            trends TEXT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        """)
        
        if not insight_result:
            logger.error("Failed to create hr_insights table")
            return False
        
        logger.info("Snowflake tables initialized successfully")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Error initializing Snowflake tables: {e}")
        return False

def seed_sample_data() -> bool:
    """Seed the database with sample data for development purposes"""
    # Check if we're in development mode
    if not settings.is_production:
        try:
            client = SnowflakeClient()
            
            # Check if we already have data
            existing_employees = client.execute("SELECT COUNT(*) FROM employees")
            if not existing_employees:
                logger.error("Failed to check if employees exist")
                return False
                
            if existing_employees[0][0] > 0:
                logger.info("Sample data already exists, skipping seeding")
                client.close()
                return True
            
            # Sample teams
            teams = [
                "Engineering/Frontend", "Engineering/Backend", "Engineering/DevOps",
                "Product/Management", "Product/Research",
                "Design/UI", "Design/UX",
                "Marketing/Growth", "Marketing/Content",
                "Sales/Enterprise", "Sales/SMB"
            ]
            
            # Sample employee names
            employee_names = [
                "Alex Johnson", "Jamie Smith", "Taylor Wilson", "Morgan Lee",
                "Casey Brown", "Jordan Miller", "Riley Davis", "Quinn Martinez",
                "Avery Rodriguez", "Dakota Garcia", "Skyler Hernandez", "Reese Lopez"
            ]
            
            # Sample stressors
            stressors_list = [
                ["deadlines", "workload", "meetings"],
                ["communication", "work-life balance", "remote work"],
                ["team dynamics", "project complexity", "technical challenges"],
                ["career growth", "skill development", "feedback"],
                ["management style", "company culture", "recognition"]
            ]
            
            # Sample moods
            moods = ["happy", "neutral", "stressed", "anxious", "overwhelmed"]
            
            # Sample risk levels
            risk_levels = ["low", "medium", "high"]
            
            # Sample session summaries
            summaries = [
                "Feeling stressed about upcoming project deadline.",
                "Had a productive week, but concerned about workload.",
                "Struggling with work-life balance while working remotely.",
                "Excited about new project, but anxious about expectations.",
                "Feeling overwhelmed with multiple competing priorities.",
                "Concerned about team communication issues.",
                "Enjoying the current project and team collaboration.",
                "Worried about upcoming performance review."
            ]
            
            # Sample LLM responses
            llm_responses = [
                "I understand you're feeling stressed about the deadline. Let's break down your concerns and identify some strategies to manage your workload effectively.",
                "It sounds like you've had a productive week, which is great! However, I hear your concern about the workload. Let's discuss some prioritization techniques.",
                "Work-life balance can be particularly challenging in a remote environment. Let's explore some boundaries you could set to create more separation.",
                "It's natural to feel both excited and anxious about new opportunities. Let's talk about how you can manage those expectations and set yourself up for success.",
                "When you're juggling multiple priorities, it can definitely feel overwhelming. Let's work on a system to help you organize and prioritize your tasks."
            ]
            
            # Create sample employees
            employee_ids = []
            for i in range(len(employee_names)):
                employee_id = str(uuid.uuid4())
                employee_ids.append(employee_id)
                
                name = employee_names[i]
                email = f"{name.lower().replace(' ', '.')}@example.com"
                team = random.choice(teams)
                stressors = json.dumps(random.choice(stressors_list))
                
                # Random date in the past 30 days
                onboarding_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")
                
                result = client.execute(
                    """INSERT INTO employees (id, name, email, github_url, linkedin_url, team, stressors, onboarding_date) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (employee_id, name, email, f"https://github.com/{name.lower().replace(' ', '')}", 
                     f"https://linkedin.com/in/{name.lower().replace(' ', '-')}", team, stressors, onboarding_date)
                )
                
                if not result:
                    logger.error(f"Failed to insert employee {name}")
                    return False
            
            # Create sample sessions for each employee
            for employee_id in employee_ids:
                # Create 3-7 sessions per employee
                num_sessions = random.randint(3, 7)
                for j in range(num_sessions):
                    session_id = str(uuid.uuid4())
                    
                    # Random date in the past 14 days, with more recent sessions having later dates
                    days_ago = int(14 * (1 - j/num_sessions))
                    session_time = (datetime.now() - timedelta(days=days_ago, 
                                                             hours=random.randint(0, 23), 
                                                             minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")
                    
                    mood = random.choice(moods)
                    summary = random.choice(summaries)
                    llm_response = random.choice(llm_responses)
                    
                    # Determine risk level based on mood
                    if mood in ["happy", "neutral"]:
                        risk_level = "low"
                    elif mood == "stressed":
                        risk_level = "medium"
                    else:  # anxious or overwhelmed
                        risk_level = "high"
                    
                    result = client.execute(
                        """INSERT INTO sessions (session_id, employee_id, session_time, mood, summary, llm_response, risk_level) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (session_id, employee_id, session_time, mood, summary, llm_response, risk_level)
                    )
                    
                    if not result:
                        logger.error(f"Failed to insert session for employee {employee_id}")
                        return False
            
            # Create sample HR insights
            for employee_id in employee_ids:
                insight_id = str(uuid.uuid4())
                
                weekly_summary = "Employee has been showing consistent engagement with the platform. "
                weekly_summary += random.choice(["Mood has been improving.", "Mood has been stable.", "Mood has been declining."])
                
                flags = json.dumps(random.sample(["workload", "stress", "work-life balance", "team dynamics", "communication"], k=random.randint(0, 3)))
                
                trends = json.dumps({
                    "mood": random.choice(["improving", "stable", "declining"]),
                    "engagement": random.choice(["high", "medium", "low"]),
                    "risk_level": random.choice(risk_levels)
                })
                
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                result = client.execute(
                    """INSERT INTO hr_insights (id, employee_id, weekly_summary, flags, trends, created_at) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (insight_id, employee_id, weekly_summary, flags, trends, created_at)
                )
                
                if not result:
                    logger.error(f"Failed to insert HR insight for employee {employee_id}")
                    return False
            
            logger.info(f"Seeded database with {len(employee_ids)} employees and their sessions")
            client.close()
            return True
        except Exception as e:
            logger.error(f"Error seeding sample data: {e}")
            return False
    else:
        logger.info("Skipping sample data seeding in production environment")
        return True

# Function to run during application startup
def init_db() -> bool:
    """Initialize the database with required tables and sample data"""
    try:
        tables_success = init_snowflake_tables()
        if not tables_success:
            return False
            
        seed_success = seed_sample_data()
        if not seed_success:
            logger.warning("Failed to seed sample data, but tables were created successfully")
            
        return tables_success
    except Exception as e:
        logger.error(f"Error initializing Snowflake database: {e}")
        return False

if __name__ == "__main__":
    init_db()