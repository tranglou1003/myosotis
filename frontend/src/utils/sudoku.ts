import { getSudoku } from 'sudoku-gen';
import type { SudokuGrid, SudokuCell, SudokuDifficulty } from '../types/sudoku';

export const SUDOKU_DIFFICULTIES: SudokuDifficulty[] = [
  {
    name: 'easy',
    label: 'Easy',
    description: 'Perfect for beginners',
    blanks: 36
  },
  {
    name: 'medium',
    label: 'Medium', 
    description: 'A moderate challenge',
    blanks: 46
  },
  {
    name: 'hard',
    label: 'Hard',
    description: 'For experienced players',
    blanks: 52
  },
  {
    name: 'expert',
    label: 'Expert',
    description: 'The ultimate challenge',
    blanks: 58
  }
];

export const parseGrid = (gridString: string): SudokuGrid => {
  const grid: SudokuGrid = [];
  for (let i = 0; i < 9; i++) {
    const row: SudokuCell[] = [];
    for (let j = 0; j < 9; j++) {
      const char = gridString[i * 9 + j];
      row.push(char === '-' ? null : parseInt(char, 10));
    }
    grid.push(row);
  }
  return grid;
};

export const generateSudokuPuzzle = (difficulty: 'easy' | 'medium' | 'hard' | 'expert') => {
  const generated = getSudoku(difficulty);
  
  return {
    puzzle: parseGrid(generated.puzzle),
    solution: parseGrid(generated.solution)
  };
};

export const cloneGrid = (grid: SudokuGrid): SudokuGrid => {
  return grid.map(row => [...row]);
};

export const isValidMove = (grid: SudokuGrid, row: number, col: number, num: number): boolean => {
  for (let j = 0; j < 9; j++) {
    if (j !== col && grid[row][j] === num) {
      return false;
    }
  }

  for (let i = 0; i < 9; i++) {
    if (i !== row && grid[i][col] === num) {
      return false;
    }
  }

  const boxRow = Math.floor(row / 3) * 3;
  const boxCol = Math.floor(col / 3) * 3;
  
  for (let i = boxRow; i < boxRow + 3; i++) {
    for (let j = boxCol; j < boxCol + 3; j++) {
      if ((i !== row || j !== col) && grid[i][j] === num) {
        return false;
      }
    }
  }

  return true;
};

export const isPuzzleComplete = (grid: SudokuGrid): boolean => {
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      if (grid[i][j] === null) {
        return false;
      }
    }
  }
  return true;
};

export const hasGridErrors = (grid: SudokuGrid): boolean => {
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      const value = grid[i][j];
      if (value !== null && !isValidMove(grid, i, j, value)) {
        return true;
      }
    }
  }
  return false;
};

export const hasCellError = (grid: SudokuGrid, row: number, col: number): boolean => {
  const value = grid[row][col];
  if (value === null) return false;
  return !isValidMove(grid, row, col, value);
};

export const getHint = (grid: SudokuGrid): { row: number; col: number; value: number } | null => {
  for (let i = 0; i < 9; i++) {
    for (let j = 0; j < 9; j++) {
      if (grid[i][j] === null) {
        const possibleValues = [];
        for (let num = 1; num <= 9; num++) {
          if (isValidMove(grid, i, j, num)) {
            possibleValues.push(num);
          }
        }
        if (possibleValues.length === 1) {
          return { row: i, col: j, value: possibleValues[0] };
        }
      }
    }
  }
  return null;
};

export const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
