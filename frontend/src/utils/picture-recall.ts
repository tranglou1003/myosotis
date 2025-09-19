import type { PictureRecallCard, PictureRecallDifficulty, GameImages } from '../types/picture-recall';

export const GAME_IMAGES: GameImages = {
  flags: [
    '/recall/flags/china_texture.gif',
    '/recall/flags/russia_texture.gif', 
    '/recall/flags/singapore_texture.gif',
    '/recall/flags/thailand_texture.gif',
    '/recall/flags/vietnam_texture.gif'
  ],
  things: [
    '/recall/things/football.png',
    '/recall/things/guitar.png',
    '/recall/things/key.png',
    '/recall/things/socks.png',
    '/recall/things/tv.png'
  ]
};

export const PREVIEW_TIMES: Record<PictureRecallDifficulty, number> = {
  3: 5,
  4: 5,
  5: 10  
};

export const shuffleArray = <T>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

export const generateCards = (
  difficulty: PictureRecallDifficulty, 
  gameMode: 'flags' | 'things'
): PictureRecallCard[] => {
  const images = GAME_IMAGES[gameMode];
  const selectedImages = images.slice(0, difficulty);
  
  const cards: PictureRecallCard[] = [];
  selectedImages.forEach((imageUrl, index) => {
    const pairId = `pair-${index}`;
    
    cards.push({
      id: `${pairId}-1`,
      imageUrl,
      isFlipped: false,
      isMatched: false,
      pairId
    });
    
    cards.push({
      id: `${pairId}-2`, 
      imageUrl,
      isFlipped: false,
      isMatched: false,
      pairId
    });
  });
  
  return shuffleArray(cards);
};

export const cardsMatch = (card1: PictureRecallCard, card2: PictureRecallCard): boolean => {
  return card1.pairId === card2.pairId && card1.id !== card2.id;
};

export const getGridLayout = (difficulty: PictureRecallDifficulty): { cols: number; rows: number } => {
  switch (difficulty) {
    case 3: return { cols: 3, rows: 2 };
    case 4: return { cols: 4, rows: 2 };
    case 5: return { cols: 5, rows: 2 };
    default: return { cols: 3, rows: 2 };
  }
};


export const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
