import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ size = 'md' }: { size?: 'sm'|'md'|'lg' }) {
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 32
  };
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Loader2 
        size={sizeMap[size]} 
        color="var(--accent-indigo)" 
        style={{ animation: 'spin 1s linear infinite' }} 
      />
    </div>
  );
}
