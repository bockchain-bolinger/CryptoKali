'use client';
import { useState, useEffect } from 'react';
import { getEvolutionLessons } from '@/lib/api';
import { Brain, GraduationCap, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';

export default function EvolutionPage() {
  const [lessons, setLessons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLessons = async () => {
    setLoading(true);
    try {
      const data = await getEvolutionLessons();
      setLessons(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchLessons();
  }, []);

  return (
    <div className="page animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: 'calc(100vh - var(--topbar-height))' }}>
      
      {/* Header Panel */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(56, 189, 248, 0.05) 100%)', border: '1px solid rgba(139, 92, 246, 0.2)', flexShrink: 0 }}>
        <div>
          <div className="section-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#a78bfa' }}>
            <Brain size={22} /> Apex Evolution
          </div>
          <p style={{ margin: '8px 0 0 0', color: 'var(--text-secondary)', fontSize: '14px' }}>
            Continuous Learning Logbook. Every closed trade is analyzed via LLM to extract actionable lessons for future trades.
          </p>
        </div>
        <button className="btn btn-primary" onClick={fetchLessons} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh Memory
        </button>
      </div>

      {/* Stats Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', flexShrink: 0 }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '16px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '12px', color: '#a78bfa' }}>
            <GraduationCap size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Lessons Learned</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{lessons.length}</div>
          </div>
        </div>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '16px', background: 'rgba(34, 197, 94, 0.1)', borderRadius: '12px', color: 'var(--green)' }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Profitable Patterns Found</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{lessons.filter(l => l.pnl > 0).length}</div>
          </div>
        </div>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', color: 'var(--red)' }}>
            <AlertCircle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Mistakes Avoided</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{lessons.filter(l => l.pnl <= 0).length}</div>
          </div>
        </div>
      </div>

      {/* Timeline of Lessons */}
      <div className="card" style={{ flex: 1, overflowY: 'auto' }}>
        <div className="section-title" style={{ marginBottom: '24px' }}>AI Memory Logbook</div>
        
        {lessons.length === 0 ? (
          <div className="text-muted" style={{ textAlign: 'center', padding: '40px' }}>
            No lessons recorded yet. Close a trade to trigger the Evolution Agent.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {lessons.map((lesson) => {
              const isWin = lesson.pnl > 0;
              return (
                <div key={lesson.id} style={{ display: 'flex', gap: '16px', position: 'relative' }}>
                  {/* Timeline connector */}
                  <div style={{ position: 'absolute', left: '19px', top: '40px', bottom: '-20px', width: '2px', background: 'var(--border)', zIndex: 0 }}></div>
                  
                  {/* Status Icon */}
                  <div style={{ position: 'relative', zIndex: 1, width: '40px', height: '40px', borderRadius: '50%', background: isWin ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)', border: `2px solid ${isWin ? 'var(--green)' : 'var(--red)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    {isWin ? <TrendingUp size={18} color="var(--green)" /> : <AlertCircle size={18} color="var(--red)" />}
                  </div>
                  
                  {/* Content Box */}
                  <div style={{ flex: 1, background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '12px', padding: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <span style={{ fontWeight: 'bold', fontSize: '16px', color: 'var(--text-primary)' }}>{lesson.symbol}</span>
                        <span className={isWin ? 'text-positive' : 'text-negative'} style={{ fontWeight: 'bold' }}>
                          {isWin ? '+' : ''}${lesson.pnl.toFixed(2)}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {new Date(lesson.timestamp).toLocaleString()}
                      </div>
                    </div>
                    
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', fontFamily: 'monospace', background: 'rgba(0,0,0,0.2)', padding: '4px 8px', borderRadius: '4px' }}>
                      {lesson.market_context}
                    </div>
                    
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                      <Brain size={18} style={{ color: '#a78bfa', marginTop: '2px', flexShrink: 0 }} />
                      <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5', color: 'var(--text-primary)' }}>
                        {lesson.lesson_learned}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
