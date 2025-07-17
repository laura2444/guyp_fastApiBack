from fastapi import APIRouter
from app.services.user_service import register_user, login_user
from app.schemas.user_schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema



auth_router = APIRouter()

@auth_router.post("/signup", response_model=UserResponseSchema)
async def signup(data: UserRegisterSchema):
    return await register_user(data)

@auth_router.post("/signin", response_model=UserResponseSchema)
async def signin(data: UserLoginSchema):
    return await login_user(data)