from typing import Any, List

from fastapi import APIRouter, Depends
from app.schemas.sche_response import DataResponse
from app.services.srv_emergency_contacts import EmergencyContactService
from app.utils.exception_handler import CustomException, ExceptionType
from app.schemas.sche_user import EmergencyContactResponse, EmergencyContactBase

router = APIRouter(prefix=f"/emergency-contacts")


@router.get("/user/{user_id}", response_model=DataResponse[List[EmergencyContactResponse]])
def get_user_emergency_contacts(user_id: int, emergency_service: EmergencyContactService = Depends()):
    try:
        contacts = emergency_service.get_user_emergency_contacts(user_id)
        return DataResponse(http_code=200, data=contacts)
    except Exception as e:
        raise CustomException(exception=e)


@router.get("/{contact_id}", response_model=DataResponse[EmergencyContactResponse])
def get_emergency_contact(contact_id: int, emergency_service: EmergencyContactService = Depends()):
    try:
        contact = emergency_service.get_emergency_contact_by_id(contact_id)
        return DataResponse(http_code=200, data=contact)
    except Exception as e:
        raise CustomException(exception=e)


@router.post("/user/{user_id}", response_model=DataResponse[EmergencyContactResponse])
def create_emergency_contact(
    user_id: int, 
    data: EmergencyContactBase, 
    emergency_service: EmergencyContactService = Depends()
) -> Any:
    try:
        contact = emergency_service.create_emergency_contact(user_id, data)
        return DataResponse(http_code=201, data=contact)
    except Exception as e:
        raise CustomException(exception=e)


@router.put("/{contact_id}", response_model=DataResponse[EmergencyContactResponse])
def update_emergency_contact(
    contact_id: int, 
    data: EmergencyContactBase, 
    emergency_service: EmergencyContactService = Depends()
) -> Any:
    try:
        contact = emergency_service.update_emergency_contact(contact_id, data)
        return DataResponse(http_code=200, data=contact)
    except Exception as e:
        raise CustomException(exception=e)


@router.delete("/{contact_id}", response_model=DataResponse[dict])
def delete_emergency_contact(contact_id: int, emergency_service: EmergencyContactService = Depends()):
    try:
        emergency_service.delete_emergency_contact(contact_id)
        return DataResponse(http_code=200, data={"message": "Emergency contact deleted successfully"})
    except Exception as e:
        raise CustomException(exception=e)
