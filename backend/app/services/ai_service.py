from typing import Dict, Optional
import openai
import os
from app.core.config import settings
from app.models.session import WellnessSession
from app.utils.logger import logger

class AIService:
    def __init__(self):
        # Initialize AI services with API keys
        openai.api_key = settings.OPENAI_API_KEY
        # Could add other AI providers here

    def analyze_session(self, session: WellnessSession) -> Dict:
        """Analyze a wellness session using AI models"""
        try:
            # Basic analysis based on available data
            analysis = {
                "wellness_score": self._calculate_wellness_score(session),
                "risk_assessment": self._assess_risk(session),
                "recommendations": self._generate_recommendations(session),
                "insights": self._generate_insights(session)
            }
            
            # If we have text data, we could use OpenAI here
            if session.session_type == "emergency" and settings.OPENAI_API_KEY:
                analysis.update(self._advanced_analysis(session))
                
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "wellness_score": None,
                "risk_assessment": "unknown",
                "recommendations": None,
                "insights": None
            }

    def _calculate_wellness_score(self, session: WellnessSession) -> float:
        """Calculate a composite wellness score (0-1)"""
        mood_score = {
            "very_sad": 0.1,
            "sad": 0.3,
            "neutral": 0.6,
            "happy": 0.8,
            "very_happy": 1.0
        }.get(session.mood_level, 0.5)
        
        # Adjust based on stress indicators if available
        if session.voice_stress_indicators is not None:
            stress_factor = 1 - (session.voice_stress_indicators * 0.5)
            mood_score *= stress_factor
            
        return min(max(mood_score, 0.1), 1.0)

    def _assess_risk(self, session: WellnessSession) -> str:
        """Assess risk level based on session data"""
        if session.mood_level in ["very_sad", "sad"]:
            if session.voice_stress_indicators and session.voice_stress_indicators > 0.7:
                return "high"
            return "medium"
        return "low"

    def _generate_recommendations(self, session: WellnessSession) -> str:
        """Generate basic recommendations"""
        if session.mood_level == "very_sad":
            return "Consider reaching out to our Employee Assistance Program for support."
        elif session.mood_level == "sad":
            return "Try a 5-minute mindfulness exercise to improve your mood."
        return "Keep up with your regular wellness check-ins."

    def _generate_insights(self, session: WellnessSession) -> str:
        """Generate basic insights"""
        if session.mood_level in ["happy", "very_happy"]:
            return "Your positive mood suggests good overall wellness."
        elif session.mood_level == "neutral":
            return "Your neutral mood suggests stability in your current state."
        return "Your mood suggests you might benefit from additional support."

    def _advanced_analysis(self, session: WellnessSession) -> Dict:
        """Use OpenAI for more advanced analysis when needed"""
        if not settings.OPENAI_API_KEY:
            return {}
            
        try:
            prompt = f"""
            Analyze this mental wellness session:
            Mood: {session.mood_level}
            Emotional State: {session.emotional_state}
            Stress Indicators: {session.voice_stress_indicators}
            
            Provide a concise analysis focusing on:
            1. Key emotional patterns
            2. Potential risk factors
            3. Personalized recommendations
            
            Response format:
            Analysis: [text]
            Risk Factors: [text]
            Recommendations: [text]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a mental wellness expert."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return {
                "ai_insights": content
            }
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            return {}