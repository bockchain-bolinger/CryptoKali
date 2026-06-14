import React from 'react';

export function ScoreBar({ score, showLabel = true }: { score: number, showLabel?: boolean }) {
  const percentage = Math.min(100, Math.max(0, score));
  return (
    <div className="score-bar-container">
      <div className="score-bar">
        <div className="score-bar-fill" style={{ width: `${100 - percentage}%` }}></div>
      </div>
      {showLabel && (
        <span style={{ 
          fontSize: '12px', 
          fontWeight: 600,
          color: percentage >= 75 ? 'var(--green)' : percentage >= 50 ? 'var(--yellow)' : 'var(--red)'
        }}>
          {Math.round(percentage)}
        </span>
      )}
    </div>
  );
}
