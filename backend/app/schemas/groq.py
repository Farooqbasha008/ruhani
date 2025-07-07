from pydantic import BaseModel

class GroqRequest(BaseModel):
    user_input: str

class GroqResponse(BaseModel):
    response: str