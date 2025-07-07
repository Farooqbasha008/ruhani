import os
import groq
from app.core.config import settings
from app.utils.logger import logger

class GroqService:
    def __init__(self):
        self.client = groq.Client(api_key=settings.GROQ_API_KEY)
    
    async def generate_mental_health_response(self, user_input: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"""As a mental health assistant, provide a supportive response to:
                    {user_input}"""
                }],
                model="mixtral-8x7b-32768",  # Groq's fastest model
                temperature=0.7,
                max_tokens=1024
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return "I'm having trouble responding right now."