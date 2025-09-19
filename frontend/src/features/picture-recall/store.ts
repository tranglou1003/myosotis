import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { 
  PictureRecallGameState, 
  PictureRecallStats, 
  PictureRecallDifficulty 
} from '../../types/picture-recall';
import { generateCards, cardsMatch, PREVIEW_TIMES } from '../../utils/picture-recall';

interface PictureRecallState extends PictureRecallGameState {
  stats: PictureRecallStats;
  previewInterval: NodeJS.Timeout | null;
}

interface PictureRecallActions {
  newGame: (difficulty: PictureRecallDifficulty, gameMode: 'flags' | 'things') => void;
  flipCard: (cardId: string) => void;
  resetGame: () => void;
  clearStats: () => void;
  updateStats: (completed: boolean, moves: number, timeSpent: number) => void;
  cleanup: () => void;
}

interface PictureRecallStore extends PictureRecallState, PictureRecallActions {}

const initialGameState: PictureRecallGameState = {
  cards: [],
  selectedCards: [],
  matchedPairs: 0,
  totalPairs: 0,
  moves: 0,
  isGameComplete: false,
  difficulty: 3,
  gameMode: 'flags',
  showPreview: false,
  previewTime: 0,
  startTime: null,
  endTime: null
};

const initialStats: PictureRecallStats = {
  gamesPlayed: 0,
  gamesCompleted: 0,
  bestMoves: { 3: null, 4: null, 5: null },
  bestTime: { 3: null, 4: null, 5: null },
  averageMoves: { 3: 0, 4: 0, 5: 0 },
  totalTime: 0
};

export const usePictureRecallStore = create<PictureRecallStore>()(
  persist(
    (set, get) => ({
      ...initialGameState,
      stats: initialStats,
      previewInterval: null,

      newGame: (difficulty: PictureRecallDifficulty, gameMode: 'flags' | 'things') => {
        
        const currentState = get();
        if (currentState.previewInterval) {
          clearInterval(currentState.previewInterval);
        }

        const cards = generateCards(difficulty, gameMode);
        const totalPairs = difficulty;
        const previewTime = PREVIEW_TIMES[difficulty];
        
        set({
          cards: cards.map(card => ({ ...card, isFlipped: true })), 
          selectedCards: [],
          matchedPairs: 0,
          totalPairs,
          moves: 0,
          isGameComplete: false,
          difficulty,
          gameMode,
          showPreview: true,
          previewTime,
          startTime: null,
          endTime: null,
          previewInterval: null
        });

        
        const countdown = setInterval(() => {
          const currentState = get();
          if (currentState.previewTime > 1) {
            set({ previewTime: currentState.previewTime - 1 });
          } else {
            
            set({
              cards: currentState.cards.map(card => ({ ...card, isFlipped: false })),
              showPreview: false,
              previewTime: 0,
              startTime: Date.now(),
              previewInterval: null
            });
            clearInterval(countdown);
          }
        }, 1000);

        
        set({ previewInterval: countdown });
      },

      flipCard: (cardId: string) => {
        const { cards, selectedCards, showPreview, startTime } = get();
        
        
        if (showPreview || !startTime) return;
        
        
        const card = cards.find(c => c.id === cardId);
        if (!card || card.isFlipped || card.isMatched) return;
        
        
        if (selectedCards.length >= 2) return;

        
        const updatedCards = cards.map(c => 
          c.id === cardId ? { ...c, isFlipped: true } : c
        );
        
        const newSelectedCards = [...selectedCards, { ...card, isFlipped: true }];
        
        set({ 
          cards: updatedCards, 
          selectedCards: newSelectedCards 
        });

        
        if (newSelectedCards.length === 2) {
          const [card1, card2] = newSelectedCards;
          const isMatch = cardsMatch(card1, card2);
          
          setTimeout(() => {
            const currentState = get();
            const newMoves = currentState.moves + 1;
            
            if (isMatch) {
              
              const matchedCards = currentState.cards.map(c => 
                c.pairId === card1.pairId ? { ...c, isMatched: true } : c
              );
              
              const newMatchedPairs = currentState.matchedPairs + 1;
              const isGameComplete = newMatchedPairs === currentState.totalPairs;
              
              set({
                cards: matchedCards,
                selectedCards: [],
                matchedPairs: newMatchedPairs,
                moves: newMoves,
                isGameComplete,
                endTime: isGameComplete ? Date.now() : null
              });

              
              if (isGameComplete && currentState.startTime) {
                const timeSpent = Math.floor((Date.now() - currentState.startTime) / 1000);
                get().updateStats(true, newMoves, timeSpent);
              }
            } else {
              
              const resetCards = currentState.cards.map(c => 
                (c.id === card1.id || c.id === card2.id) ? { ...c, isFlipped: false } : c
              );
              
              set({
                cards: resetCards,
                selectedCards: [],
                moves: newMoves
              });
            }
          }, 1000); 
        }
      },

      resetGame: () => {
        const { difficulty, gameMode } = get();
        get().newGame(difficulty, gameMode);
      },

      updateStats: (completed: boolean, moves: number, timeSpent: number) => {
        const { stats, difficulty } = get();
        
        const newStats: PictureRecallStats = {
          gamesPlayed: stats.gamesPlayed + 1,
          gamesCompleted: completed ? stats.gamesCompleted + 1 : stats.gamesCompleted,
          bestMoves: {
            ...stats.bestMoves,
            [difficulty]: stats.bestMoves[difficulty] === null || moves < stats.bestMoves[difficulty]! 
              ? moves : stats.bestMoves[difficulty]
          },
          bestTime: {
            ...stats.bestTime,
            [difficulty]: completed && (stats.bestTime[difficulty] === null || timeSpent < stats.bestTime[difficulty]!)
              ? timeSpent : stats.bestTime[difficulty]
          },
          averageMoves: {
            ...stats.averageMoves,
            [difficulty]: Math.floor(((stats.averageMoves[difficulty] * (stats.gamesPlayed || 1)) + moves) / (stats.gamesPlayed + 1))
          },
          totalTime: stats.totalTime + timeSpent
        };

        set({ stats: newStats });
      },

      clearStats: () => {
        set({ stats: initialStats });
      },

      cleanup: () => {
        const currentState = get();
        if (currentState.previewInterval) {
          clearInterval(currentState.previewInterval);
          set({ previewInterval: null });
        }
      }
    }),
    {
      name: 'picture-recall-storage',
      partialize: (state) => ({
        stats: state.stats
      })
    }
  )
);
