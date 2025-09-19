from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.sche_response import DataResponse
from app.schemas.sche_assessment import (
    MMSEHistoryItemDetailed, MMSEHistorySummary, MMSESubmitRequest, MMSEResult, MMSEHistoryItem, MMSETestStructure, MMSEChartData
)
from app.services.srv_assessment import AssessmentService
from app.utils.exception_handler import CustomException, ExceptionType
from app.db.session import get_db

router = APIRouter(prefix="/assessments")

@router.get("/mmse/infor", response_model=DataResponse[MMSETestStructure])
def get_mmse_test_optimized() -> Any:
    """Get  dữ liệu bài test MMSE"""
    try:
        test_structure = AssessmentService.get_mmse_test_optimized()
        return DataResponse(http_code=200, data=test_structure)
    except Exception as e:
        raise CustomException(exception=e)


@router.post("/mmse/submit", response_model=DataResponse[MMSEResult])
def submit_mmse_test(
    request: MMSESubmitRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Submit bài test và tính điểm"""
    try:
        # Use user_id from request
        result = AssessmentService.submit_mmse_test(
            user_id=request.user_id,
            answers=request.answers
        )
        return DataResponse(http_code=200, data=result)
    except Exception as e:
        raise CustomException(exception=e)


@router.get("/mmse/history", response_model=DataResponse[List[MMSEHistoryItem]])
def get_mmse_history(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get lịch sử làm test của user"""
    try:
        # Use user_id from query parameter
        history = AssessmentService.get_mmse_history(user_id=user_id)
        return DataResponse(http_code=200, data=history)
    except Exception as e:
        raise CustomException(exception=e)
@router.get("/mmse/history/detailed", response_model=DataResponse[List[MMSEHistoryItemDetailed]])
def get_mmse_history_detailed(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get detailed MMSE history with question-level breakdown"""
    try:
        history = AssessmentService.get_mmse_history_detailed(user_id=user_id)
        return DataResponse(http_code=200, data=history)
    except Exception as e:
        raise CustomException(exception=e)


# Keep the original endpoint for backward compatibility
@router.get("/mmse/history", response_model=DataResponse[List[MMSEHistoryItem]])
def get_mmse_history(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get basic MMSE history (legacy endpoint)"""
    try:
        history = AssessmentService.get_mmse_history(user_id=user_id)
        return DataResponse(http_code=200, data=history)
    except Exception as e:
        raise CustomException(exception=e)

@router.get("/mmse/history/summary", response_model=DataResponse[MMSEHistorySummary])
def get_mmse_history_summary(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get summary of MMSE history for a user"""
    try:
        summary = AssessmentService.get_mmse_history_summary(user_id=user_id)
        return DataResponse(http_code=200, data=summary)
    except Exception as e:
        raise CustomException(exception=e)
    
@router.get("/mmse/chart-data", response_model=DataResponse[MMSEChartData])
def get_mmse_chart_data(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Get chart data for MMSE visualization - radar chart and line chart"""
    try:
        chart_data = AssessmentService.get_mmse_chart_data(user_id=user_id)
        return DataResponse(http_code=200, data=chart_data)
    except Exception as e:
        raise CustomException(exception=e)


@router.get("/mmse/debug-radar", response_model=DataResponse[Any])
def debug_mmse_radar_data(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Debug endpoint to check radar chart data generation"""
    try:
        debug_info = AssessmentService.debug_radar_chart_data(user_id=user_id)
        return DataResponse(http_code=200, data=debug_info)
    except Exception as e:
        raise CustomException(exception=e)