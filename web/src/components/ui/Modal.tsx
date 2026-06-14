'use client';
import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export function Modal({ 
  open, 
  onClose, 
  title, 
  children 
}: { 
  open: boolean, 
  onClose: () => void, 
  title: string, 
  children: React.ReactNode 
}) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (open) {
      window.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600 }}>{title}</h2>
          <button className="btn-icon" onClick={onClose}><X size={18} /></button>
        </div>
        <div>
          {children}
        </div>
      </div>
    </div>
  );
}
