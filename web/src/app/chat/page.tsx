'use client';
import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { Send, Plus, MessageSquare, Bot, Search, AlertTriangle, Newspaper, Briefcase } from 'lucide-react';

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: 'Willkommen bei CryptoKali AI! Frag mich über den Markt, Signale oder dein Portfolio. Nutze /help für verfügbare Befehle.', timestamp: new Date().toISOString() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('coordinator');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const agents = [
    { id: 'analyst', name: 'Analyst', icon: <Search size={16} /> },
    { id: 'risk', name: 'Risk', icon: <AlertTriangle size={16} /> },
    { id: 'sentiment', name: 'Sentiment', icon: <Newspaper size={16} /> },
    { id: 'portfolio', name: 'Portfolio', icon: <Briefcase size={16} /> },
  ];

  const commands = ['/analyze', '/signals', '/portfolio', '/risk', '/help'];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date().toISOString() }]);
    setLoading(true);

    try {
      const response = await sendChatMessage('session-1', userMsg);
      setMessages(prev => [...prev, { role: 'assistant', content: response.message, timestamp: new Date().toISOString() }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Fehler beim Abrufen der Antwort.', isError: true, timestamp: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - var(--topbar-height))', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div style={{ width: '250px', borderRight: '1px solid var(--border)', background: 'var(--bg-card)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '16px' }}>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
            <Plus size={16} /> New Chat
          </button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
          <div style={{ padding: '8px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>Recent Sessions</div>
          {[1,2,3].map(i => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 12px', borderRadius: 'var(--radius-sm)', cursor: 'pointer', background: i === 1 ? 'rgba(255,255,255,0.05)' : 'transparent', marginBottom: '4px' }} className="hover:bg-white/5">
              <MessageSquare size={16} className="text-muted" />
              <div style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {i === 1 ? 'BTC Analysis & Setup' : i === 2 ? 'Portfolio Review' : 'Market Sentiment Check'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--bg-primary)' }}>
        {/* Header */}
        <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 600 }}>Direct Agent:</div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className={`btn ${selectedAgent === 'coordinator' ? 'btn-secondary' : ''}`}
              style={{ background: selectedAgent === 'coordinator' ? '' : 'transparent' }}
              onClick={() => setSelectedAgent('coordinator')}
            >
              <Bot size={16} /> Auto (Coordinator)
            </button>
            <div style={{ width: '1px', background: 'var(--border)', margin: '0 4px' }}></div>
            {agents.map(agent => (
              <button 
                key={agent.id}
                className={`btn ${selectedAgent === agent.id ? 'btn-secondary' : ''}`}
                style={{ background: selectedAgent === agent.id ? '' : 'transparent', color: 'var(--text-secondary)' }}
                onClick={() => setSelectedAgent(agent.id)}
              >
                {agent.icon} {agent.name}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {messages.map((msg, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '16px', maxWidth: '80%', alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'assistant' && (
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Bot size={18} color="white" />
                </div>
              )}
              <div style={{ 
                background: msg.role === 'user' ? 'var(--accent-indigo)' : 'var(--bg-card)',
                color: msg.role === 'user' ? 'white' : msg.isError ? 'var(--red)' : 'var(--text-primary)',
                padding: '12px 16px',
                borderRadius: '12px',
                borderTopRightRadius: msg.role === 'user' ? '4px' : '12px',
                borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '12px',
                border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
                lineHeight: 1.5,
                fontSize: '14px'
              }}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: '16px', maxWidth: '80%', alignSelf: 'flex-start' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot size={18} color="white" />
              </div>
              <div style={{ background: 'var(--bg-card)', padding: '12px 16px', borderRadius: '12px', borderTopLeftRadius: '4px', border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', gap: '4px' }}>
                  <div className="live-dot" style={{ animationDelay: '0s', background: 'var(--text-muted)' }}></div>
                  <div className="live-dot" style={{ animationDelay: '0.2s', background: 'var(--text-muted)' }}></div>
                  <div className="live-dot" style={{ animationDelay: '0.4s', background: 'var(--text-muted)' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: '24px', borderTop: '1px solid var(--border)', background: 'var(--bg-primary)' }}>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
            {commands.map(cmd => (
              <button 
                key={cmd}
                className="badge badge-blue" 
                style={{ cursor: 'pointer', border: 'none' }}
                onClick={() => setInput(cmd + ' ')}
              >
                {cmd}
              </button>
            ))}
          </div>
          <div style={{ position: 'relative' }}>
            <textarea
              className="input"
              style={{ minHeight: '60px', maxHeight: '200px', resize: 'none', paddingRight: '48px', paddingTop: '16px' }}
              placeholder="Ask anything about the market..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button 
              className="btn-icon"
              style={{ position: 'absolute', right: '12px', bottom: '12px', background: input.trim() ? 'var(--accent-indigo)' : '', color: input.trim() ? 'white' : '' }}
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              <Send size={16} />
            </button>
          </div>
          <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
            AI responses may be inaccurate. Always verify trading signals.
          </div>
        </div>
      </div>
    </div>
  );
}
