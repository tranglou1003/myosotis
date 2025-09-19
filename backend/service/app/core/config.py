import os
from typing import Optional
from pydantic_settings import BaseSettings
from keycloak.keycloak_openid import KeycloakOpenID


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
print(f"BASE_DIR: {BASE_DIR}")

class Settings(BaseSettings):
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "FASTAPI_BASE")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", None)
    API_PREFIX: str = os.environ.get("API_PREFIX", "/api")
    API_VERSIONS: str = os.environ.get("API_VERSIONS", "")
    API_VERSION: str = os.environ.get("API_VERSION", "v1")
    BACKEND_CORS_ORIGINS: str = os.environ.get("BACKEND_CORS_ORIGINS", '["*"]')
    DATABASE_URL: str = (
        f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"
    )
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7 
    SECURITY_ALGORITHM: str = "HS256"
    LOGGING_CONFIG_FILE: str = os.path.join(BASE_DIR, "logging.ini")
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"
    KEYCLOAK_SERVER_URL: Optional[str] = os.environ.get("KEYCLOAK_SERVER_URL", None)
    KEYCLOAK_REALM: Optional[str] = os.environ.get("KEYCLOAK_REALM", None)
    KEYCLOAK_CLIENT_ID: Optional[str] = os.environ.get("KEYCLOAK_CLIENT_ID", None)
    KEYCLOAK_CLIENT_SECRET: Optional[str] = os.environ.get("KEYCLOAK_CLIENT_SECRET", None)
    KEYCLOAK_VERIFY: Optional[bool] = os.environ.get("KEYCLOAK_VERIFY", "False").lower() == "true"
    GOOGLE_CLIENT_ID: Optional[str] = os.environ.get("GOOGLE_CLIENT_ID", None)
    SEA_LION_API_KEY: Optional[str] = os.environ.get("SEA_LION_API_KEY", "")
    
    # AI Clone Services Configuration
    HUMAN_CLONE_SERVICE_URL: str = os.environ.get("HUMAN_CLONE_SERVICE_URL", "http://192.168.30.206:8779")
    LLM_SERVICE_URL: str = os.environ.get("LLM_SERVICE_URL", "http://192.168.30.206:8080")
    AI_REQUEST_TIMEOUT: int = int(os.environ.get("AI_REQUEST_TIMEOUT", "500"))
    MAX_CONCURRENT_AI_REQUESTS: int = int(os.environ.get("MAX_CONCURRENT_AI_REQUESTS", "3"))
    ENABLE_AI_CACHE: bool = os.environ.get("ENABLE_AI_CACHE", "true").lower() == "true"
    
    # Chatbot Configuration
    LLM_API_URL: str = os.environ.get("LLM_API_URL", "https://api.sea-lion.ai/v1/chat/completions")
    LLM_API_PYTHON_URL: str = os.environ.get("LLM_API_PYTHON_URL", "https://api.sea-lion.ai/v1")
    LLM_MODEL_NAME: str = os.environ.get("LLM_MODEL_NAME", "aisingapore/Gemma-SEA-LION-v4-27B-IT")
    CHATBOT_TIMEOUT: int = int(os.environ.get("CHATBOT_TIMEOUT", "60"))
    CHATBOT_MAX_HISTORY: int = int(os.environ.get("CHATBOT_MAX_HISTORY", "5"))
    CHATBOT_TEMPERATURE: float = float(os.environ.get("CHATBOT_TEMPERATURE", "0.7"))
    CHATBOT_TOP_P: float = float(os.environ.get("CHATBOT_TOP_P", "0.9"))

settings = Settings()

if (
    settings.KEYCLOAK_SERVER_URL != None
    and settings.KEYCLOAK_REALM != None
    and settings.KEYCLOAK_CLIENT_ID != None
    and settings.KEYCLOAK_CLIENT_SECRET != None
    and settings.KEYCLOAK_VERIFY != None
):
    keycloak_openid = KeycloakOpenID(
        server_url=settings.KEYCLOAK_SERVER_URL,
        realm_name=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT_ID,
        client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        verify=settings.KEYCLOAK_VERIFY,
    )
else:
    keycloak_openid = None


def get_openid_config():
    if keycloak_openid == None:
        return {}
    return keycloak_openid.well_known()
