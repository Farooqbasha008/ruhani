import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..models.employee import EmployeeOnboardRequest, EmployeeOnboardResponse, SessionRequest, SessionResponse, SentimentLogRequest, SentimentLogResponse
from ..services.fetchai import FetchAIClient
from ..services.groq import GroqClient
from ..services.elevenlabs import ElevenLabsClient
from ..services.coral import CoralClient
from ..db.snowflake_client import SnowflakeClient
from typing import Dict, Any
import json
import base64
from datetime import datetime

router = APIRouter()

@router.post("/onboard", response_model=EmployeeOnboardResponse)
async def onboard_employee(payload: EmployeeOnboardRequest, background_tasks: BackgroundTasks):
    """Onboard a new employee by fetching public info and storing in Snowflake"""
    try:
        # Generate a unique ID for the employee
        employee_id = str(uuid.uuid4())
        
        # Fetch public info from FetchAI
        fetchai_client = FetchAIClient()
        public_info = await fetchai_client.fetch_public_info(
            github=payload.github, 
            linkedin=payload.linkedin
        )
        await fetchai_client.close()
        
        # Store in Snowflake
        snowflake_client = SnowflakeClient()
        
        # Extract name from public info or use provided name
        name = payload.name
        if "public_info" in public_info and "name" in public_info["public_info"]:
            name = public_info["public_info"]["name"]
        
        # Extract skills and interests as potential stressors
        stressors = []
        if "public_info" in public_info:
            if "skills" in public_info["public_info"]:
                stressors.extend(public_info["public_info"]["skills"])
            if "interests" in public_info["public_info"]:
                stressors.extend(public_info["public_info"]["interests"])
        
        # Insert employee data into Snowflake
        snowflake_client.execute(
            """INSERT INTO employees (id, name, email, github_url, linkedin_url, team, stressors) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (employee_id, name, f"{name.lower().replace(' ', '.')}@example.com", 
             payload.github, payload.linkedin, payload.role, json.dumps(stressors))
        )
        
        # Log activity via Coral in the background
        background_tasks.add_task(log_onboarding_activity, employee_id, payload, public_info)
        
        return EmployeeOnboardResponse(
            success=True, 
            message=f"Successfully onboarded {name}",
            employee_id=employee_id
        )
    except Exception as e:
        print(f"Error in onboard_employee: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error onboarding employee: {str(e)}")

@router.post("/session", response_model=SessionResponse)
async def process_session(payload: SessionRequest, background_tasks: BackgroundTasks):
    """Process an employee session with audio transcription, LLM consultation, and TTS response"""
    try:
        # Generate a unique ID for the session
        session_id = str(uuid.uuid4())
        
        # Initialize clients
        groq_client = GroqClient()
        elevenlabs_client = ElevenLabsClient()
        
        # For now, we'll use a mock transcript since we don't have actual audio processing
        # In a real implementation, you would use the audio_url to download and process the audio
        transcript = "I've been feeling stressed about the upcoming project deadline. "
        transcript += "The requirements keep changing and I'm not sure if we'll be able to deliver on time."
        
        # If there's an audio_url, we would transcribe it
        if payload.audio_url:
            # This is a placeholder - in a real implementation, you would download the audio
            # and pass it to the transcribe_audio method
            # transcript_result = await groq_client.transcribe_audio(audio_data)
            # transcript = transcript_result["transcript"]
            pass
        
        # Prepare system prompt for the LLM
        system_prompt = """
        You are Ruhani, an empathetic AI assistant designed to support employees' mental well-being.
        Your goal is to listen, understand, and provide supportive responses that help employees
        manage stress and improve their mental health. Be compassionate, non-judgmental, and helpful.
        Keep your responses concise (2-3 paragraphs maximum) and focused on providing practical advice.
        """
        
        # Prepare user prompt based on transcript
        user_prompt = f"""Based on this employee's statement: \"{transcript}\", 
        provide a supportive and helpful response. Acknowledge their feelings, 
        offer practical advice, and suggest resources or techniques that might help.
        """
        
        # Get LLM response
        llm_result = await groq_client.consult_llm(user_prompt, system_prompt)
        llm_response = llm_result.get("response", "I understand you're feeling stressed. Let's work through this together.")
        
        # Generate TTS response
        tts_result = await elevenlabs_client.generate_tts(llm_response)
        
        # Close clients
        await groq_client.close()
        await elevenlabs_client.close()
        
        # Determine risk level based on transcript content
        risk_level = "low"
        if "stressed" in transcript.lower() or "anxiety" in transcript.lower():
            risk_level = "medium"
        if "overwhelmed" in transcript.lower() or "can't handle" in transcript.lower():
            risk_level = "high"
        
        # Store session in Snowflake
        snowflake_client = SnowflakeClient()
        snowflake_client.execute(
            """INSERT INTO sessions (session_id, employee_id, mood, summary, llm_response, risk_level) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (session_id, payload.employee_id, "stressed", transcript, llm_response, risk_level)
        )
        
        # Log activity via Coral in the background
        background_tasks.add_task(log_session_activity, session_id, payload.employee_id, transcript, llm_response)
        
        return SessionResponse(
            success=True,
            message="Session processed successfully",
            session_id=session_id,
            transcript=transcript,
            response=llm_response,
            audio_data=tts_result.get("audio_data", ""),
            risk_level=risk_level
        )
    except Exception as e:
        print(f"Error in process_session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing session: {str(e)}")

