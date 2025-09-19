import React from 'react';
import type { SudokuCellProps } from '../types/sudoku';

export const SudokuCell: React.FC<SudokuCellProps> = ({
  value,
  isOriginal,
  isSelected,
  hasError,
  onSelect,
  onChange
}) => {
  const handleClick = () => {
    onSelect();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (isOriginal) return;

    const key = e.key;
    
    if (key >= '1' && key <= '9') {
      const num = parseInt(key, 10);
      onChange(num);
    } else if (key === 'Backspace' || key === 'Delete' || key === ' ') {
      onChange(null);
    }
  };

  return (
    <div
      className={`
        w-12 h-12 border border-gray-300 flex items-center justify-center cursor-pointer
        text-lg font-semibold transition-all duration-200
        ${isSelected ? 'bg-blue-200 border-blue-500 ring-2 ring-blue-300' : 'hover:bg-gray-100'}
        ${isOriginal ? 'bg-gray-50 text-gray-900' : 'bg-white text-blue-700'}
        ${hasError ? 'bg-red-100 text-red-700 border-red-400' : ''}
        ${isOriginal ? 'cursor-default' : 'cursor-pointer'}
      `}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`Cell ${value || 'empty'}${isOriginal ? ' (original)' : ''}`}
    >
      {value || ''}
    </div>
  );
};
