import React from 'react';

interface StatCardProps {
  icon: React.ReactNode;
  value: string | number;
  label: string;
  iconBgColor?: string;
  iconTextColor?: string;
  valueColor?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  icon,
  value,
  label,
  iconBgColor = 'bg-cyan-100',
  iconTextColor = 'text-cyan-700',
  valueColor = 'text-gray-900',
  onClick,
}) => {
  const containerClasses = onClick 
    ? 'flex items-center gap-4 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition-colors'
    : 'flex items-center gap-4';

  return (
    <div className={containerClasses} onClick={onClick}>
      <div className={`h-12 w-12 rounded-xl ${iconBgColor} ${iconTextColor} flex items-center justify-center shrink-0`}>
        {icon}
      </div>
      <div>
        <div className={`text-2xl font-semibold ${valueColor}`}>{value}</div>
        <div className="text-lg text-gray-600">{label}</div>
      </div>
    </div>
  );
};
