import React from 'react';

export function FearGreedGauge({ value }: { value: number }) {
  const percentage = Math.min(100, Math.max(0, value));
  
  let color = 'var(--yellow)';
  let label = 'Neutral';
  
  if (value < 25) { color = 'var(--red)'; label = 'Extreme Fear'; }
  else if (value < 45) { color = 'var(--orange)'; label = 'Fear'; }
  else if (value > 75) { color = 'var(--green)'; label = 'Extreme Greed'; }
  else if (value > 55) { color = 'var(--accent-emerald)'; label = 'Greed'; }

  const rotation = (percentage / 100) * 180 - 90;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '10px' }}>
      <div style={{ 
        position: 'relative', 
        width: '160px', 
        height: '80px', 
        overflow: 'hidden',
        marginBottom: '10px'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '160px',
          height: '160px',
          borderRadius: '50%',
          border: '15px solid rgba(255,255,255,0.05)',
          borderBottomColor: 'transparent',
          borderRightColor: 'transparent',
          transform: 'rotate(-45deg)',
          boxSizing: 'border-box'
        }}></div>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '160px',
          height: '160px',
          borderRadius: '50%',
          border: `15px solid ${color}`,
          borderBottomColor: 'transparent',
          borderRightColor: 'transparent',
          transform: `rotate(${rotation - 45}deg)`,
          transition: 'transform 1s ease-out, border-color 1s',
          boxSizing: 'border-box'
        }}></div>
        <div style={{
          position: 'absolute',
          bottom: '0',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: '32px',
          fontWeight: 800,
          color: color,
          textShadow: `0 0 20px ${color}40`
        }}>
          {value}
        </div>
      </div>
      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)' }}>
        {label}
      </div>
    </div>
  );
}
