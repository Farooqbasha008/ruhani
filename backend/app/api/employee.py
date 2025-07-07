import uuid
import hashlib
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from ..models.employee import (
    EmployeeOnboardRequest, EmployeeOnboardResponse, SessionRequest, SessionResponse, 
    SentimentLogRequest, SentimentLogResponse, ConsentRequest, ConsentResponse,
    VerifiableCredential, VerifiablePresentation
)
from ..services.fetchai import FetchAIClient
from ..services.groq import GroqClient
from ..services.elevenlabs import ElevenLabsClient
from ..services.coral import CoralClient
from ..db.snowflake_client import SnowflakeClient
from typing import Dict, Any, List, Optional
import json
import base64
from datetime import datetime, timedelta

router = APIRouter()

# Organization DID for issuing credentials
ORG_DID = None

# Get or create organization DID
async def get_org_did() -> str:
    """Get or create the organization DID"""
    global ORG_DID
    if ORG_DID:
        return ORG_DID
    
    # Check if org DID exists in database
    snowflake_client = SnowflakeClient()
    result = snowflake_client.execute(
        "SELECT did FROM organization WHERE id = 'ruhani'"
    )
    
    if result and result[0] and result[0][0]:
        ORG_DID = result[0][0]
        return ORG_DID
    
    # Create new org DID
    coral_client = CoralClient()
    try:
        did_result = await coral_client.create_did(
            employee_id="ruhani-organization",
            name="Ruhani Organization",
            email="admin@ruhani.ai"
        )
        
        if "error" in did_result:
            # Fall back to a deterministic mock DID
            ORG_DID = f"did:coral:{hashlib.sha256('ruhani-organization'.encode()).hexdigest()[:16]}"
        else:
            ORG_DID = did_result["did"]
        
        # Store org DID in database
        snowflake_client.execute(
            "INSERT INTO organization (id, name, did, did_document) VALUES (%s, %s, %s, PARSE_JSON(%s))",
            ("ruhani", "Ruhani Organization", ORG_DID, str(did_result.get("did_document", {})).replace("'", '"'))
        )
        
        return ORG_DID
    finally:
        await coral_client.close()

