from fastapi import APIRouter
from app.api.v1.endpoints import auth, employee, hr, health

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(employee.router, prefix="/employee", tags=["Employee"])
router.include_router(hr.router, prefix="/hr", tags=["HR"])
router.include_router(health.router, prefix="/health", tags=["Health"])