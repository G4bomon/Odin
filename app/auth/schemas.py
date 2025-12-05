from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema para login con JSON en lugar de FormData"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "yourpassword"
            }
        }
