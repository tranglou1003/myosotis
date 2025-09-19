from typing import Any, List

from fastapi import APIRouter, Depends
from app.schemas.sche_response import DataResponse
from app.services.srv_user import UserService
from app.utils.exception_handler import CustomException, ExceptionType
from app.schemas.sche_user import UserResponse, UserCreateRequest, UserUpdateRequest

router = APIRouter(prefix=f"/users")


@router.get("/", response_model=DataResponse[List[UserResponse]])
def get_users(user_service: UserService = Depends()):
    try:
        users = user_service.get_all_users()
        return DataResponse(http_code=200, data=users)
    except Exception as e:
        raise CustomException(exception=e)


@router.get("/{user_id}", response_model=DataResponse[UserResponse])
def get_user(user_id: int, user_service: UserService = Depends()):
    try:
        user = user_service.get_user_by_id(user_id)
        return DataResponse(http_code=200, data=user)
    except Exception as e:
        raise CustomException(exception=e)


@router.post("/", response_model=DataResponse[UserResponse])
def create_user(data: UserCreateRequest, user_service: UserService = Depends()) -> Any:
    try:
        user = user_service.create_user(data)
        return DataResponse(http_code=201, data=user)
    except Exception as e:
        raise CustomException(exception=e)


@router.put("/{user_id}", response_model=DataResponse[UserResponse])
def update_user(user_id: int, data: UserUpdateRequest, user_service: UserService = Depends()) -> Any:
    try:
        user = user_service.update_user(user_id, data)
        return DataResponse(http_code=200, data=user)
    except Exception as e:
        raise CustomException(exception=e)


@router.delete("/{user_id}", response_model=DataResponse[dict])
def delete_user(user_id: int, user_service: UserService = Depends()):
    try:
        user_service.delete_user(user_id)
        return DataResponse(http_code=200, data={"message": "User deleted successfully"})
    except Exception as e:
        raise CustomException(exception=e)
