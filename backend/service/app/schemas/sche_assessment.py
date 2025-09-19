from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from app.schemas.sche_base import BaseModelResponse


class MMSEAnswer(BaseModel):
    section_index: int
    question_index: Optional[int] = None  # For multi-select sections
    answer: Union[str, int, float, List[str]]


class MMSESubmitRequest(BaseModel):
    user_id: int
    answers: List[MMSEAnswer]


# New optimized answer format
class MMSEAnswerOptimized(BaseModel):
    question_id: str  # e.g., "weekday", "calc_1", "memory_words"
    answer: Union[str, int, float, List[str]]


class MMSESubmitRequestOptimized(BaseModel):
    answers: List[MMSEAnswerOptimized]


class MMSEInterpretation(BaseModel):
    level: str
    score_range: str


class MMSEResultData(BaseModel):
    assessment_id: int
    user_id: int
    total_score: int
    max_score: int
    percentage: float
    interpretation: MMSEInterpretation
    completed_at: datetime
    saved_to_database: bool = True


class MMSEResult(BaseModel):
    success: bool = True
    message: str = "MMSE assessment submitted successfully"
    data: MMSEResultData


class MMSEHistoryItem(BaseModel):
    assessment_id: int
    test_date: datetime
    total_score: int
    max_score: int
    percentage: float
    interpretation: MMSEInterpretation


# Improved question structures
class QuestionMedia(BaseModel):
    """Media assets for questions"""
    type: str  # "image", "audio"
    url: str
    description: Optional[str] = None


class QuestionOption(BaseModel):
    """Question option with optional media"""
    value: str
    label: str
    media: Optional[QuestionMedia] = None


class MMSEQuestion(BaseModel):
    """Standardized question structure"""
    id: str  # Unique identifier for each question
    text: str  # Question text
    type: str  # "select", "multi-select", "number", "text"
    required: bool = True
    score_points: int = 1
    
    # Options for select/multi-select questions
    options: Optional[List[QuestionOption]] = None
    
    # Media assets
    media: Optional[List[QuestionMedia]] = None
    
    # Special properties
    time_limit_seconds: Optional[int] = None
    placeholder: Optional[str] = None
    validation_rule: Optional[str] = None  # For special validation logic


class MMSESection(BaseModel):
    """Standardized section structure"""
    id: str  # Unique section identifier
    title: str
    description: Optional[str] = None
    instruction: Optional[str] = None
    order: int
    
    # Section-level media (e.g., audio introduction)
    media: Optional[List[QuestionMedia]] = None
    
    # Questions in this section
    questions: List[MMSEQuestion]
    
    # Section metadata
    estimated_time_minutes: Optional[int] = None
    section_type: str = "standard"  # "standard", "calculation", "memory"


class MMSECognitiveLevel(BaseModel):
    score_range: str
    meaning: str
    recommendation: Optional[str] = None


class MMSEInterpretationGuide(BaseModel):
    cognitive_levels: List[MMSECognitiveLevel]
    notes: Optional[str] = None


class MMSETestStructure(BaseModel):
    """Optimized test structure for frontend"""
    test_info: Dict[str, Any]
    sections: List[MMSESection]
    interpretation_guide: MMSEInterpretationGuide
    ui_config: Dict[str, Any]  # Frontend configuration


# Legacy schemas for backward compatibility
class MMSETestOption(BaseModel):
    label: str
    imageUrl: Optional[str] = None


class MMSETestQuestion(BaseModel):
    label: str
    type: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    audioUrl: Optional[str] = None
    options: Optional[List[str]] = None
    imageOptions: Optional[List[MMSETestOption]] = None
    correctAnswer: Optional[Union[str, int, List[str]]] = None
    correctAnswers: Optional[List[str]] = None
    score: Optional[int] = None
    scoreEach: Optional[int] = None


class MMSETestSection(BaseModel):
    sectionName: str
    description: Optional[str] = None
    instruction: Optional[str] = None
    audioUrl: Optional[str] = None
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correctAnswers: Optional[List[str]] = None
    type: Optional[str] = None
    scoreEach: Optional[int] = None
    questions: Optional[List[MMSETestQuestion]] = None
    calculations: Optional[List[MMSETestQuestion]] = None


class MMSETestContent(BaseModel):
    test_id: int = 1
    test_name: str = "Kiểm tra MMSE phiên bản dễ kiểm tra"
    total_questions: int = 27
    max_score: int = 27
    sections: List[MMSETestSection]
    interpretation: MMSEInterpretationGuide


class AssessmentTypeResponse(BaseModelResponse):
    name: str
    description: Optional[str]
    difficulty_level: int
    max_score: int
    passing_score: Optional[int]
    is_active: bool


class UserAssessmentResponse(BaseModelResponse):
    user_id: int
    assessment_type_id: int
    total_score: int
    max_possible_score: int
    percentage_score: float
    difficulty_level: int
    duration_seconds: Optional[int]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    notes: Optional[str]

class MMSEQuestionDetail(BaseModel):
    """Detailed information about a specific question and answer"""
    question_id: str
    question_text: str
    question_type: str  # "select", "multi-select", "number", "text"
    section_name: str
    user_answer: Union[str, int, float, List[str], None]
    correct_answer: Union[str, int, float, List[str], None]
    is_correct: bool
    points_earned: int
    max_points: int
    explanation: Optional[str] = None  # Additional context for the answer


class MMSEHistoryItemDetailed(BaseModel):
    """Enhanced history item with question-level details"""
    assessment_id: int
    test_date: datetime
    total_score: int
    max_score: int
    percentage: float
    interpretation: MMSEInterpretation
    duration_seconds: Optional[int] = None
    question_details: List[MMSEQuestionDetail]

class MMSEHistorySummarySubmission(BaseModel):
    assessment_id: int
    test_date: str  # ISO format
    total_score: int
    interpretation: str
    section_scores: List[int]
    user_answers: List[Any]
    correct_answers:List[Any]
class MMSEHistorySummary(BaseModel):
    success: bool
    user_id: int
    test_id: str
    test_name: str
    chart_labels: List[str]
    submissions: List[MMSEHistorySummarySubmission]


# New schemas for chart data
class MMSERadarChartData(BaseModel):
    """Radar chart data for a single test result"""
    assessment_id: int
    test_date: str  # ISO format
    total_score: int
    max_score: int
    percentage: float
    interpretation: str
    section_labels: List[str]  # Section names
    section_scores: List[int]  # Actual scores per section
    section_max_scores: List[int]  # Max possible scores per section
    section_percentages: List[float]  # Percentage per section


class MMSELineChartDataPoint(BaseModel):
    """Single data point for line chart"""
    assessment_id: int
    test_date: str  # ISO format for x-axis
    total_score: int  # y-axis value
    percentage: float
    interpretation: str


class MMSEChartData(BaseModel):
    """Complete chart data response"""
    success: bool
    user_id: int
    test_name: str
    
    # Radar chart data (latest test only)
    radar_chart: Optional[MMSERadarChartData] = None
    
    # Line chart data (all tests)
    line_chart: Dict[str, Any]  # Contains labels, data points, metadata
    
    # Summary statistics
    summary_stats: Dict[str, Any]