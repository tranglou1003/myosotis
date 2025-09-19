import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SudokuGameState, SudokuStats } from '../../types/sudoku';
import { generateSudokuPuzzle, cloneGrid, isPuzzleComplete, hasGridErrors, getHint } from '../../utils/sudoku';

interface SudokuState extends SudokuGameState {
  stats: SudokuStats;
}

interface SudokuActions {
  newGame: (difficulty: 'easy' | 'medium' | 'hard' | 'expert') => void;
  selectCell: (row: number, col: number) => void;
  setCellValue: (row: number, col: number, value: number | null) => void;
  clearCell: () => void;
  resetGame: () => void;
  completeGame: () => void;
  clearStats: () => void;
  updateStats: (completed: boolean, timeSpent: number) => void;
  getHint: () => boolean;
}

interface SudokuStore extends SudokuState, SudokuActions {}

const initialGameState: SudokuGameState = {
  puzzle: Array(9).fill(null).map(() => Array(9).fill(null)),
  solution: Array(9).fill(null).map(() => Array(9).fill(null)),
  currentGrid: Array(9).fill(null).map(() => Array(9).fill(null)),
  selectedCell: null,
  isCompleted: false,
  hasErrors: false,
  startTime: Date.now(),
  endTime: null,
  difficulty: 'easy',
  hintsUsed: 0,
  maxHints: 5
};

const initialStats: SudokuStats = {
  gamesPlayed: 0,
  gamesCompleted: 0,
  bestTime: null,
  totalTime: 0,
  averageTime: 0,
  streakCurrent: 0,
  streakBest: 0
};

export const useSudokuStore = create<SudokuStore>()(
  persist(
    (set, get) => ({
      ...initialGameState,
      stats: initialStats,

      newGame: (difficulty: 'easy' | 'medium' | 'hard' | 'expert') => {
        const { puzzle, solution } = generateSudokuPuzzle(difficulty);
        const currentGrid = cloneGrid(puzzle);
        
        set({
          puzzle,
          solution,
          currentGrid,
          selectedCell: null,
          isCompleted: false,
          hasErrors: false,
          startTime: Date.now(),
          endTime: null,
          difficulty,
          hintsUsed: 0,
          maxHints: 5
        });
      },

      selectCell: (row: number, col: number) => {
        set({ selectedCell: { row, col } });
      },

      setCellValue: (row: number, col: number, value: number | null) => {
        const { currentGrid, puzzle } = get();
        
        if (puzzle[row][col] !== null) return;

        const newGrid = cloneGrid(currentGrid);
        newGrid[row][col] = value;

        const isCompleted = isPuzzleComplete(newGrid);
        const hasErrors = hasGridErrors(newGrid);

        set({
          currentGrid: newGrid,
          hasErrors,
          isCompleted,
          endTime: isCompleted ? Date.now() : null
        });

        // Update stats if game is completed
        if (isCompleted && !get().isCompleted) {
          const timeSpent = Math.floor((Date.now() - get().startTime) / 1000);
          get().updateStats(true, timeSpent);
        }
      },

      clearCell: () => {
        const { selectedCell } = get();
        if (selectedCell) {
          get().setCellValue(selectedCell.row, selectedCell.col, null);
        }
      },

      resetGame: () => {
        const { puzzle } = get();
        set({
          currentGrid: cloneGrid(puzzle),
          selectedCell: null,
          isCompleted: false,
          hasErrors: false,
          startTime: Date.now(),
          endTime: null,
          hintsUsed: 0
        });
      },

      getHint: () => {
        const { currentGrid, hintsUsed, maxHints } = get();
        
        if (hintsUsed >= maxHints) {
          return false;
        }

        const hint = getHint(currentGrid);
        if (hint) {
          get().setCellValue(hint.row, hint.col, hint.value);
          set({ hintsUsed: hintsUsed + 1 });
          return true;
        }
        
        return false;
      },

      completeGame: () => {
        set({
          isCompleted: true,
          endTime: Date.now()
        });
      },

      updateStats: (completed: boolean, timeSpent: number) => {
        const { stats } = get();
        
        const newStats: SudokuStats = {
          gamesPlayed: stats.gamesPlayed + 1,
          gamesCompleted: completed ? stats.gamesCompleted + 1 : stats.gamesCompleted,
          bestTime: completed && (stats.bestTime === null || timeSpent < stats.bestTime) 
            ? timeSpent 
            : stats.bestTime,
          totalTime: stats.totalTime + timeSpent,
          averageTime: Math.floor((stats.totalTime + timeSpent) / (stats.gamesPlayed + 1)),
          streakCurrent: completed ? stats.streakCurrent + 1 : 0,
          streakBest: completed && stats.streakCurrent + 1 > stats.streakBest 
            ? stats.streakCurrent + 1 
            : stats.streakBest
        };

        set({ stats: newStats });
      },

      clearStats: () => {
        set({ stats: initialStats });
      }
    }),
    {
      name: 'sudoku-storage',
      partialize: (state) => ({
        stats: state.stats
      })
    }
  )
);
