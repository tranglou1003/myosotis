from typing import Any

from app.services.srv_user import UserService
from fastapi import APIRouter, Depends
from app.schemas.sche_response import DataResponse
from app.services.srv_auth import AuthService
from app.utils.exception_handler import CustomException, ExceptionType
from app.schemas.sche_auth import LoginRequest, RegisterRequest, LoginResponse
from app.schemas.sche_user import UserCreateRequest, UserResponse

router = APIRouter(prefix=f"/auth")


@router.post("/login", response_model=DataResponse[LoginResponse])
def login(form_data: LoginRequest, auth_service: AuthService = Depends()):
    try:
        login_response = auth_service.login(data=form_data)
        return DataResponse(http_code=200, data=login_response)
    except Exception as e:
        print(e, flush=True)
        raise CustomException(exception=e)


@router.post("/register", response_model=DataResponse[UserResponse])
def register(data: UserCreateRequest, user_service: UserService = Depends()) -> Any:
    try:
        user = user_service.create_user(data)
        return DataResponse(http_code=201, data=user)
    except Exception as e:
        raise CustomException(exception=e)
