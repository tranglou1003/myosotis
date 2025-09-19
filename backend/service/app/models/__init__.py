# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.model_base import Base  # noqa
from app.models.model_user import User  # noqa
from app.models.model_assessment import AssessmentType, AssessmentQuestion, UserAssessment, AssessmentAnswer  # noqa
from app.models.model_ai_clone import AICloneVideo  # noqa
