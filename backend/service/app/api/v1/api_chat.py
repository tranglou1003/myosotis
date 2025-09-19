# app/api/v1/api_chat_improved.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import json

from app.schemas.sche_chat import (
    ChatRequest, ChatResponse, ChatStreamRequest, ChatStreamChunk,
    SessionSummary, SessionListItem, ChatHistory, ChatMessageItem, ChatHistoryListItem
    , ChatRawRequest, ChatRawResponse
)
from app.services.srv_chat import ChatbotService
from app.models.model_user import User
from app.models.model_chat import ChatSession, ChatMessage
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat")


def get_chatbot_service(db: Session = Depends(get_db)) -> ChatbotService:
    """Dependency to create ChatbotService instance"""
    return ChatbotService(db_session=db)


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
) -> ChatResponse:
    """
    Send a message to the chatbot and get a response
    
    - **user_id**: ID of the user from database
    - **message**: The message content (1-1000 characters)
    - **session_number**: Session number (optional, will use latest if not provided)
    """
    try:
        # Validate user exists
        user = chatbot_service.db_session.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )

        # Process chat using improved service
        async with chatbot_service:
            session, bot_response = await chatbot_service.process_chat(
                user_id=request.user_id,
                message=request.message,
                session_number=request.session_number if request.session_number > 0 else None
            )

        return ChatResponse(
            session_id=str(session.id),
            response=bot_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing chat message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )


@router.post("/stream")
async def send_message_stream(
    request: ChatStreamRequest,
    chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Send a message to the chatbot and get a streaming response
    
    - **user_id**: ID of the user from database
    - **message**: The message content (1-1000 characters)
    - **session_number**: Session number (0 for latest, specific number for existing session)
    
    Returns a streaming response with Server-Sent Events (SSE) format
    """
    try:
        # Validate user exists
        user = chatbot_service.db_session.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )

        async def generate_stream():
            session_id = None
            try:
                async with chatbot_service:
                    async for session, content_chunk in chatbot_service.process_chat_stream(
                        user_id=request.user_id,
                        message=request.message,
                        session_number=request.session_number if request.session_number > 0 else None
                    ):
                        session_id = str(session.id)
                        
                        # Create streaming chunk
                        chunk = ChatStreamChunk(
                            session_id=session_id,
                            content=content_chunk,
                            is_complete=False
                        )
                        
                        # Format as SSE
                        yield f"data: {chunk.json()}\n\n"
                
                # Send completion marker
                if session_id:
                    final_chunk = ChatStreamChunk(
                        session_id=session_id,
                        content="",
                        is_complete=True
                    )
                    yield f"data: {final_chunk.json()}\n\n"
                
            except Exception as e:
                logger.exception("Error in streaming response")
                error_chunk = ChatStreamChunk(
                    session_id=session_id or "unknown",
                    content=f"Error: {str(e)}",
                    is_complete=True
                )
                yield f"data: {error_chunk.json()}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error setting up streaming chat")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while setting up streaming chat"
        )


@router.get("/sessions", response_model=List[SessionListItem])
def list_user_sessions(
    user_id: int = None,
    db: Session = Depends(get_db)
) -> List[SessionListItem]:
    """
    List chat sessions
    
    - **user_id**: Optional filter by user ID
    """
    try:
        query = db.query(ChatSession).join(User)
        
        if user_id:
            query = query.filter(ChatSession.user_id == user_id)
        
        sessions = query.order_by(ChatSession.last_active_at.desc()).all()
        
        result = []
        for session in sessions:
            user_name = (
                session.user.profile.full_name 
                if session.user.profile and session.user.profile.full_name
                else session.user.email.split('@')[0] if session.user.email
                else f"User {session.user_id}"
            )
            
            result.append(SessionListItem(
                session_id=str(session.id),
                user_name=user_name,
                created_at=session.created_at.isoformat() if session.created_at else None,
                total_messages=session.total_messages or 0,
                last_active=session.last_active_at.isoformat() if session.last_active_at else None
            ))
        
        return result
        
    except Exception as e:
        logger.exception("Error listing sessions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sessions"
        )


@router.get("/session/{session_id}", response_model=SessionSummary)
def get_session_details(
    session_id: int,
    include_messages: bool = False,
    db: Session = Depends(get_db)
) -> SessionSummary:
    """
    Get detailed information about a specific chat session
    
    - **session_id**: The ID of the session
    - **include_messages**: Whether to include message history in response
    """
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        user_name = (
            session.user.profile.full_name 
            if session.user.profile and session.user.profile.full_name
            else session.user.email.split('@')[0] if session.user.email
            else f"User {session.user_id}"
        )

        history_length = len(session.messages) if session.messages else 0

        return SessionSummary(
            user_name=user_name,
            created_at=session.created_at.isoformat() if session.created_at else None,
            total_messages=session.total_messages or 0,
            last_active=session.last_active_at.isoformat() if session.last_active_at else None,
            history_length=history_length
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting session details")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session information"
        )


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages
    
    - **session_id**: The ID of the session to delete
    """
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found"
            )

        db.delete(session)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting session")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting session"
        )


