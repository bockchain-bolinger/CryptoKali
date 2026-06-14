import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export function StatCard({ 
  title, 
  value, 
  change, 
  changePercent, 
  icon, 
  trend = 'neutral' 
}: { 
  title: string, 
  value: string | number, 
  change?: string | number, 
  changePercent?: string | number, 
  icon?: React.ReactNode, 
  trend?: 'up'|'down'|'neutral' 
}) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '13px', fontWeight: 500 }}>{title}</div>
        {icon && <div style={{ color: 'var(--text-muted)' }}>{icon}</div>}
      </div>
      <div style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px' }}>{value}</div>
      {(change !== undefined || changePercent !== undefined) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '13px' }}>
          {trend === 'up' && <TrendingUp size={14} className="text-positive" />}
          {trend === 'down' && <TrendingDown size={14} className="text-negative" />}
          {trend === 'neutral' && <Minus size={14} className="text-muted" />}
          
          <span className={trend === 'up' ? 'text-positive' : trend === 'down' ? 'text-negative' : 'text-muted'}>
            {change} {changePercent ? `(${changePercent}%)` : ''}
          </span>
        </div>
      )}
    </div>
  );
}
