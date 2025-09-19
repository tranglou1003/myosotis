# app/api/api_sudoku.py
import os
import random
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.sche_sudoku import (
    MoveRequest, BoardResponse, MultipleMoveRequest, IndexCheckResponse,
    SudokuCreateRequest, SudokuUpdateRequest, SudokuGameResponse, 
    SudokuListResponse, SudokuStatsResponse, SaveGameRequest
)
from app.services.srv_sudoku import SudokuService
from app.models.model_sudoku import SudokuStatusEnum
from app.core.config import BASE_DIR

router = APIRouter()
csv_path = os.path.join(BASE_DIR, "app", "db", "sudoku_clean.csv")
df = pd.read_csv(csv_path)

# Global service instance for anonymous play (backward compatibility)
current_service = None
current_index = 0

# Anonymous gameplay routes (existing functionality)
@router.get("/board", response_model=BoardResponse)
def get_board():
    """Get current board state (anonymous play)"""
    global current_service
    if current_service is None:
        return get_random_board()
    return current_service.get_board()

@router.get("/board/random", response_model=BoardResponse)
def get_random_board():
    """Get a random sudoku puzzle from CSV (anonymous play)"""
    global current_service, current_index, df
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No puzzles available")
    
    current_index = random.randint(0, len(df) - 1)
    puzzle = df.loc[current_index, "quizzes"]
    solution = df.loc[current_index, "solutions"]
    
    current_service = SudokuService(puzzle, solution)
    
    response = current_service.get_board()
    response.message = f"Random board (Index: {current_index})"
    return response

@router.get("/board/index/{index}", response_model=BoardResponse)
def get_board_by_index(index: int):
    """Get sudoku puzzle by specific index (anonymous play)"""
    global current_service, current_index, df
    
    if index < 0 or index >= len(df):
        raise HTTPException(status_code=404, detail=f"Index {index} not found. Available: 0-{len(df)-1}")
    
    current_index = index
    puzzle = df.loc[index, "quizzes"]
    solution = df.loc[index, "solutions"]
    
    current_service = SudokuService(puzzle, solution)
    
    response = current_service.get_board()
    response.message = f"Board at index {index}"
    return response

@router.get("/current-index", response_model=IndexCheckResponse)
def check_current_index():
    """Check current puzzle index (anonymous play)"""
    global current_index, current_service
    
    if current_service is None:
        return IndexCheckResponse(
            current_index=None, 
            message="No puzzle loaded",
            total_puzzles=len(df)
        )
    
    return IndexCheckResponse(
        current_index=current_index,
        message=f"Current puzzle at index {current_index}",
        total_puzzles=len(df)
    )

@router.post("/move", response_model=BoardResponse)
def make_move(move: MoveRequest):
    """Make a single move (anonymous play)"""
    global current_service
    
    if current_service is None:
        raise HTTPException(status_code=400, detail="No puzzle loaded. Call /board/random first.")
    
    return current_service.make_move(move.row, move.col, move.number)

@router.post("/moves/batch", response_model=BoardResponse)
def make_multiple_moves(moves: MultipleMoveRequest):
    """Make multiple moves at once (anonymous play)"""
    global current_service
    
    if current_service is None:
        raise HTTPException(status_code=400, detail="No puzzle loaded. Call /board/random first.")
    
    return current_service.make_multiple_moves(moves.moves)

@router.post("/reset")
def reset_game():
    """Reset current game to initial state (anonymous play)"""
    global current_service, current_index, df
    
    if current_service is None:
        raise HTTPException(status_code=400, detail="No puzzle to reset")
    
    puzzle = df.loc[current_index, "quizzes"]
    solution = df.loc[current_index, "solutions"]
    current_service = SudokuService(puzzle, solution)
    
    return {"message": f"Game reset to initial state (Index: {current_index})"}

# Authenticated user routes - Modified to receive user_id directly
@router.post("/games/{user_id}", response_model=SudokuGameResponse)
def create_game(
    user_id: int,
    req: SudokuCreateRequest
):
    """Create new Sudoku game for user"""
    if req.puzzle_index is not None:
        if req.puzzle_index < 0 or req.puzzle_index >= len(df):
            raise HTTPException(status_code=404, detail=f"Invalid puzzle index: {req.puzzle_index}")
        puzzle = df.loc[req.puzzle_index, "quizzes"]
        solution = df.loc[req.puzzle_index, "solutions"]
    else:
        # Random puzzle
        index = random.randint(0, len(df) - 1)
        req.puzzle_index = index
        puzzle = df.loc[index, "quizzes"]
        solution = df.loc[index, "solutions"]
    
    sudoku = SudokuService.create_game(user_id, puzzle, solution, req)
    return SudokuGameResponse.from_orm(sudoku)

