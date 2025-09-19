import uuid
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
import httpx
from sqlalchemy.orm import Session
from app.models.model_chat import ChatSession, ChatMessage
from app.models.model_user import User, UserProfile
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Improved Chatbot Service without Singleton pattern
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.api_url = settings.LLM_API_URL
        self.model_name = settings.LLM_MODEL_NAME
        
        # Fixed headers based on Sea Lion API documentation
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Content-Type": "application/json",
                "accept": "text/plain",  # Changed from application/json
                "Authorization": f"Bearer {settings.SEA_LION_API_KEY}"
            }
        )
        
        self.system_prompt = self._load_system_prompt()
        logger.info(f"ChatbotService initialized with model: {self.model_name}")
        logger.info(f"SEA_LION_API_KEY : {settings.SEA_LION_API_KEY}")

    def _load_system_prompt(self) -> str:
        """Load system prompt from config or file"""
        return (
            "You are an AI specialist dedicated to supporting Alzheimer's patients and their families. "
            "Always use simple, clear, and easy-to-understand language. "
            "Be patient, practical, safe, and positive in all responses. "
            "Keep answers concise but helpful. "
            "Always respond with a caring, understanding, and supportive attitude. "
            "Prioritize user safety and comfort in all situations. "
            "Gently remind about treatment compliance and healthcare when necessary. "
            "Remember previous conversations to maintain continuity and context. "
            "ALWAYS reply in English, NOTHING ELSE"
        )

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def get_user_context(self, user_id: int) -> Dict:
        """Get user information for context building"""
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if not user or not user.profile:
            return {"user_name": "User", "age": None, "gender": None}

        profile = user.profile
        age = self._calculate_age(profile.date_of_birth) if profile.date_of_birth else None

        return {
            "user_name": profile.full_name or f"User {user_id}",
            "age": age,
            "gender": profile.gender.value if profile.gender else None
        }

    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date"""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def get_or_create_session(self, user_id: int, session_number: Optional[int] = None) -> ChatSession:
        """
        Simplified session management
        If session_number is None, get or create latest session
        """
        if session_number is None:
            # Get latest session or create new one
            session = (
                self.db_session.query(ChatSession)
                .filter(ChatSession.user_id == user_id)
                .order_by(ChatSession.session_number.desc())
                .first()
            )
            
            if session:
                session.last_active_at = datetime.utcnow()
                self.db_session.commit()
                return session
        else:
            # Try to get specific session
            session = (
                self.db_session.query(ChatSession)
                .filter(
                    ChatSession.user_id == user_id,
                    ChatSession.session_number == session_number
                )
                .first()
            )
            
            if session:
                session.last_active_at = datetime.utcnow()
                self.db_session.commit()
                return session

        # Create new session
        return self._create_new_session(user_id)

    def _create_new_session(self, user_id: int) -> ChatSession:
        """Create a new chat session"""
        from sqlalchemy import func
        
        last_number = (
            self.db_session.query(func.max(ChatSession.session_number))
            .filter(ChatSession.user_id == user_id)
            .scalar() or 0
        )

        new_session = ChatSession(
            user_id=user_id,
            session_number=last_number + 1,
            session_name=f"Chat Session {last_number + 1}",
            created_at=datetime.utcnow(),
            last_active_at=datetime.utcnow(),
            total_messages=0
        )
        
        self.db_session.add(new_session)
        self.db_session.commit()
        self.db_session.refresh(new_session)
        return new_session

    def build_conversation_context(self, session_id: int, user_id: int, current_message: str) -> List[Dict]:
        """Build conversation context for LLM - fixed role alternation"""
        # Build a single comprehensive system prompt
        system_content = self.system_prompt
        
        # Add user context to the system prompt instead of separate message
        user_context = self.get_user_context(user_id)
        context_parts = []
        
        if user_context.get("user_name"):
            context_parts.append(f"named {user_context['user_name']}")
        if user_context.get("age"):
            context_parts.append(f"{user_context['age']} years old")
        if user_context.get("gender"):
            gender_text = "male" if user_context["gender"] == "male" else "female"
            context_parts.append(gender_text)

        if context_parts:
            system_content += f"\n\nThe user is {', '.join(context_parts)}. Please adjust your communication style appropriately."

        # Start with single system message
        messages = [{"role": "system", "content": system_content}]

        # Add recent conversation history ensuring alternating pattern
        recent_messages = (
            self.db_session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(4)  # Last 4 messages (2 exchanges)
            .all()
        )

        # Add history in correct order (oldest first)
        for msg in reversed(recent_messages):
            messages.append({"role": "user", "content": msg.user_message})
            messages.append({"role": "assistant", "content": msg.bot_response})

        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        # Log the message structure for debugging
        logger.info(f"Built conversation context with {len(messages)} messages:")
        for i, msg in enumerate(messages):
            logger.info(f"  {i}: {msg['role']} - {msg['content'][:50]}...")
        
        return messages

    def _validate_message_pattern(self, messages: List[Dict]) -> None:
        """
        Validate that messages follow the required alternating pattern:
        system -> user -> assistant -> user -> assistant -> ... -> user
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        # First message should be system
        if messages[0]["role"] != "system":
            raise ValueError("First message must be system role")
        
        # Check alternating pattern for the rest
        expected_roles = ["user", "assistant"] * (len(messages) // 2 + 1)
        
        for i, message in enumerate(messages[1:], 1):  # Skip first system message
            expected_role = expected_roles[(i-1) % 2]  # 0 -> user, 1 -> assistant
            actual_role = message["role"]
            
            if actual_role != expected_role:
                logger.error(f"Invalid role pattern at position {i}: expected '{expected_role}', got '{actual_role}'")
                logger.error(f"Full message sequence: {[msg['role'] for msg in messages]}")
                raise ValueError(f"Invalid conversation pattern: messages must alternate user/assistant after system message")
        
        # Last message should be user (since we're about to get assistant response)
        if len(messages) > 1 and messages[-1]["role"] != "user":
            raise ValueError("Last message must be user role when requesting assistant response")

    async def generate_response(self, messages: List[Dict]) -> str:
        """Generate response from LLM"""
        try:
            # Validate message pattern before sending
            self._validate_message_pattern(messages)
            
            # Exact payload format matching the working curl example
            payload = {
                "model": self.model_name,
                "messages": messages,
                "chat_template_kwargs": {
                    "thinking_mode": "off"
                }
            }
            
            logger.info(f"Payload for LLM: {payload}")
            logger.info(f"Number of messages in context: {len(messages)}")
            print(f"Payload: {payload}")
            
            response = await self.client.post(self.api_url, json=payload)
            
            # Log the response status and headers for debugging
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            
            if response.status_code != 200:
                response_text = await response.aread() if hasattr(response, 'aread') else response.text
                logger.error(f"HTTP {response.status_code} response body: {response_text}")
            
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            
            logger.warning("No choices in LLM response")
            logger.warning(f"Full response data: {data}")
            return "I apologize, but I'm having trouble generating a response right now."
            
        except httpx.TimeoutException:
            logger.error("Sea Lion API timeout")
            return "I'm taking a bit longer to respond. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"Sea Lion API HTTP error: {e}")
            # Enhanced error logging
            try:
                error_body = e.response.text if hasattr(e.response, 'text') else str(e.response.content)
                logger.error(f"Error response body: {error_body}")
            except Exception as log_error:
                logger.error(f"Could not log error response body: {log_error}")
            return "I'm experiencing some technical difficulties. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error calling Sea Lion API: {e}")
            return "I'm sorry, but I encountered an unexpected error. Please try again."

    async def generate_response_stream(self, messages: List[Dict]):
        """Generate streaming response from LLM"""
        try:
            # Validate message pattern before sending
            self._validate_message_pattern(messages)
            
            # Simplified payload for streaming, removing unsupported parameters
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": True,
                "chat_template_kwargs": {
                    "thinking_mode": "off"
                }
            }
            
            logger.info(f"Payload for LLM streaming: {payload}")
            print(payload)
            
            async with self.client.stream('POST', self.api_url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        line_str = line.strip()
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # Remove 'data: ' prefix
                            
                            # Check for completion marker
                            if data_str.strip() == '[DONE]':
                                break
                            
                            try:
                                import json
                                chunk_data = json.loads(data_str)
                                
                                # Parse OpenAI-compatible streaming format
                                if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                    choice = chunk_data["choices"][0]
                                    
                                    # Check for delta content (streaming format)
                                    if "delta" in choice and "content" in choice["delta"]:
                                        content = choice["delta"]["content"]
                                        if content:
                                            yield content
                                    
                                    # Check if this is the final chunk
                                    if choice.get("finish_reason") is not None:
                                        break
                                        
                            except json.JSONDecodeError:
                                # Skip malformed JSON lines
                                continue
                            
        except httpx.TimeoutException:
            logger.error("Sea Lion API timeout during streaming")
            yield "I'm taking a bit longer to respond. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"Sea Lion API HTTP error during streaming: {e}")
            # Log response body for debugging
            if hasattr(e.response, 'text'):
                logger.error(f"Streaming response body: {e.response.text}")
            yield "I'm experiencing some technical difficulties. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error during streaming with Sea Lion API: {e}")
            yield "I'm sorry, but I encountered an unexpected error. Please try again."

    def save_message(self, session_id: int, user_message: str, bot_response: str) -> ChatMessage:
        """Save chat message to database"""
        message = ChatMessage(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            created_at=datetime.utcnow()
        )
        
        # Update session stats
        session = self.db_session.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.total_messages = (session.total_messages or 0) + 1
            session.last_active_at = datetime.utcnow()
        
        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)
        
        return message

    async def process_chat(self, user_id: int, message: str, session_number: Optional[int] = None) -> tuple[ChatSession, str]:
        """
        Main chat processing method
        Returns (session, bot_response)
        """
        # Get or create session
        session = self.get_or_create_session(user_id, session_number)
        
        # Build context and generate response
        context = self.build_conversation_context(session.id, user_id, message)
        bot_response = await self.generate_response(context)
        
        # Save to database
        self.save_message(session.id, message, bot_response)
        
        return session, bot_response

    async def process_chat_stream(self, user_id: int, message: str, session_number: Optional[int] = None):
        """
        Main streaming chat processing method
        Yields (session, content_chunk) tuples
        """
        logger.info(f"Starting streaming chat for user {user_id}, message: '{message[:50]}...'")
        
        # Get or create session
        session = self.get_or_create_session(user_id, session_number)
        logger.info(f"Using session {session.id} for streaming chat")
        
        # Build context
        context = self.build_conversation_context(session.id, user_id, message)
        logger.info(f"Built context with {len(context)} messages")
        
        # Collect full response for database storage
        full_response = ""
        chunk_count = 0
        
        try:
            # Generate streaming response
            async for content_chunk in self.generate_response_stream(context):
                chunk_count += 1
                full_response += content_chunk
                logger.debug(f"Yielding chunk {chunk_count}: '{content_chunk[:30]}...'")
                yield session, content_chunk
            
            logger.info(f"Streaming completed. Total chunks: {chunk_count}, response length: {len(full_response)}")
            
            # Save complete message to database after streaming is done
            if full_response.strip():
                self.save_message(session.id, message, full_response.strip())
                logger.info(f"Saved streaming message to database")
            else:
                # Fallback if no content was generated
                fallback_response = "I apologize, but I couldn't generate a proper response."
                self.save_message(session.id, message, fallback_response)
                logger.warning("No content generated, saved fallback response")
                
        except Exception as e:
            logger.error(f"Error in streaming chat processing: {e}")
            # Yield error message
            error_message = "I encountered an error while processing your message."
            yield session, error_message
            # Save error to database
            self.save_message(session.id, message, error_message)

        
    # This code is only for dev, not used in production
    async def generate_raw_chat(self, user_prompt: str) -> str:
        """
        Generate response from LLM without any system prompt or history.
        Only use the raw user prompt.
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "chat_template_kwargs": {
                    "thinking_mode": "off"
                }
            }
            logger.info(f"Payload (raw chat): {payload}")
            
            response = await self.client.post(self.api_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            
            logger.warning("No choices in raw LLM response")
            return "I couldn't generate a response."
            
        except httpx.TimeoutException:
            logger.error("LLM API timeout (raw chat)")
            return "Request timed out, please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API HTTP error (raw chat): {e}")
            # Log response body for debugging
            if hasattr(e.response, 'text'):
                logger.error(f"Raw chat response body: {e.response.text}")
            return "HTTP error, please try again."
        except Exception as e:
            logger.error(f"Unexpected error in raw chat: {e}")
            return "Unexpected error occurred."

    async def test_simple_request(self) -> str:
        """
        Test with the exact same payload as the working curl example
        Use this for debugging API connectivity
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, can you respond briefly?"
                    }
                ],
                "chat_template_kwargs": {
                    "thinking_mode": "off"
                }
            }
            
            logger.info(f"Testing simple request with payload: {payload}")
            
            response = await self.client.post(self.api_url, json=payload)
            
            logger.info(f"Test response status: {response.status_code}")
            logger.info(f"Test response headers: {response.headers}")
            
            if response.status_code != 200:
                response_text = await response.aread() if hasattr(response, 'aread') else response.text
                logger.error(f"Test HTTP {response.status_code} response: {response_text}")
                return f"Test failed with status {response.status_code}: {response_text}"
            
            data = response.json()
            logger.info(f"Test response data: {data}")
            
            if "choices" in data and len(data["choices"]) > 0:
                result = data["choices"][0]["message"]["content"].strip()
                logger.info(f"Test successful! Response: {result}")
                return result
            
            return "Test failed: No choices in response"
            
        except Exception as e:
            logger.error(f"Test request failed: {e}")
            return f"Test failed with error: {e}"

    async def check_available_models(self) -> List[str]:
        """
        Check available models from Sea Lion API
        Useful for debugging model name issues
        """
        try:
            response = await self.client.get("https://api.sea-lion.ai/v1/models")
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("id", "unknown") for model in data.get("data", [])]
            logger.info(f"Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"Error fetching available models: {e}")
            return []