@router.post("/onboard", response_model=EmployeeOnboardResponse)
async def onboard_employee(payload: EmployeeOnboardRequest, background_tasks: BackgroundTasks):
    """Onboard a new employee by fetching public info, creating DID, and storing in Snowflake"""
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
        
        # Create DID for employee using Coral Protocol
        coral_client = CoralClient()
        try:
            # Create DID for the employee
            did_result = await coral_client.create_did(
                employee_id=employee_id,
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com"
            )
            
            if "error" in did_result:
                raise HTTPException(status_code=500, detail=f"Failed to create DID: {did_result['error']}")
            
            employee_did = did_result["did"]
            did_document = did_result["did_document"]
            
            # Store in Snowflake
            snowflake_client = SnowflakeClient()
            
            # Insert employee data into Snowflake with DID information
            snowflake_client.execute(
                """INSERT INTO employees (id, name, email, github_url, linkedin_url, team, stressors, did, did_document) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s))""",
                (employee_id, name, f"{name.lower().replace(' ', '.')}@example.com", 
                 payload.github, payload.linkedin, payload.role, json.dumps(stressors),
                 employee_did, str(did_document).replace("'", '"'))
            )
            
            # Create initial consent credential in background
            background_tasks.add_task(
                create_initial_consent, 
                employee_id=employee_id, 
                employee_did=employee_did,
                name=name
            )
            
            return EmployeeOnboardResponse(
                success=True, 
                message=f"Successfully onboarded {name}",
                employee_id=employee_id,
                did=employee_did
            )
        finally:
            await coral_client.close()
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
        
        # Create a hash of the summary for privacy
        summary_hash = hashlib.sha256(transcript.encode()).hexdigest()
        
        # Store session in Snowflake
        snowflake_client = SnowflakeClient()
        snowflake_client.execute(
            """INSERT INTO sessions (session_id, employee_id, mood, summary, llm_response, risk_level, summary_hash) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (session_id, payload.employee_id, "stressed", transcript, llm_response, risk_level, summary_hash)
        )
        
        # Create session credential in background
        background_tasks.add_task(
            create_session_credential,
            session_id=session_id,
            employee_id=payload.employee_id,
            mood="stressed",
            summary_hash=summary_hash,
            risk_level=risk_level
        )
        
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
        
        # Update session credential in background if needed
        background_tasks.add_task(
            update_session_with_sentiment,
            employee_id=payload.employee_id,
            sentiment_score=payload.score
        )
        
        return SentimentLogResponse(
            success=True,
            message=f"Sentiment logged successfully from {payload.source}",
            log_id=log_id
        )
    except Exception as e:
        print(f"Error in log_sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging sentiment: {str(e)}")

@router.post("/consent", response_model=ConsentResponse)
async def create_consent(payload: ConsentRequest):
    """Create a consent record with verifiable credential"""
    try:
        # Generate a unique consent ID
        consent_id = str(uuid.uuid4())
        granted_at = datetime.utcnow()
        expires_at = granted_at + timedelta(days=payload.expiration_days)
        
        # Get employee DID
        snowflake_client = SnowflakeClient()
        employee_result = snowflake_client.execute(
            "SELECT did FROM employees WHERE id = %s",
            (payload.employee_id,)
        )
        
        if not employee_result or not employee_result[0] or not employee_result[0][0]:
            raise HTTPException(status_code=404, detail="Employee not found or DID not available")
        
        employee_did = employee_result[0][0]
        
        # Get organization DID
        org_did = await get_org_did()
        
        # Create consent credential
        coral_client = CoralClient()
        try:
            consent_result = await coral_client.create_consent_credential(
                issuer_did=employee_did,  # Employee issues consent
                subject_did=org_did,       # Organization is the subject
                data_categories=payload.data_categories,
                authorized_parties=[org_did],
                purpose=payload.purpose,
                expiration_days=payload.expiration_days
            )
            
            if "error" in consent_result:
                raise HTTPException(status_code=500, detail=f"Failed to create consent credential: {consent_result['error']}")
            
            credential_id = consent_result["credential"]["id"]
            
            # Store credential in database
            credential_data = str(consent_result["credential"]).replace("'", '"')
            snowflake_client.execute(
                """INSERT INTO credentials 
                   (credential_id, credential_type, issuer_did, subject_did, issuance_date, expiration_date, credential_data) 
                   VALUES (%s, %s, %s, %s, %s, %s, PARSE_JSON(%s))""",
                (credential_id, "ConsentCredential", employee_did, org_did, granted_at.isoformat(), 
                 expires_at.isoformat(), credential_data)
            )
            
            # Store consent record
            snowflake_client.execute(
                """INSERT INTO consent_records 
                   (consent_id, employee_id, data_categories, authorized_parties, purpose, credential_id, granted_at, expires_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (consent_id, payload.employee_id, json.dumps(payload.data_categories), json.dumps([org_did]), 
                 payload.purpose, credential_id, granted_at.isoformat(), expires_at.isoformat())
            )
            
            return ConsentResponse(
                success=True,
                message="Consent created successfully",
                consent_id=consent_id,
                employee_id=payload.employee_id,
                data_categories=payload.data_categories,
                authorized_parties=[org_did],
                purpose=payload.purpose,
                credential_id=credential_id,
                granted_at=granted_at,
                expires_at=expires_at
            )
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error in create_consent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating consent: {str(e)}")

# Background tasks for Coral Protocol credential issuance
async def create_initial_consent(employee_id: str, employee_did: str, name: str):
    """Create initial consent credential for new employee"""
    try:
        # Default consent parameters
        data_categories = ["wellness_metrics", "session_summaries", "risk_assessments"]
        purpose = "Wellness monitoring and HR insights"
        expiration_days = 90
        
        # Get organization DID
        org_did = await get_org_did()
        
        # Create consent credential
        coral_client = CoralClient()
        try:
            consent_result = await coral_client.create_consent_credential(
                issuer_did=employee_did,  # Employee issues consent
                subject_did=org_did,       # Organization is the subject
                data_categories=data_categories,
                authorized_parties=[org_did],
                purpose=purpose,
                expiration_days=expiration_days
            )
            
            if "error" in consent_result:
                print(f"Failed to create initial consent credential for {name}: {consent_result['error']}")
                return
            
            # Generate a unique consent ID
            consent_id = str(uuid.uuid4())
            granted_at = datetime.utcnow()
            expires_at = granted_at + timedelta(days=expiration_days)
            credential_id = consent_result["credential"]["id"]
            
            # Store credential in database
            snowflake_client = SnowflakeClient()
            credential_data = str(consent_result["credential"]).replace("'", '"')
            snowflake_client.execute(
                """INSERT INTO credentials 
                   (credential_id, credential_type, issuer_did, subject_did, issuance_date, expiration_date, credential_data) 
                   VALUES (%s, %s, %s, %s, %s, %s, PARSE_JSON(%s))""",
                (credential_id, "ConsentCredential", employee_did, org_did, granted_at.isoformat(), 
                 expires_at.isoformat(), credential_data)
            )
            
            # Store consent record
            snowflake_client.execute(
                """INSERT INTO consent_records 
                   (consent_id, employee_id, data_categories, authorized_parties, purpose, credential_id, granted_at, expires_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (consent_id, employee_id, json.dumps(data_categories), json.dumps([org_did]), 
                 purpose, credential_id, granted_at.isoformat(), expires_at.isoformat())
            )
            
            print(f"Created initial consent credential for {name}")
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error creating initial consent: {str(e)}")

async def create_session_credential(session_id: str, employee_id: str, mood: str, summary_hash: str, risk_level: str = "low"):
    """Create verifiable credential for a wellness session"""
    try:
        # Get employee DID
        snowflake_client = SnowflakeClient()
        employee_result = snowflake_client.execute(
            "SELECT did FROM employees WHERE id = %s",
            (employee_id,)
        )
        
        if not employee_result or not employee_result[0] or not employee_result[0][0]:
            print(f"Employee not found or DID not available for employee_id: {employee_id}")
            return
        
        employee_did = employee_result[0][0]
        
        # Get organization DID
        org_did = await get_org_did()
        
        # Create session credential
        coral_client = CoralClient()
        try:
            credential_result = await coral_client.create_session_credential(
                issuer_did=org_did,
                subject_did=employee_did,
                session_id=session_id,
                session_date=datetime.utcnow().isoformat(),
                mood=mood,
                risk_level=risk_level,
                summary_hash=summary_hash
            )
            
            if "error" in credential_result:
                print(f"Failed to create session credential: {credential_result['error']}")
                return
            
            credential_id = credential_result["credential"]["id"]
            issuance_date = datetime.utcnow()
            expiration_date = issuance_date + timedelta(days=365)
            
            # Store credential in database
            credential_data = str(credential_result["credential"]).replace("'", '"')
            snowflake_client.execute(
                """INSERT INTO credentials 
                   (credential_id, credential_type, issuer_did, subject_did, issuance_date, expiration_date, credential_data) 
                   VALUES (%s, %s, %s, %s, %s, %s, PARSE_JSON(%s))""",
                (credential_id, "WellnessSessionCredential", org_did, employee_did, issuance_date.isoformat(), 
                 expiration_date.isoformat(), credential_data)
            )
            
            # Update session with credential ID
            snowflake_client.execute(
                "UPDATE sessions SET credential_id = %s WHERE session_id = %s",
                (credential_id, session_id)
            )
            
            print(f"Created session credential for session {session_id}")
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error creating session credential: {str(e)}")

async def update_session_with_sentiment(employee_id: str, sentiment_score: float):
    """Update the most recent session credential with sentiment data"""
    try:
        # Get the most recent session for this employee
        snowflake_client = SnowflakeClient()
        session_result = snowflake_client.execute(
            """SELECT session_id, credential_id FROM sessions 
               WHERE employee_id = %s ORDER BY created_at DESC LIMIT 1""",
            (employee_id,)
        )
        
        if not session_result or not session_result[0] or not session_result[0][1]:
            # No recent session with credential found
            return
        
        session_id = session_result[0][0]
        credential_id = session_result[0][1]
        
        # Get employee DID
        employee_result = snowflake_client.execute(
            "SELECT did FROM employees WHERE id = %s",
            (employee_id,)
        )
        
        if not employee_result or not employee_result[0] or not employee_result[0][0]:
            return
        
        employee_did = employee_result[0][0]
        
        # Get organization DID
        org_did = await get_org_did()
        
        # Revoke the old credential
        coral_client = CoralClient()
        try:
            revoke_result = await coral_client.revoke_credential(
                credential_id=credential_id,
                issuer_did=org_did
            )
            
            if "error" in revoke_result:
                print(f"Failed to revoke credential: {revoke_result['error']}")
                return
            
            # Update credential status in database
            snowflake_client.execute(
                "UPDATE credentials SET revoked = TRUE, revocation_date = %s WHERE credential_id = %s",
                (datetime.utcnow().isoformat(), credential_id)
            )
            
            # Get session details to create updated credential
            session_details = snowflake_client.execute(
                "SELECT mood, summary_hash, risk_level FROM sessions WHERE session_id = %s",
                (session_id,)
            )
            
            if not session_details or not session_details[0]:
                return
            
            mood = session_details[0][0]
            summary_hash = session_details[0][1]
            risk_level = session_details[0][2] or "low"
            
            # Create updated session credential with sentiment data
            new_credential_result = await coral_client.create_session_credential(
                issuer_did=org_did,
                subject_did=employee_did,
                session_id=session_id,
                session_date=datetime.utcnow().isoformat(),
                mood=mood,
                risk_level=risk_level,
                summary_hash=summary_hash,
                sentiment_score=sentiment_score
            )
            
            if "error" in new_credential_result:
                print(f"Failed to create updated session credential: {new_credential_result['error']}")
                return
            
            new_credential_id = new_credential_result["credential"]["id"]
            issuance_date = datetime.utcnow()
            expiration_date = issuance_date + timedelta(days=365)
            
            # Store new credential in database
            credential_data = str(new_credential_result["credential"]).replace("'", '"')
            snowflake_client.execute(
                """INSERT INTO credentials 
                   (credential_id, credential_type, issuer_did, subject_did, issuance_date, expiration_date, credential_data) 
                   VALUES (%s, %s, %s, %s, %s, %s, PARSE_JSON(%s))""",
                (new_credential_id, "WellnessSessionCredential", org_did, employee_did, issuance_date.isoformat(), 
                 expiration_date.isoformat(), credential_data)
            )
            
            # Update session with new credential ID
            snowflake_client.execute(
                "UPDATE sessions SET credential_id = %s WHERE session_id = %s",
                (new_credential_id, session_id)
            )
            
            print(f"Updated session credential with sentiment data for session {session_id}")
        finally:
            await coral_client.close()
    except Exception as e:
        print(f"Error updating session with sentiment: {str(e)}")