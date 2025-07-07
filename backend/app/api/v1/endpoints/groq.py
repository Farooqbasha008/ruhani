from fastapi import APIRouter, Depends
from app.services.groq_service import GroqService
from app.schemas.groq import GroqRequest, GroqResponse

router = APIRouter()

@router.post("/mental-health-support", response_model=GroqResponse)
async def get_mental_health_support(
    request: GroqRequest,
    groq_service: GroqService = Depends()
):
    response = await groq_service.generate_mental_health_response(request.user_input)
    return {"response": response}