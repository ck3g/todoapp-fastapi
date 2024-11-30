from fastapi import APIRouter, status
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterResponse(BaseModel):
    email: str
    username: str


class RegisterRequest(BaseModel):
    """Create user request form"""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=3, max_length=255)
    password_confirmation: str = Field(min_length=3, max_length=255)

    @model_validator(mode="after")
    def validate_password_and_confirmation(self):
        """Validates whether password matches password_confirmation"""
        p = self.password
        pc = self.password_confirmation
        if p is not None and pc is not None and p != pc:
            raise PydanticCustomError(
                "confirmation_error", "Password and Password Confirmation do not match"
            )

        return self


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest):
    """Creates and new user with provided credentials"""
    username = request.email.split("@")[0]
    response = RegisterResponse(email=request.email, username=username)
    return {"msg": "User successfully created", "user": response}