@router.get("/stats")
def get_chat_statistics(db: Session = Depends(get_db)):
    """
    Get overall chat statistics
    """
    try:
        from sqlalchemy import func
        
        stats = db.query(
            func.count(ChatSession.id).label('total_sessions'),
            func.count(ChatMessage.id).label('total_messages'),
            func.count(func.distinct(ChatSession.user_id)).label('active_users')
        ).outerjoin(ChatMessage).first()
        
        return {
            "total_sessions": stats.total_sessions or 0,
            "total_messages": stats.total_messages or 0,
            "active_users": stats.active_users or 0
        }
        
    except Exception as e:
        logger.exception("Error getting statistics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get("/history/{user_id}", response_model=List[ChatHistoryListItem])
def get_user_chat_history_list(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> List[ChatHistoryListItem]:
    """
    Get list of chat sessions for a user (summary view)
    
    - **user_id**: ID of the user
    - **limit**: Maximum number of sessions to return (default 20)
    - **offset**: Number of sessions to skip (default 0)
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get sessions with pagination
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.last_active_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for session in sessions:
            # Get last message preview
            last_message = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at.desc())
                .first()
            )
            
            last_message_preview = None
            if last_message:
                # Take first 100 characters of user message as preview
                last_message_preview = last_message.user_message[:100]
                if len(last_message.user_message) > 100:
                    last_message_preview += "..."

            result.append(ChatHistoryListItem(
                session_id=str(session.id),
                session_number=session.session_number,
                session_name=session.session_name,
                total_messages=session.total_messages or 0,
                last_message_preview=last_message_preview,
                created_at=session.created_at.isoformat() if session.created_at else None,
                last_active=session.last_active_at.isoformat() if session.last_active_at else None
            ))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting chat history for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving chat history"
        )


@router.get("/history/{user_id}/{session_id}", response_model=ChatHistory)
def get_chat_session_history(
    user_id: int,
    session_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> ChatHistory:
    """
    Get detailed chat history for a specific session
    
    - **user_id**: ID of the user
    - **session_id**: ID of the chat session
    - **limit**: Maximum number of messages to return (default 50)
    - **offset**: Number of messages to skip (default 0)
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get session
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            .first()
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found for user {user_id}"
            )

        # Get messages with pagination
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # Convert to schema format
        message_list = []
        for msg in messages:
            message_list.append(ChatMessageItem(
                id=msg.id,
                user_message=msg.user_message,
                bot_response=msg.bot_response,
                created_at=msg.created_at.isoformat() if msg.created_at else None
            ))

        return ChatHistory(
            session_id=str(session.id),
            user_id=session.user_id,
            session_number=session.session_number,
            session_name=session.session_name,
            total_messages=session.total_messages or 0,
            messages=message_list,
            created_at=session.created_at.isoformat() if session.created_at else None,
            last_active=session.last_active_at.isoformat() if session.last_active_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting session history {session_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session history"
        )


@router.get("/latest-session/{user_id}", response_model=ChatHistory)
def get_latest_chat_session(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> ChatHistory:
    """
    Get the latest chat session for a user with recent messages
    
    - **user_id**: ID of the user
    - **limit**: Maximum number of recent messages to return (default 20)
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get latest session
        session = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.last_active_at.desc())
            .first()
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No chat sessions found for user {user_id}"
            )

        # Get recent messages
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        
        # Reverse to chronological order
        messages = list(reversed(messages))

        # Convert to schema format
        message_list = []
        for msg in messages:
            message_list.append(ChatMessageItem(
                id=msg.id,
                user_message=msg.user_message,
                bot_response=msg.bot_response,
                created_at=msg.created_at.isoformat() if msg.created_at else None
            ))

        return ChatHistory(
            session_id=str(session.id),
            user_id=session.user_id,
            session_number=session.session_number,
            session_name=session.session_name,
            total_messages=session.total_messages or 0,
            messages=message_list,
            created_at=session.created_at.isoformat() if session.created_at else None,
            last_active=session.last_active_at.isoformat() if session.last_active_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting latest session for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving latest session"
        )

# THis api is only for dev, not use in production


@router.post("/raw", response_model=ChatRawResponse)
async def chat_raw(
    request: ChatRawRequest,
    db: Session = Depends(get_db)
):
    """
    Chat API không có system prompt, chỉ forward message người dùng
    """
    async with ChatbotService(db) as service:
        try:
            bot_response = await service.generate_raw_chat(request.message)
            return ChatRawResponse(response=bot_response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))