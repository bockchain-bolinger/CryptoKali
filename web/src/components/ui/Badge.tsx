import React from 'react';

export function Badge({ children, variant = 'blue' }: { children: React.ReactNode, variant?: 'green'|'red'|'yellow'|'blue'|'purple'|'cyan' }) {
  return (
    <span className={`badge badge-${variant}`}>
      {children}
    </span>
  );
}
