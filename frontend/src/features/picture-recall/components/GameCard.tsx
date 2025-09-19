import React from 'react';
import { useTranslation } from 'react-i18next';
import type { PictureRecallCard } from '../../../types/picture-recall';

interface GameCardProps {
  card: PictureRecallCard;
  onFlip: (cardId: string) => void;
  disabled: boolean;
}

export const GameCard: React.FC<GameCardProps> = ({ card, onFlip, disabled }) => {
  const { t } = useTranslation('miniGames');
  
  const handleClick = () => {
    if (!disabled && !card.isFlipped && !card.isMatched) {
      onFlip(card.id);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`
        relative w-full aspect-square rounded-lg cursor-pointer transition-all duration-300 transform
        ${card.isMatched ? 'scale-105 ring-2 ring-gray-400' : ''}
        ${!card.isFlipped && !card.isMatched ? 'hover:scale-105' : ''}
        ${disabled || card.isMatched ? 'cursor-not-allowed' : ''}
      `}
    >
      <div
        className={`
          absolute inset-0 rounded-lg bg-gray-600 
          flex items-center justify-center transition-opacity duration-300
          ${card.isFlipped ? 'opacity-0' : 'opacity-100'}
        `}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="white" viewBox="0 0 16 16">
          <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286m1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94"/>
        </svg>
      </div>

      <div
        className={`
          absolute inset-0 rounded-lg bg-gray-50 border-2 border-gray-300 
          flex items-center justify-center p-2 transition-opacity duration-300
          ${card.isFlipped ? 'opacity-100' : 'opacity-0'}
          ${card.isMatched ? 'border-gray-500 bg-gray-100' : ''}
        `}
      >
        {card.isFlipped && (
          <div className="w-full h-full bg-gray-200 rounded border border-gray-300 p-2">
            <img
              src={card.imageUrl}
              alt={t('pictureRecall.accessibility.cardAlt')}
              className="w-full h-full object-contain rounded"
              draggable={false}
            />
          </div>
        )}
      </div>

      {card.isMatched && (
        <div className="absolute top-2 -right-2 bg-gray-700 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">
          ✓
        </div>
      )}
    </div>
  );
};
