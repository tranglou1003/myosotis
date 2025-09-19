from fastapi_sqlalchemy import db
from app.models.model_user import EmergencyContact, User
from app.schemas.sche_user import EmergencyContactResponse, EmergencyContactBase
from app.utils.exception_handler import CustomException, ExceptionType


class EmergencyContactService(object):
    __instance = None

    @staticmethod
    def get_user_emergency_contacts(user_id: int) -> list[EmergencyContactResponse]:
        # Check if user exists
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        contacts = db.session.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).all()
        
        result = []
        for contact in contacts:
            contact_response = EmergencyContactResponse(
                id=contact.id,
                user_id=contact.user_id,
                contact_name=contact.contact_name,
                relation=contact.relation,  # Fixed: use 'relation' instead of 'relationship'
                phone=contact.phone,
                email=contact.email,
                address=contact.address,
                is_primary=contact.is_primary,
                created_at=str(contact.created_at)
            )
            result.append(contact_response)
        
        return result

    @staticmethod
    def get_emergency_contact_by_id(contact_id: int) -> EmergencyContactResponse:
        contact = db.session.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        
        if not contact:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        return EmergencyContactResponse(
            id=contact.id,
            user_id=contact.user_id,
            contact_name=contact.contact_name,
            relation=contact.relation,  # Fixed: use 'relation' instead of 'relationship'
            phone=contact.phone,
            email=contact.email,
            address=contact.address,
            is_primary=contact.is_primary,
            created_at=str(contact.created_at)
        )

    @staticmethod
    def create_emergency_contact(user_id: int, data: EmergencyContactBase) -> EmergencyContactResponse:
        # Check if user exists
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        # If this is a primary contact, unset other primary contacts for this user
        if data.is_primary:
            db.session.query(EmergencyContact).filter(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary == True
            ).update({"is_primary": False})
        
        new_contact = EmergencyContact(
            user_id=user_id,
            contact_name=data.contact_name,
            relation=data.relation,  # Fixed: use 'relation' instead of 'relationship'
            phone=data.phone,
            email=data.email,
            address=data.address,
            is_primary=data.is_primary
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        return EmergencyContactResponse(
            id=new_contact.id,
            user_id=new_contact.user_id,
            contact_name=new_contact.contact_name,
            relation=new_contact.relation,  # Fixed: use 'relation' instead of 'relationship'
            phone=new_contact.phone,
            email=new_contact.email,
            address=new_contact.address,
            is_primary=new_contact.is_primary,
            created_at=str(new_contact.created_at)
        )

    @staticmethod
    def update_emergency_contact(contact_id: int, data: EmergencyContactBase) -> EmergencyContactResponse:
        contact = db.session.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        
        if not contact:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        # If this is being set as primary, unset other primary contacts for this user
        if data.is_primary:
            db.session.query(EmergencyContact).filter(
                EmergencyContact.user_id == contact.user_id,
                EmergencyContact.is_primary == True,
                EmergencyContact.id != contact_id
            ).update({"is_primary": False})
        
        # Update contact fields
        contact.contact_name = data.contact_name
        contact.relation = data.relation  # Fixed: use 'relation' instead of 'relationship'
        contact.phone = data.phone
        contact.email = data.email
        contact.address = data.address
        contact.is_primary = data.is_primary
        
        db.session.commit()
        
        return EmergencyContactResponse(
            id=contact.id,
            user_id=contact.user_id,
            contact_name=contact.contact_name,
            relation=contact.relation,  # Fixed: use 'relation' instead of 'relationship'
            phone=contact.phone,
            email=contact.email,
            address=contact.address,
            is_primary=contact.is_primary,
            created_at=str(contact.created_at)
        )

    @staticmethod
    def delete_emergency_contact(contact_id: int):
        contact = db.session.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
        
        if not contact:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        db.session.delete(contact)
        db.session.commit()