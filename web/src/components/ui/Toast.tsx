'use client';
import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, Info } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  addToast: (message: string, type: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
  }, []);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {toasts.map(toast => (
          <div key={toast.id} className="animate-fade" style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderLeft: `4px solid ${
              toast.type === 'success' ? 'var(--green)' : 
              toast.type === 'error' ? 'var(--red)' : 
              toast.type === 'warning' ? 'var(--yellow)' : 'var(--accent-indigo)'
            }`,
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            boxShadow: 'var(--shadow)',
            minWidth: '300px'
          }}>
            {toast.type === 'success' && <CheckCircle2 size={18} color="var(--green)" />}
            {toast.type === 'error' && <AlertCircle size={18} color="var(--red)" />}
            {toast.type === 'warning' && <AlertCircle size={18} color="var(--yellow)" />}
            {toast.type === 'info' && <Info size={18} color="var(--accent-indigo)" />}
            <span style={{ fontSize: '13px', fontWeight: 500 }}>{toast.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
}
