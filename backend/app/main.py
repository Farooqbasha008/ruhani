from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import employee, hr

app = FastAPI(title="RUHANI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee.router, prefix="/employee", tags=["Employee"])
app.include_router(hr.router, prefix="/hr", tags=["HR"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RUHANI backend is running"} 