from fastapi_sqlalchemy import db
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import pytz
from app.models.model_assessment import (
    UserAssessment, AssessmentAnswer, AssessmentType, AssessmentQuestion,
    AssessmentStatusEnum
)
from app.models.model_user import User, UserProfile
from app.schemas.sche_assessment import (
    MMSEHistoryItemDetailed, MMSEHistorySummary, MMSEHistorySummarySubmission, MMSEResult, MMSEAnswer, MMSEHistoryItem, MMSEInterpretation, MMSEResultData,
    MMSETestContent, MMSETestSection, MMSETestQuestion, MMSECognitiveLevel, MMSEInterpretationGuide,
    MMSETestStructure, MMSESection, MMSEQuestion, QuestionOption, QuestionMedia, MMSEQuestionDetail,
    MMSERadarChartData, MMSELineChartDataPoint, MMSEChartData
)
from app.utils.exception_handler import CustomException, ExceptionType
import logging


class AssessmentService:
    
    @staticmethod
    def get_mmse_test_content() -> MMSETestContent:
        """Get MMSE test content structure (legacy format)"""
        return AssessmentService._get_legacy_mmse_structure()
    
    @staticmethod
    def get_mmse_test_optimized() -> MMSETestStructure:
        """Get optimized MMSE test structure for modern frontend"""
        
        # Build optimized sections
        sections = [
            # Section 1: Time and Space Orientation
            MMSESection(
                id="time_space_orientation",
                title="Time and Space Orientation",
                description="Assessment of time and space orientation ability",
                order=1,
                estimated_time_minutes=3,
                questions=[
                    MMSEQuestion(
                        id="weekday",
                        text="What day of the week is today?",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(value="monday", label="Monday"),
                            QuestionOption(value="tuesday", label="Tuesday"),
                            QuestionOption(value="wednesday", label="Wednesday"),
                            QuestionOption(value="thursday", label="Thursday"),
                            QuestionOption(value="friday", label="Friday"),
                            QuestionOption(value="saturday", label="Saturday"),
                            QuestionOption(value="sunday", label="Sunday")
                        ]
                    ),
                    MMSEQuestion(
                        id="day",
                        text="What day of the month is it?",
                        type="number",
                        score_points=1,
                        placeholder="Enter day (1-31)",
                        validation_rule="range:1-31"
                    ),
                    MMSEQuestion(
                        id="month",
                        text="What month is it?",
                        type="number",
                        score_points=1,
                        placeholder="Enter month (1-12)",
                        validation_rule="range:1-12"
                    ),
                    MMSEQuestion(
                        id="year",
                        text="What year is it?",
                        type="number",
                        score_points=1,
                        placeholder="Enter year",
                        validation_rule="range:2020-2030"
                    ),
                    MMSEQuestion(
                        id="hour",
                        text="What time is it now?",
                        type="number",
                        score_points=1,
                        placeholder="Enter hour (0-23)",
                        validation_rule="range:0-23"
                    ),
                    MMSEQuestion(
                        id="city",
                        text="What city do you live in?",
                        type="text",
                        score_points=1,
                        placeholder="Enter city name"
                    ),
                    MMSEQuestion(
                        id="hometown",
                        text="Where is your hometown?",
                        type="text",
                        score_points=1,
                        placeholder="Enter hometown"
                    ),
                    MMSEQuestion(
                        id="country",
                        text="What country are you in?",
                        type="text",
                        score_points=1,
                        placeholder="Enter country name"
                    )
                ]
            ),
            
            # Section 2: Memory Reception
            MMSESection(
                id="memory_reception",
                title="Memory Reception and Retention",
                description="Assessment of information reception and retention ability",
                instruction="Listen to the audio and select the words mentioned",
                order=2,
                estimated_time_minutes=2,
                section_type="memory",
                media=[
                    QuestionMedia(
                        type="audio",
                        url="/static/audios/mmse_memory_words.mp3",
                        description="Audio containing 3 words to remember"
                    )
                ],
                questions=[
                    MMSEQuestion(
                        id="memory_words",
                        text="Which of the following words were mentioned?",
                        type="multi-select",
                        score_points=3,  # 1 point per correct word
                        options=[
                            QuestionOption(value="cat", label="Cat"),
                            QuestionOption(value="key", label="Key"),
                            QuestionOption(value="forest", label="Forest"),
                            QuestionOption(value="hammer", label="Hammer"),
                            QuestionOption(value="dog", label="Dog")
                        ]
                    )
                ]
            ),
            
            # Section 3: Attention and Calculation
            MMSESection(
                id="attention_calculation",
                title="Attention / Calculation Performance",
                description="Assessment of concentration and calculation ability",
                order=3,
                estimated_time_minutes=3,
                section_type="calculation",
                questions=[
                    MMSEQuestion(
                        id="calc_1",
                        text="What is 100 minus 7?",
                        type="number",
                        score_points=1,
                        placeholder="Enter result"
                    ),
                    MMSEQuestion(
                        id="calc_2",
                        text="What is 93 minus 7?",
                        type="number",
                        score_points=1,
                        placeholder="Enter result"
                    ),
                    MMSEQuestion(
                        id="calc_3",
                        text="What is 86 minus 7?",
                        type="number",
                        score_points=1,
                        placeholder="Enter result"
                    ),
                    MMSEQuestion(
                        id="calc_4",
                        text="What is 79 minus 7?",
                        type="number",
                        score_points=1,
                        placeholder="Enter result"
                    ),
                    MMSEQuestion(
                        id="calc_5",
                        text="What is 72 minus 7?",
                        type="number",
                        score_points=1,
                        placeholder="Enter result"
                    )
                ]
            ),
            
            # Section 4: Recent Memory
            MMSESection(
                id="recent_memory",
                title="Recent Memory",
                description="Assessment of ability to recall recently learned information",
                instruction="Select the words from the audio you heard earlier",
                order=4,
                estimated_time_minutes=1,
                section_type="memory",
                questions=[
                    MMSEQuestion(
                        id="recall_words",
                        text="Select the words from the previous audio:",
                        type="multi-select",
                        score_points=3,  # 1 point per correct word
                        options=[
                            QuestionOption(value="cat", label="Cat"),
                            QuestionOption(value="key", label="Key"),
                            QuestionOption(value="forest", label="Forest"),
                            QuestionOption(value="dog", label="Dog"),
                            QuestionOption(value="hammer", label="Hammer")
                        ]
                    )
                ]
            ),
            
            # Section 5: Language
            MMSESection(
                id="language",
                title="Language",
                description="Assessment of language recognition and comprehension ability",
                order=5,
                estimated_time_minutes=3,
                questions=[
                    MMSEQuestion(
                        id="identify_pen",
                        text="What is this?",
                        type="select",
                        score_points=1,
                        media=[
                            QuestionMedia(
                                type="image",
                                url="/static/images/mmse_pen.jpg",
                                description="Pen image"
                            )
                        ],
                        options=[
                            QuestionOption(value="pen", label="Pen"),
                            QuestionOption(value="scissors", label="Scissors"),
                            QuestionOption(value="spoon", label="Spoon")
                        ]
                    ),
                    MMSEQuestion(
                        id="identify_clock",
                        text="What is this?",
                        type="select",
                        score_points=1,
                        media=[
                            QuestionMedia(
                                type="image",
                                url="/static/images/mmse_clock.jpg",
                                description="Clock image"
                            )
                        ],
                        options=[
                            QuestionOption(value="clock", label="Clock"),
                            QuestionOption(value="cup", label="Cup"),
                            QuestionOption(value="hammer", label="Hammer")
                        ]
                    ),
                    MMSEQuestion(
                        id="audio_topic",
                        text="What is the topic of the following audio?",
                        type="select",
                        score_points=1,
                        media=[
                            QuestionMedia(
                                type="audio",
                                url="/static/audios/mmse_conversation_topic.mp3",
                                description="Short conversation"
                            )
                        ],
                        options=[
                            QuestionOption(value="family", label="Family life"),
                            QuestionOption(value="weather", label="Today's weather"),
                            QuestionOption(value="work", label="Office work")
                        ]
                    )
                ]
            ),
            
            # Section 6: Verbal Understanding
            MMSESection(
                id="verbal_understanding",
                title="Verbal Comprehension",
                description="Assessment of ability to understand and follow verbal instructions",
                order=6,
                estimated_time_minutes=2,
                questions=[
                    MMSEQuestion(
                        id="nose_instruction",
                        text="If you are asked 'Use your right hand to touch your nose', what would you do?",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(value="touch_nose", label="Touch nose with right hand"),
                            QuestionOption(value="touch_ear", label="Touch left ear"),
                            QuestionOption(value="no_action", label="Do nothing")
                        ]
                    ),
                    MMSEQuestion(
                        id="ear_instruction",
                        text="If you are asked 'Touch your left ear', what would you do?",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(value="touch_ear", label="Touch left ear"),
                            QuestionOption(value="touch_nose", label="Touch nose"),
                            QuestionOption(value="no_action", label="Do nothing")
                        ]
                    )
                ]
            ),
            
            # Section 7: Written Language Understanding
            MMSESection(
                id="written_understanding",
                title="Written Comprehension",
                description="Assessment of ability to understand and follow written instructions",
                order=7,
                estimated_time_minutes=1,
                questions=[
                    MMSEQuestion(
                        id="written_instruction",
                        text="If you read the text 'CLOSE YOUR EYES', what would you do?",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(value="close_eyes", label="Close your eyes"),
                            QuestionOption(value="read_aloud", label="Read aloud"),
                            QuestionOption(value="no_action", label="Do nothing")
                        ]
                    )
                ]
            ),
            
            # Section 8: Writing and Visual Skills
            MMSESection(
                id="writing_visual",
                title="Writing and Visual Skills",
                description="Assessment of writing ability and visual perception",
                order=8,
                estimated_time_minutes=2,
                questions=[
                    MMSEQuestion(
                        id="grammar_sentence",
                        text="Please select the grammatically correct and meaningful sentence:",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(value="correct", label="I eat lunch with my family."),
                            QuestionOption(value="wrong1", label="House go water learn."),
                            QuestionOption(value="wrong2", label="Table chair house door."),
                            QuestionOption(value="wrong3", label="Rice family water.")
                        ]
                    ),
                    MMSEQuestion(
                        id="pentagon_shape",
                        text="Which is the correct drawing of 2 intersecting pentagons?",
                        type="select",
                        score_points=1,
                        options=[
                            QuestionOption(
                                value="image_a", 
                                label="Image A",
                                media=QuestionMedia(
                                    type="image",
                                    url="/static/images/mmse_pentagon_a.jpg",
                                    description="2 non-intersecting pentagons"
                                )
                            ),
                            QuestionOption(
                                value="image_b", 
                                label="Image B",
                                media=QuestionMedia(
                                    type="image",
                                    url="/static/images/mmse_pentagon_b.jpg",
                                    description="2 intersecting pentagons (correct)"
                                )
                            ),
                            QuestionOption(
                                value="image_c", 
                                label="Image C",
                                media=QuestionMedia(
                                    type="image",
                                    url="/static/images/mmse_pentagon_c.jpg",
                                    description="2 overlapping pentagons"
                                )
                            )
                        ]
                    )
                ]
            )
        ]
        
        # Test information
        test_info = {
            "id": "mmse_v1",
            "name": "MMSE Test (Mini Mental State Examination)",
            "version": "1.0",
            "description": "Basic cognitive function assessment test",
            "total_questions": 27,
            "max_score": 27,
            "estimated_duration_minutes": 15,
            "created_date": "2025-08-10",
            "language": "en"
        }
        
        # Interpretation guide
        interpretation_guide = MMSEInterpretationGuide(
            cognitive_levels=[
                MMSECognitiveLevel(
                    score_range="24-27",
                    meaning="No cognitive impairment",
                    recommendation="Normal cognitive function"
                ),
                MMSECognitiveLevel(
                    score_range="20-23",
                    meaning="Mild cognitive impairment",
                    recommendation="Monitoring and further assessment recommended"
                ),
                MMSECognitiveLevel(
                    score_range="14-19",
                    meaning="Moderate cognitive impairment",
                    recommendation="Specialist consultation recommended"
                ),
                MMSECognitiveLevel(
                    score_range="0-13",
                    meaning="Severe cognitive impairment",
                    recommendation="Immediate medical intervention required"
                )
            ],
            notes="Results are for reference only. Should be combined with clinical assessment."
        )
        
        # UI Configuration for frontend
        ui_config = {
            "theme": "medical",
            "show_progress": True,
            "allow_back_navigation": True,
            "auto_save": True,
            "time_warnings": {
                "show_timer": False,
                "warn_at_minutes": 10
            },
            "validation": {
                "required_all_questions": True,
                "show_validation_errors": True
            },
            "media": {
                "audio_controls": {
                    "show_controls": True,
                    "allow_replay": True,
                    "auto_play": False
                },
                "image_display": {
                    "max_width": "400px",
                    "responsive": True
                }
            }
        }
        
        return MMSETestStructure(
            test_info=test_info,
            sections=sections,
            interpretation_guide=interpretation_guide,
            ui_config=ui_config
        )
    
    @staticmethod
    def _get_legacy_mmse_structure() -> MMSETestContent:
        """Get MMSE test content structure"""
        
        # Hardcoded MMSE test structure as requested
        sections = [
            # Section 1: Time and Space Orientation
            MMSETestSection(
                sectionName="Time and Space Orientation",
                questions=[
                    MMSETestQuestion(
                        label="What day of the week is today?",
                        type="select",
                        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What day of the month is it?",
                        type="number",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What month is it?",
                        type="number",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What year is it?",
                        type="number",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What time is it now?",
                        type="number",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What city do you live in?",
                        type="text",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="Where is your hometown?",
                        type="text",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What country are you in?",
                        type="text",
                        score=1
                    )
                ]
            ),
            
            # Section 2: Memory Reception and Retention
            MMSETestSection(
                sectionName="Memory Reception and Retention",
                description="User listens to audio and selects mentioned words",
                instruction="Select the words that were mentioned:",
                audioUrl="/static/audios/mmse_memory_words.mp3",
                question="Which of the following words were mentioned?",
                options=["Cat", "Key", "Forest", "Hammer", "Dog"],
                correctAnswers=["Cat", "Key", "Forest"],
                type="multi-select",
                scoreEach=1
            ),
            
            # Section 3: Attention / Calculation Performance
            MMSETestSection(
                sectionName="Attention / Calculation Performance",
                calculations=[
                    MMSETestQuestion(label="What is 100 minus 7?", type="number", correctAnswer=93, score=1),
                    MMSETestQuestion(label="What is 93 minus 7?", type="number", correctAnswer=86, score=1),
                    MMSETestQuestion(label="What is 86 minus 7?", type="number", correctAnswer=79, score=1),
                    MMSETestQuestion(label="What is 79 minus 7?", type="number", correctAnswer=72, score=1),
                    MMSETestQuestion(label="What is 72 minus 7?", type="number", correctAnswer=65, score=1)
                ]
            ),
            
            # Section 4: Recent Memory
            MMSETestSection(
                sectionName="Recent Memory",
                instruction="Select the words from the audio you heard earlier.",
                options=["Cat", "Key", "Forest", "Dog", "Hammer"],
                correctAnswers=["Cat", "Key", "Forest"],
                type="multi-select",
                scoreEach=1
            ),
            
            # Section 5: Language
            MMSETestSection(
                sectionName="Language",
                questions=[
                    MMSETestQuestion(
                        label="What is this? (Pen image displayed)",
                        description="Display pen image",
                        imageUrl="/static/images/mmse_pen.jpg",
                        type="select",
                        options=["Pen", "Scissors", "Spoon"],
                        correctAnswer="Pen",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What is this? (Clock image displayed)",
                        description="Display clock image",
                        imageUrl="/static/images/mmse_clock.jpg",
                        type="select",
                        options=["Clock", "Cup", "Hammer"],
                        correctAnswer="Clock",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="What is the topic of the following audio?",
                        description="Play a short conversation, and the test taker selects the correct topic",
                        audioUrl="/static/audios/mmse_conversation_topic.mp3",
                        type="select",
                        options=["Family life", "Today's weather", "Office work"],
                        correctAnswer="Family life",
                        score=1
                    )
                ]
            ),
            
            # Section 6: Verbal Comprehension
            MMSETestSection(
                sectionName="Verbal Comprehension",
                questions=[
                    MMSETestQuestion(
                        label="If you are asked 'Use your right hand to touch your nose', what would you do?",
                        type="select",
                        options=["Touch nose with right hand", "Touch left ear", "Do nothing"],
                        correctAnswer="Touch nose with right hand",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="If you are asked 'Touch your left ear', what would you do?",
                        type="select",
                        options=["Touch left ear", "Touch nose", "Do nothing"],
                        correctAnswer="Touch left ear",
                        score=1
                    )
                ]
            ),
            
            # Section 7: Written Comprehension
            MMSETestSection(
                sectionName="Written Comprehension",
                questions=[
                    MMSETestQuestion(
                        label="If you read the text 'CLOSE YOUR EYES', what would you do?",
                        type="select",
                        options=["Close your eyes", "Read aloud", "Do nothing"],
                        correctAnswer="Close your eyes",
                        score=1
                    )
                ]
            ),
            
            # Section 8: Writing and Visual Skills
            MMSETestSection(
                sectionName="Writing and Visual Skills",
                questions=[
                    MMSETestQuestion(
                        label="Please select the grammatically correct and meaningful sentence:",
                        type="select",
                        options=[
                            "I eat lunch with my family.",
                            "House go water learn.",
                            "Table chair house door.",
                            "Rice family water."
                        ],
                        correctAnswer="I eat lunch with my family.",
                        score=1
                    ),
                    MMSETestQuestion(
                        label="Which is the correct drawing of 2 intersecting pentagons?",
                        description="Display 3 images for selection",
                        imageOptions=[
                            {"label": "Image A", "imageUrl": "/static/images/mmse_pentagon_a.jpg"},
                            {"label": "Image B", "imageUrl": "/static/images/mmse_pentagon_b.jpg"},
                            {"label": "Image C", "imageUrl": "/static/images/mmse_pentagon_c.jpg"}
                        ],
                        type="select",
                        options=["Image A", "Image B", "Image C"],
                        correctAnswer="Image B",
                        score=1
                    )
                ]
            )
        ]
        
        interpretation = MMSEInterpretationGuide(
            cognitive_levels=[
                MMSECognitiveLevel(score_range=">=24", meaning="No cognitive impairment"),
                MMSECognitiveLevel(score_range="20-23", meaning="Mild cognitive impairment, may need monitoring/support"),
                MMSECognitiveLevel(score_range="14-19", meaning="Moderate cognitive impairment"),
                MMSECognitiveLevel(score_range="<=13", meaning="Severe cognitive impairment")
            ]
        )
        
        return MMSETestContent(
            sections=sections,
            interpretation=interpretation
        )
    
    # @staticmethod
    # def submit_mmse_test(user_id: int, answers: List[MMSEAnswer]) -> MMSEResult:
    #     """Submit MMSE test and calculate score"""
    #     try:
    #         # Get current time in Singapore timezone (UTC+8)
    #         singapore_tz = pytz.timezone('Asia/Singapore')
    #         completed_time = datetime.now(singapore_tz)
            
    #         # Get user profile for location validation
    #         user_profile = db.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
    #         # Calculate score
    #         total_score = 0
    #         max_score = 27
            
    #         # Get test content for scoring
    #         test_content = AssessmentService.get_mmse_test_content()
            
    #         # Score each answer
    #         for answer in answers:
    #             score = AssessmentService._score_answer(answer, test_content, user_profile, completed_time)
    #             total_score += score
            
    #         # Calculate percentage
    #         percentage = round((total_score / max_score) * 100, 2)
            
    #         # Get interpretation
    #         interpretation = AssessmentService._get_interpretation(total_score)
            
    #         # Save to database
    #         assessment_id = AssessmentService._save_assessment_to_db(
    #             user_id, total_score, max_score, percentage, completed_time, answers
    #         )
            
    #         return MMSEResult(
    #             data=MMSEResultData(
    #                 assessment_id=assessment_id,
    #                 user_id=user_id,
    #                 total_score=total_score,
    #                 max_score=max_score,
    #                 percentage=percentage,
    #                 interpretation=interpretation,
    #                 completed_at=completed_time
    #             )
    #         )
            
    #     except Exception as e:
    #         logging.error(f"Error submitting MMSE test: {str(e)}")
    #         raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def _score_answer(answer: MMSEAnswer, test_content: MMSETestContent, user_profile: UserProfile, current_time: datetime) -> int:
        """Score individual answer with smart logic"""
        section = test_content.sections[answer.section_index]
        score = 0
        
        # Section 0: Time and location questions
        if answer.section_index == 0:
            if answer.question_index == 0:  # Day of week
                # Map weekday values to weekday numbers
                weekday_map = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                user_weekday = weekday_map.get(str(answer.answer).lower())
                if user_weekday is not None and user_weekday == current_time.weekday():
                    score = 1
            elif answer.question_index == 1:  # Day
                try:
                    day_num = int(answer.answer)
                    if day_num == current_time.day:
                        score = 1
                except ValueError:
                    pass  # Invalid day format
            elif answer.question_index == 2:  # Month
                # Handle both month names and numbers (English and Vietnamese)
                try:
                    month_num = int(answer.answer)
                except ValueError:
                    # Convert month name to number (English)
                    month_names = {
                        "january": 1, "february": 2, "march": 3, "april": 4,
                        "may": 5, "june": 6, "july": 7, "august": 8,
                        "september": 9, "october": 10, "november": 11, "december": 12,
                        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                        "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                        # Keep Vietnamese support for backward compatibility
                        "tháng một": 1, "tháng hai": 2, "tháng ba": 3, "tháng tư": 4,
                        "tháng năm": 5, "tháng sáu": 6, "tháng bảy": 7, "tháng tám": 8,
                        "tháng chín": 9, "tháng mười": 10, "tháng mười một": 11, "tháng mười hai": 12
                    }
                    month_num = month_names.get(answer.answer.lower(), 0)
                
                if month_num == current_time.month:
                    score = 1
            elif answer.question_index == 3:  # Year
                try:
                    year_num = int(answer.answer)
                    if year_num == current_time.year:
                        score = 1
                except ValueError:
                    pass  # Invalid year format
            elif answer.question_index == 4:  # Hour (±1 hour tolerance)
                try:
                    user_hour = int(answer.answer)
                    current_hour = current_time.hour
                    if abs(user_hour - current_hour) <= 1:
                        score = 1
                except ValueError:
                    pass  # Invalid hour format
            elif answer.question_index == 5:  # City
                if user_profile and user_profile.city and str(answer.answer).lower() == user_profile.city.lower():
                    score = 1
            elif answer.question_index == 6:  # Hometown
                if user_profile and user_profile.hometown and str(answer.answer).lower() == user_profile.hometown.lower():
                    score = 1
            elif answer.question_index == 7:  # Country
                if user_profile and user_profile.country and str(answer.answer).lower() == user_profile.country.lower():
                    score = 1
        
        # Section 1: Memory words (multi-select)
        elif answer.section_index == 1:
            # Correct answer values from API structure (English version)
            correct_answers = ["cat", "key", "forest"]
            user_answers = answer.answer if isinstance(answer.answer, list) else []
            correct_count = len(set(user_answers) & set(correct_answers))
            score = correct_count  # 1 point per correct word
        
        # Section 2: Calculations (Serial 7s)
        elif answer.section_index == 2:
            # Expected answers for each calculation question
            expected_answers = [93, 86, 79, 72, 65]
            if answer.question_index < len(expected_answers):
                try:
                    user_answer = int(answer.answer)
                    expected = expected_answers[answer.question_index]
                    if user_answer == expected:
                        score = 1
                except ValueError:
                    pass  # Invalid numeric answer
        
        # Section 3: Memory recall (multi-select) 
        elif answer.section_index == 3:
            # Same correct answers as section 1 (English version)
            correct_answers = ["cat", "key", "forest"]
            user_answers = answer.answer if isinstance(answer.answer, list) else []
            correct_count = len(set(user_answers) & set(correct_answers))
            score = correct_count  # 1 point per correct word
        
        # Section 4: Language (3 questions)
        elif answer.section_index == 4:
            if answer.question_index == 0:  # Identify pen
                if str(answer.answer).lower() == "pen":
                    score = 1
            elif answer.question_index == 1:  # Identify clock
                if str(answer.answer).lower() == "clock":
                    score = 1
            elif answer.question_index == 2:  # Audio topic
                if str(answer.answer).lower() == "family":
                    score = 1
        
        # Section 5: Verbal understanding (2 questions)
        elif answer.section_index == 5:
            if answer.question_index == 0:  # Nose instruction
                if str(answer.answer).lower() == "touch_nose":
                    score = 1
            elif answer.question_index == 1:  # Ear instruction
                if str(answer.answer).lower() == "touch_ear":
                    score = 1
        
        # Section 6: Written understanding (1 question)
        elif answer.section_index == 6:
            if answer.question_index == 0:  # Close eyes instruction
                if str(answer.answer).lower() == "close_eyes":
                    score = 1
        
        # Section 7: Writing and visual (2 questions)
        elif answer.section_index == 7:
            if answer.question_index == 0:  # Grammar sentence
                if str(answer.answer).lower() == "correct":
                    score = 1
            elif answer.question_index == 1:  # Pentagon shape
                if str(answer.answer).lower() == "image_b":
                    score = 1
        
        return score
    
    @staticmethod
    def _get_interpretation(total_score: int) -> MMSEInterpretation:
        """Get cognitive interpretation based on score"""
        if total_score >= 24:
            return MMSEInterpretation(level="No cognitive impairment", score_range=">=24")
        elif total_score >= 20:
            return MMSEInterpretation(level="Mild cognitive impairment, may need monitoring/support", score_range="20-23")
        elif total_score >= 14:
            return MMSEInterpretation(level="Moderate cognitive impairment", score_range="14-19")
        else:
            return MMSEInterpretation(level="Severe cognitive impairment", score_range="<=13")
    
    @staticmethod
    def _save_assessment_to_db(user_id: int, total_score: int, max_score: int, percentage: float, completed_time: datetime, answers: List[MMSEAnswer]) -> int:
        """Save assessment results to database"""
        try:
            # Create user assessment record
            user_assessment = UserAssessment(
                user_id=user_id,
                assessment_type_id=1,  # MMSE type ID (hardcoded as per requirement)
                total_score=total_score,
                max_possible_score=max_score,
                percentage_score=percentage,
                difficulty_level=1,
                status=AssessmentStatusEnum.COMPLETED,
                completed_at=completed_time
            )
            
            db.session.add(user_assessment)
            db.session.commit()
            
            return user_assessment.id
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving assessment to database: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def submit_mmse_test(user_id: int, answers: List[MMSEAnswer]) -> MMSEResult:
        """Submit MMSE test and calculate score with detailed answer storage"""
        try:
            # Get current time in Singapore timezone (UTC+8)
            singapore_tz = pytz.timezone('Asia/Singapore')
            completed_time = datetime.now(singapore_tz)
            
            # Get user profile for location validation
            user_profile = db.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            # Calculate score
            total_score = 0
            max_score = 27
            
            # Get test content for scoring
            test_content = AssessmentService.get_mmse_test_content()
            
            # Score each answer
            for answer in answers:
                score = AssessmentService._score_answer(answer, test_content, user_profile, completed_time)
                total_score += score
            
            # Calculate percentage
            percentage = round((total_score / max_score) * 100, 2)
            
            # Get interpretation
            interpretation = AssessmentService._get_interpretation(total_score)
            
            # Save to database
            assessment_id = AssessmentService._save_assessment_to_db(
                user_id, total_score, max_score, percentage, completed_time, answers
            )
            
            # Save detailed answers for future history retrieval
            AssessmentService._save_detailed_answers_to_db(
                assessment_id, answers, test_content, user_profile, completed_time
            )
            
            return MMSEResult(
                data=MMSEResultData(
                    assessment_id=assessment_id,
                    user_id=user_id,
                    total_score=total_score,
                    max_score=max_score,
                    percentage=percentage,
                    interpretation=interpretation,
                    completed_at=completed_time
                )
            )
            
        except Exception as e:
            logging.error(f"Error submitting MMSE test: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_mmse_history_detailed(user_id: int) -> List[MMSEHistoryItemDetailed]:
        """Get user's MMSE test history with detailed question breakdown"""
        try:
            # Get all completed assessments with their answers
            assessments = db.session.query(UserAssessment).filter(
                UserAssessment.user_id == user_id,
                UserAssessment.assessment_type_id == 1,  # MMSE type
                UserAssessment.status == AssessmentStatusEnum.COMPLETED,
                # UserAssessment.completed_at >= datetime.now(timezone.utc) - timedelta(weeks=2)  
            ).order_by(desc(UserAssessment.completed_at)).all()
            
            history = []
            for assessment in assessments:
                interpretation = AssessmentService._get_interpretation(assessment.total_score)
                
                # Get question details for this assessment
                question_details = AssessmentService._get_question_details_for_assessment(assessment.id)
                
                history.append(MMSEHistoryItemDetailed(
                    assessment_id=assessment.id,
                    test_date=assessment.completed_at,
                    total_score=assessment.total_score,
                    max_score=assessment.max_possible_score,
                    percentage=float(assessment.percentage_score),
                    interpretation=interpretation,
                    duration_seconds=assessment.duration_seconds,
                    question_details=question_details
                ))
            
            return history
            
        except Exception as e:
            logging.error(f"Error getting detailed MMSE history: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
        
    @staticmethod
    def get_mmse_history(user_id: int) -> List[MMSEHistoryItem]:
        """Get user's MMSE test history"""
        try:
            assessments = db.session.query(UserAssessment).filter(
                UserAssessment.user_id == user_id,
                UserAssessment.assessment_type_id == 1,  # MMSE type
                UserAssessment.status == AssessmentStatusEnum.COMPLETED,
                # UserAssessment.completed_at >= datetime.now(timezone.utc) - timedelta(weeks=2)  
            ).order_by(desc(UserAssessment.completed_at)).all()
            
            history = []
            for assessment in assessments:
                interpretation = AssessmentService._get_interpretation(assessment.total_score)
                
                history.append(MMSEHistoryItem(
                    assessment_id=assessment.id,
                    test_date=assessment.completed_at,
                    total_score=assessment.total_score,
                    max_score=assessment.max_possible_score,
                    percentage=float(assessment.percentage_score),
                    interpretation=interpretation
                ))
            
            return history
            
        except Exception as e:
            logging.error(f"Error getting MMSE history: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)

    @staticmethod
    def _get_question_details_for_assessment(assessment_id: int) -> List[MMSEQuestionDetail]:
        """Get detailed question information for a specific assessment"""
        try:
            # Get all answers for this assessment
            answers = db.session.query(AssessmentAnswer).join(
                AssessmentQuestion
            ).filter(
                AssessmentAnswer.user_assessment_id == assessment_id
            ).order_by(AssessmentAnswer.id).all()
            
            # Get test structure for reference
            test_structure = AssessmentService.get_mmse_test_optimized()
            
            # Create question mapping for easy lookup
            question_map = {}
            for section in test_structure.sections:
                for question in section.questions:
                    question_map[question.id] = {
                        'question': question,
                        'section_name': section.title
                    }
            
            question_details = []
            
            # If we have stored answers in database, use them
            if answers:
                for answer in answers:
                    question_id = AssessmentService._get_question_id_from_db(answer.question_id)
                    question_info = question_map.get(question_id, {})
                    
                    if question_info:
                        question = question_info['question']
                        section_name = question_info['section_name']
                        
                        # Get correct answer for this question
                        correct_answer = AssessmentService._get_correct_answer_for_question(question_id)
                        
                        question_details.append(MMSEQuestionDetail(
                            question_id=question_id,
                            question_text=question.text,
                            question_type=question.type,
                            section_name=section_name,
                            user_answer=answer.user_answer,
                            correct_answer=correct_answer,
                            is_correct=answer.is_correct,
                            points_earned=answer.points_earned,
                            max_points=question.score_points,
                            explanation=AssessmentService._get_answer_explanation(question_id, answer.user_answer, correct_answer)
                        ))
            else:
                # Fallback: Generate question details from test structure
                # This handles cases where detailed answers weren't stored in database
                question_details = AssessmentService._generate_question_details_from_structure(test_structure)
            
            return question_details
            
        except Exception as e:
            logging.error(f"Error getting question details: {str(e)}")
            return []
    
    @staticmethod
    def get_mmse_history_summary(user_id: int) -> MMSEHistorySummary:
        """Get user's MMSE test history in summary with section scores and answers"""
        try:
            # Các section cố định theo thứ tự chart_labels
            chart_labels = [
                "Time and Space Orientation",
                "Memory Reception and Retention",
                "Attention / Calculation Performance",
                "Recent Memory",
                "Language",
                "Verbal Comprehension",
                "Written Comprehension",
                "Writing and Visual Skills"
            ]

            assessments = db.session.query(UserAssessment).filter(
                UserAssessment.user_id == user_id,
                UserAssessment.assessment_type_id == 1,  # MMSE
                UserAssessment.status == AssessmentStatusEnum.COMPLETED,
                UserAssessment.completed_at >= datetime.now(timezone.utc) - timedelta(weeks=2)
            ).order_by(desc(UserAssessment.completed_at)).all()

            submissions = []
            for assessment in assessments:
                # Lấy interpret
                interpretation = AssessmentService._get_interpretation(assessment.total_score)
                interpretation_text = interpretation.get("level") if isinstance(interpretation, dict) else str(interpretation)

                # Lấy chi tiết câu hỏi
                question_details = AssessmentService._get_question_details_for_assessment(assessment.id)

                # Khởi tạo score per section và answer lists
                section_scores = [0] * len(chart_labels)
                user_answers = []
                correct_answers = []

                for q in question_details:
                    if q.section_name in chart_labels:
                        idx = chart_labels.index(q.section_name)
                        section_scores[idx] += q.points_earned or 0

                    # Lưu user answer và correct answer
                    user_answers.append(q.user_answer)
                    correct_answers.append(q.correct_answer)

                submissions.append(MMSEHistorySummarySubmission(
                    assessment_id=assessment.id,
                    test_date=assessment.completed_at.isoformat(),
                    total_score=assessment.total_score,
                    interpretation=interpretation_text,
                    section_scores=section_scores,
                    user_answers=user_answers,
                    correct_answers=correct_answers
                ))

            return MMSEHistorySummary(
                success=True,
                user_id=user_id,
                test_id="mmse_v1",
                test_name="MMSE Test (Mini Mental State Examination)",
                chart_labels=chart_labels,
                submissions=submissions
            )

        except Exception as e:
            logging.error(f"Error getting MMSE summary: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)


    @staticmethod
    def _get_question_id_from_db(db_question_id: int) -> str:
        """Map database question ID to our question identifier"""
        # This mapping depends on how questions are stored in your database
        # You may need to adjust this based on your actual database structure
        
        question_id_mapping = {
            1: "weekday", 2: "day", 3: "month", 4: "year", 5: "hour",
            6: "city", 7: "hometown", 8: "country", 9: "memory_words",
            10: "calc_1", 11: "calc_2", 12: "calc_3", 13: "calc_4", 14: "calc_5",
            15: "recall_words", 16: "identify_pen", 17: "identify_clock", 18: "audio_topic",
            19: "nose_instruction", 20: "ear_instruction", 21: "written_instruction",
            22: "grammar_sentence", 23: "pentagon_shape"
        }
        
        return question_id_mapping.get(db_question_id, f"question_{db_question_id}")
    



    @staticmethod
    def _get_correct_answer_for_question(question_id: str) -> Union[str, int, List[str], None]:
        """Get the correct answer for a specific question"""
        correct_answers = {
            # Time/Space questions - these are dynamic based on current time/user profile
            "weekday": "dynamic",  # Current weekday
            "day": "dynamic",      # Current day
            "month": "dynamic",    # Current month
            "year": "dynamic",     # Current year
            "hour": "dynamic",     # Current hour (±1)
            "city": "dynamic",     # User's city
            "hometown": "dynamic", # User's hometown
            "country": "dynamic",  # User's country
            
            # Memory questions
            "memory_words": ["cat", "key", "forest"],
            "recall_words": ["cat", "key", "forest"],
            
            # Calculation questions
            "calc_1": 93,
            "calc_2": 86,
            "calc_3": 79,
            "calc_4": 72,
            "calc_5": 65,
            
            # Language questions
            "identify_pen": "pen",
            "identify_clock": "clock",
            "audio_topic": "family",
            
            # Comprehension questions
            "nose_instruction": "touch_nose",
            "ear_instruction": "touch_ear",
            "written_instruction": "close_eyes",
            
            # Writing/Visual questions
            "grammar_sentence": "correct",
            "pentagon_shape": "image_b"
        }
        
        return correct_answers.get(question_id)
    
    @staticmethod
    def _get_answer_explanation(question_id: str, user_answer: Any, correct_answer: Any) -> Optional[str]:
        """Provide explanation for the answer"""
        explanations = {
            "memory_words": "Listen carefully to the audio and select all mentioned words",
            "recall_words": "Recall the words from the earlier audio segment",
            "calc_1": "100 - 7 = 93",
            "calc_2": "93 - 7 = 86", 
            "calc_3": "86 - 7 = 79",
            "calc_4": "79 - 7 = 72",
            "calc_5": "72 - 7 = 65",
            "identify_pen": "This is a common writing instrument",
            "identify_clock": "This device shows time",
            "audio_topic": "The conversation was about family matters",
            "nose_instruction": "Follow the verbal instruction exactly",
            "ear_instruction": "Touch the specified ear as instructed",
            "written_instruction": "Follow the written command",
            "grammar_sentence": "Select the grammatically correct and meaningful sentence",
            "pentagon_shape": "Choose the image showing two intersecting five-sided shapes"
        }
        
        base_explanation = explanations.get(question_id, "")
        
        # Add dynamic explanation for time-based questions
        if question_id in ["weekday", "day", "month", "year", "hour"]:
            base_explanation = "Answer based on current date and time"
        elif question_id in ["city", "hometown", "country"]:
            base_explanation = "Answer based on your profile information"
        
        return base_explanation
    
    @staticmethod
    def _generate_question_details_from_structure(test_structure: MMSETestStructure) -> List[MMSEQuestionDetail]:
        """Generate question details when database doesn't have detailed answers"""
        question_details = []
        
        for section in test_structure.sections:
            for question in section.questions:
                correct_answer = AssessmentService._get_correct_answer_for_question(question.id)
                
                question_details.append(MMSEQuestionDetail(
                    question_id=question.id,
                    question_text=question.text,
                    question_type=question.type,
                    section_name=section.title,
                    user_answer=None,  # No stored answer
                    correct_answer=correct_answer,
                    is_correct=False,  # Unknown
                    points_earned=0,   # Unknown
                    max_points=question.score_points,
                    explanation=AssessmentService._get_answer_explanation(question.id, None, correct_answer)
                ))
        
        return question_details
    
    @staticmethod
    def _save_detailed_answers_to_db(assessment_id: int, answers: List[MMSEAnswer], test_content: MMSETestContent, user_profile: UserProfile, completed_time: datetime):
        """Save detailed answer information to database for future history retrieval"""
        try:
            # Get test structure for question mapping
            test_structure = AssessmentService.get_mmse_test_optimized()
            question_map = {}
            
            for section_idx, section in enumerate(test_structure.sections):
                for question_idx, question in enumerate(section.questions):
                    question_map[f"{section_idx}_{question_idx}"] = question.id
            
            # Create detailed answer records
            for answer in answers:
                # Map to question ID
                question_key = f"{answer.section_index}_{answer.question_index if answer.question_index is not None else 0}"
                question_id = question_map.get(question_key, f"unknown_{question_key}")
                
                # Score the answer
                score = AssessmentService._score_answer(answer, test_content, user_profile, completed_time)
                correct_answer = AssessmentService._get_correct_answer_for_question(question_id)
                
                # Determine if answer is correct
                is_correct = score > 0
                
                # Create database record (you'll need to ensure your AssessmentAnswer model supports this)
                answer_record = AssessmentAnswer(
                    user_assessment_id=assessment_id,
                    question_id=AssessmentService._get_db_question_id(question_id),
                    user_answer=str(answer.answer) if not isinstance(answer.answer, list) else ','.join(map(str, answer.answer)),
                    is_correct=is_correct,
                    points_earned=score,
                    time_taken_seconds=None  # Can be added if you track timing
                )
                
                db.session.add(answer_record)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving detailed answers: {str(e)}")
            # Don't raise exception as this is supplementary data
    
    @staticmethod
    def get_mmse_chart_data(user_id: int) -> MMSEChartData:
        """Get chart data for radar chart and line chart visualization"""
        try:
            # Get all assessments - ORDER BY DESC to get latest first (most recent date first)
            assessments = db.session.query(UserAssessment).filter(
                UserAssessment.user_id == user_id,
                UserAssessment.assessment_type_id == 1,  # MMSE type
                UserAssessment.status == AssessmentStatusEnum.COMPLETED
            ).order_by(UserAssessment.completed_at.desc(), UserAssessment.id.desc()).all()  # Order by date DESC, then ID DESC for tie-breaking
            
            if not assessments:
                return MMSEChartData(
                    success=True,
                    user_id=user_id,
                    test_name="MMSE Test (Mini Mental State Examination)",
                    radar_chart=None,
                    line_chart={
                        "labels": [],
                        "data": [],
                        "metadata": {"total_tests": 0}
                    },
                    summary_stats={
                        "total_tests": 0,
                        "average_score": 0,
                        "highest_score": 0,
                        "latest_score": 0,
                        "improvement_trend": "no_data"
                    }
                )
            
            # Log for debugging - the FIRST assessment should be the latest
            latest_assessment = assessments[0]
            logging.info(f"Chart Data - Latest assessment selected: ID={latest_assessment.id}, Date={latest_assessment.completed_at}, Score={latest_assessment.total_score}")
            
            # Prepare line chart data - REVERSE order for chronological display (oldest to newest)
            line_chart_data = []
            for assessment in reversed(assessments):  # Reverse to show chronological progression
                interpretation = AssessmentService._get_interpretation(assessment.total_score)
                interpretation_text = interpretation.level if hasattr(interpretation, 'level') else str(interpretation)
                
                line_chart_data.append(MMSELineChartDataPoint(
                    assessment_id=assessment.id,
                    test_date=assessment.completed_at.isoformat(),
                    total_score=assessment.total_score,
                    percentage=float(assessment.percentage_score),
                    interpretation=interpretation_text
                ))
            
            # Get radar chart data for THE LATEST assessment (first in DESC-ordered list)
            radar_chart_data = AssessmentService._create_radar_chart_data(latest_assessment)
            
            # Calculate summary statistics based on DESC-ordered assessments
            scores = [a.total_score for a in assessments]
            summary_stats = {
                "total_tests": len(assessments),
                "average_score": round(sum(scores) / len(scores), 1),
                "highest_score": max(scores),
                "latest_score": latest_assessment.total_score,  # Use the latest_assessment directly
                "lowest_score": min(scores),
                "improvement_trend": AssessmentService._calculate_improvement_trend([a.total_score for a in reversed(assessments)])  # Chronological for trend calculation
            }
            
            # Format line chart data
            line_chart = {
                "labels": [point.test_date for point in line_chart_data],
                "datasets": [{
                    "label": "MMSE Score",
                    "data": [point.total_score for point in line_chart_data],
                    "percentages": [point.percentage for point in line_chart_data],
                    "interpretations": [point.interpretation for point in line_chart_data],
                    "assessment_ids": [point.assessment_id for point in line_chart_data]
                }],
                "metadata": {
                    "total_tests": len(line_chart_data),
                    "max_possible_score": 27,
                    "date_range": {
                        "start": line_chart_data[0].test_date if line_chart_data else None,
                        "end": line_chart_data[-1].test_date if line_chart_data else None
                    }
                }
            }
            
            return MMSEChartData(
                success=True,
                user_id=user_id,
                test_name="MMSE Test (Mini Mental State Examination)",
                radar_chart=radar_chart_data,
                line_chart=line_chart,
                summary_stats=summary_stats
            )
            
        except Exception as e:
            logging.error(f"Error getting MMSE chart data: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def _create_radar_chart_data(assessment: UserAssessment) -> MMSERadarChartData:
        """Create radar chart data for a specific assessment"""
        
        # Section definitions with max scores
        section_definitions = [
            {"name": "Time and Space Orientation", "max_score": 8},
            {"name": "Memory Reception and Retention", "max_score": 3},
            {"name": "Attention / Calculation Performance", "max_score": 5},
            {"name": "Recent Memory", "max_score": 3},
            {"name": "Language", "max_score": 3},
            {"name": "Verbal Comprehension", "max_score": 2},
            {"name": "Written Comprehension", "max_score": 1},
            {"name": "Writing and Visual Skills", "max_score": 2}
        ]
        
        section_labels = [s["name"] for s in section_definitions]
        section_max_scores = [s["max_score"] for s in section_definitions]
        
        # Calculate section scores from detailed answers
        section_scores = [0] * len(section_definitions)
        
        # Get detailed answers for this assessment
        answers = db.session.query(AssessmentAnswer).filter(
            AssessmentAnswer.user_assessment_id == assessment.id
        ).all()
        
        # Get question details to map to sections  
        questions = db.session.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_type_id == 1
        ).all()
        
        # Build question to section mapping
        question_section_map = {}
        for q in questions:
            # Map based on question content or ID ranges
            if q.id <= 8:  # Questions 1-8: Time and Space Orientation
                question_section_map[q.id] = 0
            elif q.id == 9:  # Question 9: Memory Reception and Retention  
                question_section_map[q.id] = 1
            elif 10 <= q.id <= 14:  # Questions 10-14: Attention / Calculation Performance
                question_section_map[q.id] = 2
            elif q.id == 15:  # Question 15: Recent Memory
                question_section_map[q.id] = 3
            elif 16 <= q.id <= 18:  # Questions 16-18: Language
                question_section_map[q.id] = 4
            elif 19 <= q.id <= 20:  # Questions 19-20: Verbal Comprehension
                question_section_map[q.id] = 5
            elif q.id == 21:  # Question 21: Written Comprehension
                question_section_map[q.id] = 6
            elif 22 <= q.id <= 23:  # Questions 22-23: Writing and Visual Skills
                question_section_map[q.id] = 7
        
        # Sum points by section
        for answer in answers:
            if answer.question_id in question_section_map:
                section_idx = question_section_map[answer.question_id]
                points = answer.points_earned if answer.points_earned is not None else 0
                section_scores[section_idx] += points
        
        # If we don't have detailed answer data, use proportional fallback
        if sum(section_scores) == 0 and assessment.total_score > 0:
            logging.info(f"No detailed answers for assessment {assessment.id}, using proportional fallback")
            total_max = sum(section_max_scores)  # 27
            
            # Calculate proportional scores
            raw_scores = [(max_score / total_max) * assessment.total_score for max_score in section_max_scores]
            section_scores = [int(score) for score in raw_scores]
            
            # Adjust for exact total match
            current_total = sum(section_scores)
            difference = assessment.total_score - current_total
            
            if difference != 0:
                fractional_parts = [(raw_scores[i] - section_scores[i], i) for i in range(len(raw_scores))]
                fractional_parts.sort(reverse=True, key=lambda x: x[0])
                
                for i in range(abs(difference)):
                    if i < len(fractional_parts):
                        section_idx = fractional_parts[i][1]
                        if difference > 0:
                            section_scores[section_idx] += 1
                        else:
                            section_scores[section_idx] = max(0, section_scores[section_idx] - 1)
        
        # Calculate percentages
        section_percentages = []
        for i, score in enumerate(section_scores):
            max_score = section_max_scores[i]
            percentage = (score / max_score * 100) if max_score > 0 else 0
            section_percentages.append(round(percentage, 1))
        
        # Get interpretation
        interpretation = AssessmentService._get_interpretation(assessment.total_score)
        interpretation_text = interpretation.level if hasattr(interpretation, 'level') else str(interpretation)
        
        return MMSERadarChartData(
            assessment_id=assessment.id,
            test_date=assessment.completed_at.isoformat(),
            total_score=assessment.total_score,
            max_score=assessment.max_possible_score,
            percentage=float(assessment.percentage_score),
            interpretation=interpretation_text,
            section_labels=section_labels,
            section_scores=section_scores,
            section_max_scores=section_max_scores,
            section_percentages=section_percentages
        )
    
    @staticmethod
    def debug_radar_chart_data(user_id: int) -> Dict[str, Any]:
        """Debug method to check radar chart data generation"""
        try:
            # Get ALL assessments with detailed info - same query as chart-data
            assessments = db.session.query(UserAssessment).filter(
                UserAssessment.user_id == user_id,
                UserAssessment.assessment_type_id == 1,  # MMSE type
                UserAssessment.status == AssessmentStatusEnum.COMPLETED
            ).order_by(UserAssessment.completed_at.desc(), UserAssessment.id.desc()).all()  # Same ordering as chart-data
            
            if not assessments:
                return {"error": "No assessments found"}
            
            # Show ALL assessments for debugging (first 10 to avoid too much data)
            all_assessments_info = []
            for idx, assessment in enumerate(assessments[:10]):  # Show first 10 (latest first due to DESC order)
                all_assessments_info.append({
                    "index": idx,
                    "assessment_id": assessment.id,
                    "completed_at": assessment.completed_at.isoformat(),
                    "total_score": assessment.total_score,
                    "is_selected_as_latest": idx == 0  # First one should be selected as latest
                })
            
            # Get the supposed "latest" assessment (FIRST in DESC-ordered list)
            latest_assessment = assessments[0]  # First = most recent due to DESC ordering
            
            # Check database answers for latest assessment
            db_answers = db.session.query(AssessmentAnswer).filter(
                AssessmentAnswer.user_assessment_id == latest_assessment.id
            ).all()
            
            question_details = AssessmentService._get_question_details_for_assessment(latest_assessment.id)
            
            # Check if we have detailed data
            has_detailed_data = any(q.points_earned is not None and q.points_earned > 0 for q in question_details)
            
            # Test the radar chart creation for debugging
            radar_test_data = AssessmentService._create_radar_chart_data(latest_assessment)
            
            debug_info = {
                "user_id": user_id,
                "total_assessments_found": len(assessments),
                "all_assessments": all_assessments_info,
                "latest_assessment_logic": {
                    "selected_assessment_id": latest_assessment.id,
                    "selected_date": latest_assessment.completed_at.isoformat(),
                    "selected_score": latest_assessment.total_score,
                    "is_actually_latest": latest_assessment.completed_at == max(a.completed_at for a in assessments)
                },
                "database_answers": {
                    "count": len(db_answers),
                    "sample_answers": [
                        {
                            "id": ans.id,
                            "question_id": ans.question_id,
                            "user_answer": ans.user_answer,
                            "is_correct": ans.is_correct,
                            "points_earned": ans.points_earned
                        } for ans in db_answers[:5]
                    ] if db_answers else []
                },
                "processed_question_details": {
                    "count": len(question_details),
                    "has_detailed_data": has_detailed_data,
                    "sample_questions": [
                        {
                            "question_id": q.question_id,
                            "section_name": q.section_name,
                            "points_earned": q.points_earned,
                            "max_points": q.max_points,
                            "user_answer": q.user_answer
                        } for q in question_details[:5]
                    ]
                },
                "radar_chart_test": {
                    "section_scores": radar_test_data.section_scores,
                    "section_percentages": radar_test_data.section_percentages,
                    "fallback_should_trigger": not has_detailed_data and latest_assessment.total_score > 0,
                    "total_score_from_assessment": latest_assessment.total_score
                }
            }
            
            return debug_info
            
        except Exception as e:
            return {"error": str(e), "traceback": str(e.__class__.__name__)}
    
    @staticmethod
    def _calculate_improvement_trend(scores: List[int]) -> str:
        """Calculate improvement trend from score history"""
        if len(scores) < 2:
            return "insufficient_data"
        
        # Compare last 3 scores vs first 3 scores if available
        recent_count = min(3, len(scores))
        early_count = min(3, len(scores))
        
        recent_avg = sum(scores[-recent_count:]) / recent_count
        early_avg = sum(scores[:early_count]) / early_count
        
        difference = recent_avg - early_avg
        
        if difference >= 2:
            return "improving"
        elif difference <= -2:
            return "declining"  
        else:
            return "stable"
    
    @staticmethod
    def _get_db_question_id(question_id: str) -> int:
        """Map question identifier to database question ID"""
        # Reverse mapping of _get_question_id_from_db
        db_id_mapping = {
            "weekday": 1, "day": 2, "month": 3, "year": 4, "hour": 5,
            "city": 6, "hometown": 7, "country": 8, "memory_words": 9,
            "calc_1": 10, "calc_2": 11, "calc_3": 12, "calc_4": 13, "calc_5": 14,
            "recall_words": 15, "identify_pen": 16, "identify_clock": 17, "audio_topic": 18,
            "nose_instruction": 19, "ear_instruction": 20, "written_instruction": 21,
            "grammar_sentence": 22, "pentagon_shape": 23
        }
        
        return db_id_mapping.get(question_id, 1)