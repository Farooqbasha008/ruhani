import uuid
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from ..core.config import settings
from ..services.groq import GroqClient
from ..services.elevenlabs import ElevenLabsClient
from ..services.coral import CoralClient
from ..db.snowflake_client import SnowflakeClient
from ..models.employee import (
    VoiceSessionRequest, VoiceSessionResponse, SessionRecord,
    SentimentLogRequest, WellnessCheckRequest
)

class SessionService:
    def __init__(self):
        self.groq_client = GroqClient()
        self.elevenlabs_client = ElevenLabsClient()
        self.coral_client = CoralClient()
        self.db_client = SnowflakeClient()

    async def process_voice_session(self, request: VoiceSessionRequest) -> VoiceSessionResponse:
        """Process a complete voice-based therapy session"""
        session_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # 1. Decode and transcribe audio
            audio_data = base64.b64decode(request.audio_data)
            transcription_result = await self.groq_client.transcribe_audio(audio_data)
            transcript = transcription_result.get("transcript", "")
            
            if not transcript.strip():
                return VoiceSessionResponse(
                    success=False,
                    session_id=session_id,
                    transcript="",
                    ai_response="I couldn't hear you clearly. Could you please try speaking again?",
                    audio_response=None,
                    sentiment_analysis={"sentiment": "neutral", "mood_score": 3.0},
                    mood_score=3.0,
                    recommendations=["Try speaking more clearly", "Check your microphone"],
                    follow_up_needed=False
                )

            # 2. Analyze sentiment and emotional state
            sentiment_result = await self.groq_client.analyze_sentiment(transcript)
            mood_score = sentiment_result.get("mood_score", 3.0)
            
            # 3. Generate empathetic AI response
            context = f"Employee mood: {mood_score}/5. Previous context: {request.session_context or 'First session'}"
            ai_response_result = await self.groq_client.consult_llm(
                prompt=transcript,
                context=context
            )
            ai_response = ai_response_result.get("response", "I'm here to support you.")

            # 4. Generate voice response
            tts_result = await self.elevenlabs_client.generate_tts(ai_response)
            audio_response = tts_result.get("audio_url")

            # 5. Generate recommendations based on sentiment
            recommendations = await self._generate_recommendations(sentiment_result, mood_score)
            
            # 6. Determine if follow-up is needed
            follow_up_needed = mood_score <= settings.MOOD_THRESHOLDS["warning"]

            # 7. Log session to database
            await self._log_session(session_id, request.employee_id, transcript, ai_response, mood_score, sentiment_result)

            # 8. Log activity to Coral Protocol
            await self._log_activity(request.employee_id, session_id, "voice_session", sentiment_result)

            return VoiceSessionResponse(
                success=True,
                session_id=session_id,
                transcript=transcript,
                ai_response=ai_response,
                audio_response=audio_response,
                sentiment_analysis=sentiment_result,
                mood_score=mood_score,
                recommendations=recommendations,
                follow_up_needed=follow_up_needed
            )

        except Exception as e:
            print(f"Session processing error: {e}")
            return VoiceSessionResponse(
                success=False,
                session_id=session_id,
                transcript="",
                ai_response="I'm experiencing technical difficulties. Please try again in a moment.",
                audio_response=None,
                sentiment_analysis={"sentiment": "neutral", "mood_score": 3.0},
                mood_score=3.0,
                recommendations=["Try again later", "Contact support if issue persists"],
                follow_up_needed=False
            )

    async def _generate_recommendations(self, sentiment_result: Dict[str, Any], mood_score: float) -> List[str]:
        """Generate personalized wellness recommendations"""
        recommendations = []
        
        # Base recommendations on mood score
        if mood_score <= 2.0:
            recommendations.extend([
                "Consider taking a short break to breathe deeply",
                "Try some gentle stretching exercises",
                "Reach out to a trusted colleague or friend"
            ])
        elif mood_score <= 3.0:
            recommendations.extend([
                "Take a moment to reflect on what's going well",
                "Consider a brief walk outside",
                "Practice some positive self-talk"
            ])
        else:
            recommendations.extend([
                "Great energy! Keep up the positive momentum",
                "Consider sharing your good mood with others",
                "Use this energy to tackle challenging tasks"
            ])

        # Add emotion-specific recommendations
        emotions = sentiment_result.get("emotions", [])
        if "stress" in emotions or "anxiety" in emotions:
            recommendations.append("Try the 4-7-8 breathing technique")
        if "loneliness" in emotions:
            recommendations.append("Consider joining a team activity or social event")
        if "overwhelm" in emotions:
            recommendations.append("Break down tasks into smaller, manageable steps")

        return recommendations[:5]  # Limit to 5 recommendations

    async def _log_session(self, session_id: str, employee_id: str, transcript: str, 
                          ai_response: str, mood_score: float, sentiment_result: Dict[str, Any]):
        """Log session to Snowflake database"""
        try:
            query = """
            INSERT INTO employee_sessions (
                session_id, employee_id, session_type, start_time, status,
                transcript, ai_response, mood_score, sentiment_analysis, created_at
            ) VALUES (%(session_id)s, %(employee_id)s, %(session_type)s, %(start_time)s, %(status)s, %(transcript)s, %(ai_response)s, %(mood_score)s, %(sentiment_analysis)s, %(created_at)s)
            """
            
            params = {
                "session_id": session_id,
                "employee_id": employee_id,
                "session_type": "voice_check_in",
                "start_time": datetime.utcnow(),
                "status": "completed",
                "transcript": transcript,
                "ai_response": ai_response,
                "mood_score": mood_score,
                "sentiment_analysis": json.dumps(sentiment_result),
                "created_at": datetime.utcnow()
            }
            
            self.db_client.execute(query, params)
        except Exception as e:
            print(f"Database logging error: {e}")

    async def _log_activity(self, employee_id: str, session_id: str, activity_type: str, data: Dict[str, Any]):
        """Log activity to Coral Protocol"""
        try:
            activity_data = {
                "employee_id": employee_id,
                "session_id": session_id,
                "activity_type": activity_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            await self.coral_client.log_activity(activity_data)
        except Exception as e:
            print(f"Coral logging error: {e}")

    async def get_employee_wellness_summary(self, employee_id: str) -> Dict[str, Any]:
        """Get comprehensive wellness summary for an employee"""
        try:
            query = """
            SELECT 
                AVG(mood_score) as avg_mood,
                COUNT(*) as total_sessions,
                MAX(start_time) as last_session,
                AVG(CASE WHEN mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage
            FROM employee_sessions 
            WHERE employee_id = %(employee_id)s AND status = 'completed'
            """
            
            result = self.db_client.execute(query, {"employee_id": employee_id})
            
            if result:
                row = result[0]
                avg_mood = row[0] or 3.0
                total_sessions = row[1] or 0
                last_session = row[2]
                low_mood_percentage = row[3] or 0.0
                
                # Determine wellness status
                if avg_mood >= 4.0 and low_mood_percentage < 0.2:
                    wellness_status = "excellent"
                elif avg_mood >= 3.0 and low_mood_percentage < 0.4:
                    wellness_status = "stable"
                elif avg_mood >= 2.5:
                    wellness_status = "improving"
                elif low_mood_percentage > 0.6:
                    wellness_status = "at_risk"
                else:
                    wellness_status = "declining"
                
                return {
                    "employee_id": employee_id,
                    "average_mood": avg_mood,
                    "total_sessions": total_sessions,
                    "last_session": last_session,
                    "low_mood_percentage": low_mood_percentage,
                    "wellness_status": wellness_status,
                    "recommendations": await self._get_wellness_recommendations(avg_mood, low_mood_percentage)
                }
            
            return {
                "employee_id": employee_id,
                "average_mood": 3.0,
                "total_sessions": 0,
                "last_session": None,
                "low_mood_percentage": 0.0,
                "wellness_status": "stable",
                "recommendations": ["Start with regular check-ins"]
            }
            
        except Exception as e:
            print(f"Wellness summary error: {e}")
            return {
                "employee_id": employee_id,
                "error": "Unable to retrieve wellness data"
            }

    async def _get_wellness_recommendations(self, avg_mood: float, low_mood_percentage: float) -> List[str]:
        """Get personalized wellness recommendations based on data"""
        recommendations = []
        
        if avg_mood < 2.5:
            recommendations.append("Consider scheduling a longer therapy session")
            recommendations.append("Reach out to HR for additional support resources")
        
        if low_mood_percentage > 0.5:
            recommendations.append("Monitor mood patterns more closely")
            recommendations.append("Consider stress management techniques")
        
        if avg_mood >= 4.0:
            recommendations.append("Great progress! Continue with current wellness practices")
        
        return recommendations 