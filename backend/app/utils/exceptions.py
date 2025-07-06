from fastapi import HTTPException, status

class RuhaniException(HTTPException):
    """Base exception class for RUHANI platform"""
    
class InvalidCredentialsException(RuhaniException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class InactiveUserException(RuhaniException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

class UnauthorizedAccessException(RuhaniException):
    def __init__(self, role_required: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{role_required} access required"
        )

class NotFoundException(RuhaniException):
    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )