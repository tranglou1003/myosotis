export type PictureRecallDifficulty = 3 | 4 | 5;

export interface PictureRecallCard {
  id: string;
  imageUrl: string;
  isFlipped: boolean;
  isMatched: boolean;
  pairId: string;
}

export interface PictureRecallGameState {
  cards: PictureRecallCard[];
  selectedCards: PictureRecallCard[];
  matchedPairs: number;
  totalPairs: number;
  moves: number;
  isGameComplete: boolean;
  difficulty: PictureRecallDifficulty;
  gameMode: 'flags' | 'things';
  showPreview: boolean;
  previewTime: number;
  startTime: number | null;
  endTime: number | null;
}

export interface PictureRecallStats {
  gamesPlayed: number;
  gamesCompleted: number;
  bestMoves: Record<PictureRecallDifficulty, number | null>;
  bestTime: Record<PictureRecallDifficulty, number | null>;
  averageMoves: Record<PictureRecallDifficulty, number>;
  totalTime: number;
}

export interface GameImages {
  flags: string[];
  things: string[];
}
