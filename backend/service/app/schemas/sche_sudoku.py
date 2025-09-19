# app/schemas/sche_sudoku.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.model_sudoku import SudokuStatusEnum


class MoveRequest(BaseModel):
    row: int = Field(..., ge=0, le=8, description="Hàng (0-8)")
    col: int = Field(..., ge=0, le=8, description="Cột (0-8)")
    number: int = Field(..., ge=1, le=9, description="Số cần điền (1-9)")


class MultipleMoveRequest(BaseModel):
    moves: List[MoveRequest] = Field(..., description="Danh sách các nước đi")


class BoardResponse(BaseModel):
    board: List[List[int]]
    message: str
    finished: bool
    valid_moves: int = Field(default=0, description="Số nước đi hợp lệ")
    invalid_moves: int = Field(default=0, description="Số nước đi không hợp lệ")
    sudoku_id: Optional[int] = Field(None, description="ID của game trong database")
    completion_percentage: Optional[float] = Field(None, description="Phần trăm hoàn thành")


class IndexCheckResponse(BaseModel):
    current_index: Optional[int] = Field(None, description="Index hiện tại của puzzle")
    message: str
    total_puzzles: int = Field(default=0, description="Tổng số puzzle có sẵn")


class SudokuCreateRequest(BaseModel):
    puzzle_index: Optional[int] = Field(None, description="Index của puzzle từ CSV")
    difficulty: Optional[str] = Field(None, description="Độ khó (easy, medium, hard, expert)")
    notes: Optional[str] = Field(None, description="Ghi chú của người chơi")


class SudokuUpdateRequest(BaseModel):
    status: Optional[SudokuStatusEnum] = None
    notes: Optional[str] = None
    total_play_time: Optional[int] = None
    hints_used: Optional[int] = None


class SudokuGameResponse(BaseModel):
    id: int
    user_id: int
    original_puzzle: str
    solution: str
    current_board: str
    puzzle_index: Optional[int]
    difficulty: str
    status: str
    moves_count: int
    valid_moves: int
    invalid_moves: int
    hints_used: int
    start_time: datetime
    completion_time: Optional[datetime]
    total_play_time: int
    play_time_formatted: str
    completion_percentage: float
    is_saved: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SudokuListResponse(BaseModel):
    games: List[SudokuGameResponse]
    total: int
    page: int
    per_page: int


class SudokuStatsResponse(BaseModel):
    total_games: int
    completed_games: int
    in_progress_games: int
    abandoned_games: int
    total_play_time: int
    total_play_time_formatted: str
    average_completion_time: Optional[float]
    best_completion_time: Optional[int]
    games_by_difficulty: dict
    completion_rate: float


class SaveGameRequest(BaseModel):
    save: bool = Field(True, description="Có lưu game này không")
    notes: Optional[str] = Field(None, description="Ghi chú khi lưu")