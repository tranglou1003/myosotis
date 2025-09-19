export type SudokuCell = number | null;
export type SudokuGrid = SudokuCell[][];

export interface SudokuGameState {
  puzzle: SudokuGrid;
  solution: SudokuGrid;
  currentGrid: SudokuGrid;
  selectedCell: { row: number; col: number } | null;
  isCompleted: boolean;
  hasErrors: boolean;
  startTime: number;
  endTime: number | null;
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  hintsUsed: number;
  maxHints: number;
}

export interface SudokuCellProps {
  value: SudokuCell;
  isOriginal: boolean;
  isSelected: boolean;
  hasError: boolean;
  onSelect: () => void;
  onChange: (value: number | null) => void;
}

export interface SudokuStats {
  gamesPlayed: number;
  gamesCompleted: number;
  bestTime: number | null;
  totalTime: number;
  averageTime: number;
  streakCurrent: number;
  streakBest: number;
}

export interface SudokuDifficulty {
  name: 'easy' | 'medium' | 'hard' | 'expert';
  label: string;
  description: string;
  blanks: number;
}
