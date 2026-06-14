'use client';
import { useState } from 'react';
import { useToast } from '@/components/ui/Toast';
import { Save, Key, Bot, Shield, Bell, Scan } from 'lucide-react';

export default function SettingsPage() {
  const { addToast } = useToast();
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      addToast('Settings saved successfully', 'success');
    }, 500);
  };

  return (
    <div className="page animate-fade" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Settings</h1>
          <p>Configure your API keys and system preferences</p>
        </div>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          <Save size={16} /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div className="card">
          <div className="section-title"><Key size={18} /> Exchange API Keys</div>
          <div className="grid-2">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Binance API Key</label>
              <input type="password" className="input" defaultValue="abcdef1234567890" />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Binance Secret Key</label>
              <input type="password" className="input" defaultValue="****************" />
            </div>
          </div>
          <div style={{ marginTop: '16px' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => addToast('Connection successful', 'success')}>Test Connection</button>
          </div>
        </div>

        <div className="card">
          <div className="section-title"><Bot size={18} /> AI Settings</div>
          <div className="grid-2">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>OpenAI API Key</label>
              <input type="password" className="input" defaultValue="sk-..." />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Model Selection</label>
              <select className="input" defaultValue="gpt-4o">
                <option value="gpt-4o">GPT-4o (Recommended)</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Fast)</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-title"><Shield size={18} /> Risk Management</div>
          <div className="grid-3">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Account Equity (USDT)</label>
              <input type="number" className="input" defaultValue="10000" />
            </div>
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                <span>Risk per Trade</span> <span>1.5%</span>
              </label>
              <input type="range" min="0.5" max="5" step="0.1" defaultValue="1.5" style={{ width: '100%', marginTop: '10px' }} />
            </div>
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                <span>Max Open Trades</span> <span>5</span>
              </label>
              <input type="range" min="1" max="20" step="1" defaultValue="5" style={{ width: '100%', marginTop: '10px' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-title"><Bell size={18} /> Notifications</div>
          <div className="grid-2">
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Telegram Bot Token</label>
              <input type="password" className="input" placeholder="bot..." />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Telegram Chat ID</label>
              <input type="text" className="input" placeholder="123456789" />
            </div>
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>Discord Webhook URL</label>
              <input type="text" className="input" placeholder="https://discord.com/api/webhooks/..." />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-title"><Scan size={18} /> Scanner Configuration</div>
          <div className="grid-3">
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                <span>Scan Interval</span> <span>300s</span>
              </label>
              <input type="range" min="60" max="3600" step="60" defaultValue="300" style={{ width: '100%', marginTop: '10px' }} />
            </div>
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                <span>Top N Signals</span> <span>50</span>
              </label>
              <input type="range" min="10" max="100" step="5" defaultValue="50" style={{ width: '100%', marginTop: '10px' }} />
            </div>
            <div>
              <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                <span>Min AI Score</span> <span>70</span>
              </label>
              <input type="range" min="0" max="100" step="5" defaultValue="70" style={{ width: '100%', marginTop: '10px' }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