@router.get("/games/{user_id}", response_model=SudokuListResponse)
def get_user_games(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[SudokuStatusEnum] = None,
    difficulty: Optional[str] = None
):
    """Get user's Sudoku games with pagination and filtering"""
    games, total = SudokuService.get_by_user(
        user_id, skip, limit, status, difficulty
    )
    
    return SudokuListResponse(
        games=[SudokuGameResponse.from_orm(game) for game in games],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.get("/games/{user_id}/{sudoku_id}", response_model=SudokuGameResponse)
def get_game(
    user_id: int,
    sudoku_id: int
):
    """Get specific Sudoku game"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own games")
    
    return SudokuGameResponse.from_orm(sudoku)

@router.get("/games/{user_id}/{sudoku_id}/board", response_model=BoardResponse)
def get_game_board(
    user_id: int,
    sudoku_id: int
):
    """Get board state for specific game"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own games")
    
    service = SudokuService(sudoku_id=sudoku_id)
    return service.get_board()

@router.post("/games/{user_id}/{sudoku_id}/move", response_model=BoardResponse)
def make_game_move(
    user_id: int,
    sudoku_id: int,
    move: MoveRequest
):
    """Make a move in specific game"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only play your own games")
    
    if sudoku.status != SudokuStatusEnum.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Cannot make moves in completed/abandoned game")
    
    service = SudokuService(sudoku_id=sudoku_id)
    return service.make_move(move.row, move.col, move.number)

@router.post("/games/{user_id}/{sudoku_id}/moves/batch", response_model=BoardResponse)
def make_game_multiple_moves(
    user_id: int,
    sudoku_id: int,
    moves: MultipleMoveRequest
):
    """Make multiple moves in specific game"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only play your own games")
    
    if sudoku.status != SudokuStatusEnum.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Cannot make moves in completed/abandoned game")
    
    service = SudokuService(sudoku_id=sudoku_id)
    return service.make_multiple_moves(moves.moves)

@router.put("/games/{user_id}/{sudoku_id}", response_model=SudokuGameResponse)
def update_game(
    user_id: int,
    sudoku_id: int,
    req: SudokuUpdateRequest
):
    """Update Sudoku game (status, notes, etc.)"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own games")
    
    updated_sudoku = SudokuService.update_game(sudoku_id, req)
    return SudokuGameResponse.from_orm(updated_sudoku)

@router.delete("/games/{user_id}/{sudoku_id}")
def delete_game(
    user_id: int,
    sudoku_id: int
):
    """Delete Sudoku game"""
    success = SudokuService.delete_game(sudoku_id, user_id)
    
    if success:
        return {"message": f"Sudoku game {sudoku_id} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete game")

@router.post("/games/{user_id}/{sudoku_id}/reset", response_model=BoardResponse)
def reset_game_to_start(
    user_id: int,
    sudoku_id: int
):
    """Reset game to initial state"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only reset your own games")
    
    # Reset board to original puzzle
    sudoku.current_board = sudoku.original_puzzle
    sudoku.status = SudokuStatusEnum.IN_PROGRESS
    sudoku.moves_count = 0
    sudoku.valid_moves = 0
    sudoku.invalid_moves = 0
    sudoku.completion_time = None
    
    from fastapi_sqlalchemy import db
    db.session.commit()
    
    service = SudokuService(sudoku_id=sudoku_id)
    response = service.get_board()
    response.message = f"Game {sudoku_id} reset to initial state"
    return response

@router.get("/stats/{user_id}", response_model=SudokuStatsResponse)
def get_user_stats(user_id: int):
    """Get user's Sudoku statistics"""
    return SudokuService.get_user_stats(user_id)

@router.post("/games/{user_id}/{sudoku_id}/save", response_model=SudokuGameResponse)
def save_game(
    user_id: int,
    sudoku_id: int,
    req: SaveGameRequest
):
    """Save/unsave game"""
    sudoku = SudokuService.get_by_id(sudoku_id)
    
    if sudoku.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only save your own games")
    
    sudoku.is_saved = req.save
    if req.notes:
        sudoku.notes = req.notes
    
    from fastapi_sqlalchemy import db
    db.session.commit()
    
    return SudokuGameResponse.from_orm(sudoku)