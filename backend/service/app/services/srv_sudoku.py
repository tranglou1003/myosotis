# app/services/srv_sudoku.py
from fastapi_sqlalchemy import db
from sqlalchemy import func, desc
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from app.models.model_sudoku import Sudoku, SudokuStatusEnum
from app.schemas.sche_sudoku import (
    SudokuCreateRequest, SudokuUpdateRequest, BoardResponse, 
    SudokuGameResponse, SudokuStatsResponse, MoveRequest
)
from app.utils.exception_handler import CustomException, ExceptionType
import logging

logger = logging.getLogger(__name__)


class SudokuService:
    def __init__(self, puzzle: str = None, solution: str = None, sudoku_id: int = None):
        """Initialize service with either new puzzle or existing game from DB"""
        if sudoku_id:
            self.sudoku = self.get_by_id(sudoku_id)
            self.board = self.str_to_board(self.sudoku.current_board)
            self.solution = self.str_to_board(self.sudoku.solution)
        elif puzzle and solution:
            self.puzzle_str = puzzle
            self.solution_str = solution
            self.board = self.str_to_board(puzzle)
            self.solution = self.str_to_board(solution)
            self.sudoku = None
        else:
            raise CustomException(ExceptionType.BAD_REQUEST, "Either sudoku_id or puzzle+solution required")

    def str_to_board(self, s: str) -> List[List[int]]:
        """Convert string to 2D board"""
        return [[int(s[i*9+j]) for j in range(9)] for i in range(9)]

    def board_to_str(self, board: List[List[int]]) -> str:
        """Convert 2D board to string"""
        return ''.join(str(cell) for row in board for cell in row)

    def is_valid_move(self, row: int, col: int, num: int) -> bool:
        """Check if move is valid according to Sudoku rules"""
        # Check if cell is already filled in original puzzle
        if self.sudoku:
            original_board = self.str_to_board(self.sudoku.original_puzzle)
            if original_board[row][col] != 0:
                return False
        
        # Check row
        for j in range(9):
            if j != col and self.board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if i != row and self.board[i][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.board[i][j] == num:
                    return False
        
        return True

    def is_completed(self) -> bool:
        """Check if puzzle is completed"""
        return self.board == self.solution

    def get_board(self) -> BoardResponse:
        """Get current board state"""
        completion_percentage = None
        sudoku_id = None
        valid_moves = 0
        invalid_moves = 0
        
        if self.sudoku:
            completion_percentage = self.sudoku.completion_percentage
            sudoku_id = self.sudoku.id
            valid_moves = self.sudoku.valid_moves
            invalid_moves = self.sudoku.invalid_moves
        
        return BoardResponse(
            board=self.board,
            message="Current board state",
            finished=self.is_completed(),
            valid_moves=valid_moves,
            invalid_moves=invalid_moves,
            sudoku_id=sudoku_id,
            completion_percentage=completion_percentage
        )

    def make_move(self, row: int, col: int, number: int) -> BoardResponse:
        """Make a single move"""
        if self.is_valid_move(row, col, number):
            self.board[row][col] = number
            
            if self.sudoku:
                self.sudoku.current_board = self.board_to_str(self.board)
                self.sudoku.moves_count += 1
                self.sudoku.valid_moves += 1
                
                # Check if completed
                if self.is_completed():
                    self.sudoku.status = SudokuStatusEnum.COMPLETED
                    self.sudoku.completion_time = datetime.utcnow()
                
                db.session.commit()
            
            return BoardResponse(
                board=self.board,
                message=f"Valid move: placed {number} at ({row}, {col})",
                finished=self.is_completed(),
                valid_moves=self.sudoku.valid_moves if self.sudoku else 1,
                invalid_moves=self.sudoku.invalid_moves if self.sudoku else 0,
                sudoku_id=self.sudoku.id if self.sudoku else None,
                completion_percentage=self.sudoku.completion_percentage if self.sudoku else None
            )
        else:
            if self.sudoku:
                self.sudoku.moves_count += 1
                self.sudoku.invalid_moves += 1
                db.session.commit()
            
            return BoardResponse(
                board=self.board,
                message=f"Invalid move: cannot place {number} at ({row}, {col})",
                finished=False,
                valid_moves=self.sudoku.valid_moves if self.sudoku else 0,
                invalid_moves=self.sudoku.invalid_moves if self.sudoku else 1,
                sudoku_id=self.sudoku.id if self.sudoku else None,
                completion_percentage=self.sudoku.completion_percentage if self.sudoku else None
            )

    def make_multiple_moves(self, moves: List[MoveRequest]) -> BoardResponse:
        """Make multiple moves"""
        valid_count = 0
        invalid_count = 0
        
        for move in moves:
            if self.is_valid_move(move.row, move.col, move.number):
                self.board[move.row][move.col] = move.number
                valid_count += 1
            else:
                invalid_count += 1
        
        if self.sudoku:
            self.sudoku.current_board = self.board_to_str(self.board)
            self.sudoku.moves_count += len(moves)
            self.sudoku.valid_moves += valid_count
            self.sudoku.invalid_moves += invalid_count
            
            if self.is_completed():
                self.sudoku.status = SudokuStatusEnum.COMPLETED
                self.sudoku.completion_time = datetime.utcnow()
            
            db.session.commit()
        
        return BoardResponse(
            board=self.board,
            message=f"Made {len(moves)} moves: {valid_count} valid, {invalid_count} invalid",
            finished=self.is_completed(),
            valid_moves=self.sudoku.valid_moves if self.sudoku else valid_count,
            invalid_moves=self.sudoku.invalid_moves if self.sudoku else invalid_count,
            sudoku_id=self.sudoku.id if self.sudoku else None,
            completion_percentage=self.sudoku.completion_percentage if self.sudoku else None
        )

    @staticmethod
    def create_game(user_id: int, puzzle: str, solution: str, req: SudokuCreateRequest = None) -> Sudoku:
        """Create new Sudoku game in database"""
        try:
            sudoku_data = {
                "user_id": user_id,
                "original_puzzle": puzzle,
                "solution": solution,
                "current_board": puzzle,
                "status": SudokuStatusEnum.IN_PROGRESS
            }
            
            if req:
                if req.puzzle_index is not None:
                    sudoku_data["puzzle_index"] = req.puzzle_index
                if req.difficulty:
                    sudoku_data["difficulty"] = req.difficulty
                if req.notes:
                    sudoku_data["notes"] = req.notes
            
            sudoku = Sudoku(**sudoku_data)
            db.session.add(sudoku)
            db.session.commit()
            db.session.refresh(sudoku)
            
            logger.info(f"Created Sudoku game {sudoku.id} for user {user_id}")
            return sudoku
        except Exception as e:
            logger.error(f"Error creating Sudoku game: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to create Sudoku game")

    @staticmethod
    def get_by_id(sudoku_id: int) -> Sudoku:
        """Get Sudoku game by ID"""
        try:
            sudoku = db.session.query(Sudoku).filter(Sudoku.id == sudoku_id).first()
            if not sudoku:
                raise CustomException(ExceptionType.NOT_FOUND, f"Sudoku game {sudoku_id} not found")
            return sudoku
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting Sudoku game {sudoku_id}: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to retrieve Sudoku game")

    @staticmethod
    def get_by_user(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[SudokuStatusEnum] = None,
        difficulty: Optional[str] = None
    ) -> Tuple[List[Sudoku], int]:
        """Get user's Sudoku games with filtering"""
        try:
            query = db.session.query(Sudoku).filter(Sudoku.user_id == user_id)
            
            if status:
                query = query.filter(Sudoku.status == status)
            if difficulty:
                query = query.filter(Sudoku.difficulty == difficulty)
            
            total = query.count()
            games = query.order_by(desc(Sudoku.created_at)).offset(skip).limit(limit).all()
            
            return games, total
        except Exception as e:
            logger.error(f"Error getting user {user_id} Sudoku games: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to retrieve Sudoku games")

    @staticmethod
    def update_game(sudoku_id: int, req: SudokuUpdateRequest) -> Sudoku:
        """Update Sudoku game"""
        try:
            sudoku = SudokuService.get_by_id(sudoku_id)
            
            update_data = req.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(sudoku, key, value)
            
            db.session.commit()
            logger.info(f"Updated Sudoku game {sudoku_id}")
            return sudoku
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating Sudoku game {sudoku_id}: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to update Sudoku game")

    @staticmethod
    def delete_game(sudoku_id: int, user_id: int) -> bool:
        """Delete Sudoku game (only by owner)"""
        try:
            sudoku = SudokuService.get_by_id(sudoku_id)
            
            if sudoku.user_id != user_id:
                raise CustomException(ExceptionType.FORBIDDEN, "You can only delete your own games")
            
            db.session.delete(sudoku)
            db.session.commit()
            
            logger.info(f"Deleted Sudoku game {sudoku_id}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error deleting Sudoku game {sudoku_id}: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to delete Sudoku game")

    @staticmethod
    def get_user_stats(user_id: int) -> SudokuStatsResponse:
        """Get user's Sudoku statistics"""
        try:
            query = db.session.query(Sudoku).filter(Sudoku.user_id == user_id)
            
            total_games = query.count()
            completed_games = query.filter(Sudoku.status == SudokuStatusEnum.COMPLETED).count()
            in_progress_games = query.filter(Sudoku.status == SudokuStatusEnum.IN_PROGRESS).count()
            abandoned_games = query.filter(Sudoku.status == SudokuStatusEnum.ABANDONED).count()
            
            # Total play time
            total_play_time = db.session.query(func.sum(Sudoku.total_play_time)).filter(
                Sudoku.user_id == user_id
            ).scalar() or 0
            
            # Average and best completion time (only for completed games)
            completed_query = query.filter(Sudoku.status == SudokuStatusEnum.COMPLETED)
            avg_completion = db.session.query(func.avg(Sudoku.total_play_time)).filter(
                Sudoku.user_id == user_id,
                Sudoku.status == SudokuStatusEnum.COMPLETED
            ).scalar()
            
            best_completion = db.session.query(func.min(Sudoku.total_play_time)).filter(
                Sudoku.user_id == user_id,
                Sudoku.status == SudokuStatusEnum.COMPLETED
            ).scalar()
            
            # Games by difficulty
            games_by_difficulty = dict(
                db.session.query(Sudoku.difficulty, func.count(Sudoku.id))
                .filter(Sudoku.user_id == user_id)
                .group_by(Sudoku.difficulty)
                .all()
            )
            
            # Completion rate
            completion_rate = (completed_games / total_games * 100) if total_games > 0 else 0
            
            # Format total play time
            hours = total_play_time // 3600
            minutes = (total_play_time % 3600) // 60
            seconds = total_play_time % 60
            total_play_time_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            return SudokuStatsResponse(
                total_games=total_games,
                completed_games=completed_games,
                in_progress_games=in_progress_games,
                abandoned_games=abandoned_games,
                total_play_time=total_play_time,
                total_play_time_formatted=total_play_time_formatted,
                average_completion_time=avg_completion,
                best_completion_time=best_completion,
                games_by_difficulty=games_by_difficulty,
                completion_rate=round(completion_rate, 2)
            )
        except Exception as e:
            logger.error(f"Error getting user {user_id} Sudoku stats: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to get Sudoku statistics")