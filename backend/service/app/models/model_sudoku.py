# app/models/model_sudoku.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.model_base import BareBaseModel, Base
from enum import Enum


class SudokuStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Sudoku(BareBaseModel):
    __tablename__ = "sudokus"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Puzzle data
    original_puzzle = Column(Text, nullable=False, comment="81-character string representing original puzzle")
    solution = Column(Text, nullable=False, comment="81-character string representing complete solution")
    current_board = Column(Text, nullable=False, comment="81-character string representing current game state")
    
    # Game metadata
    puzzle_index = Column(Integer, nullable=True, comment="Index from CSV file if applicable")
    difficulty = Column(String(20), nullable=True, comment="Puzzle difficulty level (easy, medium, hard, expert)")
    status = Column(String(20), default=SudokuStatusEnum.IN_PROGRESS, comment="Current game status")
    
    # Game statistics
    moves_count = Column(Integer, default=0, comment="Total number of moves made")
    valid_moves = Column(Integer, default=0, comment="Number of valid moves")
    invalid_moves = Column(Integer, default=0, comment="Number of invalid moves")
    hints_used = Column(Integer, default=0, comment="Number of hints used")
    
    # Time tracking
    start_time = Column(DateTime(timezone=True), server_default=func.now(), comment="When game started")
    completion_time = Column(DateTime(timezone=True), nullable=True, comment="When game was completed")
    total_play_time = Column(Integer, default=0, comment="Total play time in seconds")
    
    # Game settings
    is_saved = Column(Boolean, default=True, comment="Whether this game is saved for later")
    notes = Column(Text, nullable=True, comment="Player notes or comments")
    
    
    # Relationships
    user = relationship("User", back_populates="sudoku_games")

    def __repr__(self):
        return f"<Sudoku(id={self.id}, user_id={self.user_id}, status={self.status})>"

    @property
    def is_completed(self):
        """Check if the game is completed"""
        return self.status == SudokuStatusEnum.COMPLETED

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on filled cells"""
        if not self.current_board:
            return 0
        filled_cells = sum(1 for c in self.current_board if c != '0')
        return round((filled_cells / 81) * 100, 2)

    @property
    def play_time_formatted(self):
        """Format play time as HH:MM:SS"""
        if not self.total_play_time:
            return "00:00:00"
        hours = self.total_play_time // 3600
        minutes = (self.total_play_time % 3600) // 60
        seconds = self.total_play_time % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"