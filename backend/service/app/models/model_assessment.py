from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.model_base import BareBaseModel
import enum
from datetime import datetime


class QuestionTypeEnum(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    NUMERICAL = "numerical"
    DRAWING = "drawing"
    MEMORY_RECALL = "memory_recall"


class AssessmentStatusEnum(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AssessmentType(BareBaseModel):
    __tablename__ = "assessment_types"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    difficulty_level = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    passing_score = Column(Integer)
    is_active = Column(Boolean, default=True)


class AssessmentQuestion(BareBaseModel):
    __tablename__ = "assessment_questions"
    
    assessment_type_id = Column(Integer, ForeignKey("assessment_types.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum))
    options = Column(JSON)
    correct_answer = Column(String)
    points = Column(Integer, default=1)
    order_index = Column(Integer)
    
    # Relationships
    assessment_type = relationship("AssessmentType")


class UserAssessment(BareBaseModel):
    __tablename__ = "user_assessments"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_type_id = Column(Integer, ForeignKey("assessment_types.id"), nullable=False)
    total_score = Column(Integer, nullable=False)
    max_possible_score = Column(Integer, nullable=False)
    percentage_score = Column(Numeric(5, 2), nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    duration_seconds = Column(Integer)
    status = Column(Enum(AssessmentStatusEnum), default=AssessmentStatusEnum.IN_PROGRESS)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User")
    assessment_type = relationship("AssessmentType")
    answers = relationship("AssessmentAnswer", back_populates="user_assessment")


class AssessmentAnswer(BareBaseModel):
    __tablename__ = "assessment_answers"
    
    user_assessment_id = Column(Integer, ForeignKey("user_assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    time_taken_seconds = Column(Integer)
    
    # Relationships
    user_assessment = relationship("UserAssessment", back_populates="answers")
    question = relationship("AssessmentQuestion")