@router.post("/sentiment", response_model=SentimentLogResponse)
async def log_sentiment(payload: SentimentLogRequest, background_tasks: BackgroundTasks):
    """Log employee sentiment from various sources"""
    try:
        # Generate a unique ID for the sentiment log
        log_id = str(uuid.uuid4())
        
        # Store sentiment in Snowflake
        snowflake_client = SnowflakeClient()
        timestamp = payload.timestamp or datetime.utcnow().isoformat()
        
        # For simplicity, we'll store this in the sessions table
        snowflake_client.execute(
            """INSERT INTO sessions (session_id, employee_id, mood, summary, risk_level) 
               VALUES (%s, %s, %s, %s, %s)""",
            (log_id, payload.employee_id, payload.sentiment, 
             f"Sentiment from {payload.source}: {payload.score}", 
             "low" if payload.score > 0.5 else "medium")
        )
        
        # Log activity via Coral in the background
        background_tasks.add_task(log_sentiment_activity, payload)
        
        return SentimentLogResponse(
            success=True,
            message=f"Sentiment logged successfully from {payload.source}",
            log_id=log_id
        )
    except Exception as e:
        print(f"Error in log_sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging sentiment: {str(e)}")

# Background tasks for logging activities
async def log_onboarding_activity(employee_id: str, payload: EmployeeOnboardRequest, public_info: Dict[str, Any]):
    """Log onboarding activity to Coral Protocol"""
    try:
        coral_client = CoralClient()
        activity = {
            "activity_type": "employee_onboarding",
            "employee_id": employee_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "name": payload.name,
                "role": payload.role,
                # Anonymize URLs for privacy
                "github_provided": bool(payload.github),
                "linkedin_provided": bool(payload.linkedin),
                "public_info_fetched": bool(public_info and "public_info" in public_info)
            }
        }
        await coral_client.log_activity(activity)
        await coral_client.close()
    except Exception as e:
        print(f"Error logging onboarding activity: {str(e)}")

async def log_session_activity(session_id: str, employee_id: str, transcript: str, response: str):
    """Log session activity to Coral Protocol"""
    try:
        coral_client = CoralClient()
        
        # Anonymize the transcript and response
        anonymized_data = await coral_client.anonymize_data(
            {"transcript": transcript, "response": response},
            ["transcript", "response"]
        )
        
        activity = {
            "activity_type": "employee_session",
            "employee_id": employee_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "transcript_length": len(transcript),
                "response_length": len(response),
                "anonymized": anonymized_data.get("anonymized", {})
            }
        }
        await coral_client.log_activity(activity)
        await coral_client.close()
    except Exception as e:
        print(f"Error logging session activity: {str(e)}")

async def log_sentiment_activity(payload: SentimentLogRequest):
    """Log sentiment activity to Coral Protocol"""
    try:
        coral_client = CoralClient()
        activity = {
            "activity_type": "sentiment_log",
            "employee_id": payload.employee_id,
            "timestamp": payload.timestamp or datetime.utcnow().isoformat(),
            "details": {
                "source": payload.source,
                "sentiment": payload.sentiment,
                "score": payload.score
            }
        }
        await coral_client.log_activity(activity)
        await coral_client.close()
    except Exception as e:
        print(f"Error logging sentiment activity: {str(e)}")