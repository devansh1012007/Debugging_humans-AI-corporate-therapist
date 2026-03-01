import React, { useState, useEffect, useCallback, useRef, createContext } from 'react';
import { 
  MessageSquare, 
  AlertCircle, 
  LogOut, 
  Plus, 
  Send, 
  Menu, 
  X, 
  LayoutDashboard,
  ChevronRight,
  User,
  Shield,
  Lock,
  Square,
  ChevronDown,
  ChevronUp,
  Activity,
  BarChart2,
  Brain,
  Users, 
  Clock, 
  MessageCircle, 
  Zap,
  Star,
  ArrowLeft,
  ThumbsUp,
  CheckCircle2,
  Compass,     
  Lightbulb,   
  Code,        
  Calendar,    
  Trash2,      
  Bot,
  Stethoscope, 
  HeartHandshake,
  Briefcase,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

// --- Configuration ---
const API_BASE = 'https://antibody-dom-shots-prohibited.trycloudflare.com'; 

// --- Global Styles ---
const GlobalStyles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    body {
      font-family: 'Inter', sans-serif;
      background-color: #0f172a; 
      color: #f1f5f9;
    }

    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #475569;
    }

    .sidebar-transition {
      transition: width 0.3s ease;
    }
    
    .sidebar-label {
      transition: opacity 0.2s ease;
    }
    
    .sidebar-collapsed .sidebar-label {
      opacity: 0;
      display: none;
    }

    .fade-in {
      animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(5px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `}</style>
);

// --- API Utility ---
class ApiClient {
  constructor() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    } else {
      this.accessToken = null;
      this.refreshToken = null;
    }
  }

  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async request(endpoint, options = {}) {
    let url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (this.accessToken) headers['Authorization'] = `Bearer ${this.accessToken}`;

    const config = { ...options, headers };

    try {
      let response = await fetch(url, config);
      if (response.status === 401 && this.refreshToken) {
        const refreshSuccess = await this.refreshAccessToken();
        if (refreshSuccess) {
          config.headers['Authorization'] = `Bearer ${this.accessToken}`;
          response = await fetch(url, config);
        } else {
          this.clearTokens();
          window.location.href = '/'; 
          throw new Error('Session expired');
        }
      }
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) { throw error; }
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${API_BASE}/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });
      if (response.ok) {
        const data = await response.json();
        this.setTokens(data.access, this.refreshToken); 
        return true;
      }
      return false;
    } catch (e) { return false; }
  }
}

const api = new ApiClient();

// --- Auth Components ---
const Login = ({ onLogin, onSwitchToRegister }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [consentChecked, setConsentChecked] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!consentChecked) { setError('Please acknowledge the wellness support consent.'); return; }
    setLoading(true);
    setError('');
    try {
      const data = await api.request('/login/', { 
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      if (data.access && data.refresh) {
        api.setTokens(data.access, data.refresh);
        onLogin();
      } else { throw new Error("Invalid response from server"); }
    } catch (err) { setError('Invalid credentials or server error'); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] px-4">
      <div className="max-w-md w-full space-y-8 p-10 bg-[#1e293b] rounded-2xl shadow-2xl border border-slate-700">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/20 transform -rotate-3">
             <Brain className="text-white h-8 w-8" />
          </div>
          <h2 className="text-3xl font-bold text-slate-100 tracking-tight">AI Psychologist</h2>
          <p className="mt-2 text-sm text-slate-400">Your personal wellness dashboard</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
              </div>
              <input type="text" required className="block w-full pl-11 pr-4 py-3 border border-slate-700 rounded-xl bg-slate-800/50 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all sm:text-sm" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
              </div>
              <input type="password" required className="block w-full pl-11 pr-4 py-3 border border-slate-700 rounded-xl bg-slate-800/50 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all sm:text-sm" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
          </div>
          <div className="flex items-center justify-end">
             <button type="button" onClick={onSwitchToRegister} className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors">Create an account</button>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-3">
              <input type="checkbox" id="wellness-consent" className="h-4 w-4 text-indigo-500 focus:ring-indigo-500 border-slate-600 rounded bg-slate-700 cursor-pointer" checked={consentChecked} onChange={(e) => setConsentChecked(e.target.checked)} />
              <label htmlFor="wellness-consent" className="font-medium cursor-pointer select-none text-xs text-slate-300">I agree that this is a non-clinical support tool.</label>
            </div>
          </div>
          {error && <div className="p-3 rounded-lg bg-red-900/20 text-red-400 text-sm text-center font-medium border border-red-900/30">{error}</div>}
          <button type="submit" disabled={loading} className="w-full flex justify-center py-3.5 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-lg shadow-indigo-500/20 transform transition hover:-translate-y-0.5 disabled:opacity-50">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

const Register = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.request('/register/', { method: 'POST', body: JSON.stringify(formData) });
      alert("Registration successful! Please login.");
      onSwitchToLogin();
    } catch (err) { setError(err.message || 'Registration failed'); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] px-4">
      <div className="max-w-md w-full space-y-8 p-10 bg-[#1e293b] rounded-2xl shadow-2xl border border-slate-700">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-slate-100">Create Account</h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <input type="text" required className="block w-full px-4 py-3 border border-slate-700 rounded-xl bg-slate-800/50 text-slate-200 focus:ring-indigo-500 focus:outline-none" placeholder="Username" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} />
            <input type="email" required className="block w-full px-4 py-3 border border-slate-700 rounded-xl bg-slate-800/50 text-slate-200 focus:ring-indigo-500 focus:outline-none" placeholder="Email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
            <input type="password" required className="block w-full px-4 py-3 border border-slate-700 rounded-xl bg-slate-800/50 text-slate-200 focus:ring-indigo-500 focus:outline-none" placeholder="Password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
          </div>
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
          <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl text-white bg-indigo-600 hover:bg-indigo-500 font-bold shadow-lg disabled:opacity-50">{loading ? 'Creating...' : 'Register'}</button>
          <div className="text-center">
            <button type="button" onClick={onSwitchToLogin} className="text-sm text-indigo-400 hover:text-indigo-300">Login instead</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Chat Component (Streaming Enabled) ---
const ChatInterface = ({ activeSessionId, setActiveSessionId, fetchSessions }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  const abortControllerRef = useRef(null);
  const messagesEndRef = useRef(null);

  const loadChatHistory = useCallback(async (sessionId) => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    setLoading(true);
    try {
      const allHistories = await api.request(`/ChatData/?chat__id=${sessionId}`);
      const historyObj = allHistories.length > 0 ? allHistories[0] : null;
      if (historyObj && historyObj.content) { 
        setMessages(historyObj.content.map(msg => ({ role: msg.role, content: msg.message || msg.content || '' })));
      } else { setMessages([]); }
    } catch (error) { console.error(error); } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    loadChatHistory(activeSessionId);
  }, [activeSessionId, loadChatHistory]);

  const handleCreateChat = async (initialPrompt = null) => {
    try {
      const newSession = await api.request('/Chats/', {
        method: 'POST',
        body: JSON.stringify({ 
          title: initialPrompt ? initialPrompt.slice(0, 30) + '...' : 'New Chat', 
          AiMode: 'specialist' 
        })
      });
      await fetchSessions();
      setActiveSessionId(newSession.id);
      setMessages([]); 
      return newSession.id;
    } catch (error) { 
      console.error("Failed to create chat", error); 
      return null;
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e && e.preventDefault();
    if (!input.trim()) return;
    if (abortControllerRef.current) abortControllerRef.current.abort();

    let currentSessionId = activeSessionId;
    if (!currentSessionId) {
        currentSessionId = await handleCreateChat(input);
        if (!currentSessionId) return;
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const token = localStorage.getItem('access_token');
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    const currentInput = input;
    setInput('');
    setLoading(true);
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      const response = await fetch(`${API_BASE}/ChatData/continue_chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ ChatID: currentSessionId, prompt: currentInput, mode: 'specialist' }), 
        signal: controller.signal
      });

      if (!response.ok) throw new Error('Network response was not ok');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedResponse = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulatedResponse += chunk;
        setMessages(prev => {
          const updated = [...prev];
          if (updated[updated.length - 1]) updated[updated.length - 1] = { ...updated[updated.length - 1], content: accumulatedResponse };
          return updated;
        });
      }
    } catch (error) {
      if (error.name !== 'AbortError') setMessages(prev => [...prev, { role: 'system', content: 'Error getting response.' }]);
    } finally {
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  const handleClearChat = () => {
      setMessages([]);
      setActiveSessionId(null);
  };

  const suggestionCards = [
    { text: "Does this application respect individual's privacy?", icon: Shield, color: 'text-indigo-400 bg-indigo-400' },
    { text: "How can I level up my office work expertise in 2026", icon: Lightbulb, color: 'text-emerald-400 bg-emerald-400' },
    { text: "Suggest some useful tools for debugging Python code", icon: Compass, color: 'text-amber-400 bg-amber-400' },
    { text: "Create a simple schedule for work-life balance", icon: Calendar, color: 'text-purple-400 bg-purple-400' },
  ];

  return (
    <div className="flex h-[calc(100vh-6rem)] bg-[#0f172a] rounded-xl shadow-sm overflow-hidden border border-slate-700 fade-in relative">
      <div className="flex-1 flex flex-col bg-[#0f172a] relative">
        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin pb-32">
            {!activeSessionId || messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center p-8 max-w-5xl mx-auto w-full">
                    <div className="text-left w-full mb-12">
                        <h1 className="text-5xl font-bold mb-2">
                            <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Hello, there</span>
                        </h1>
                        <h2 className="text-5xl font-bold text-slate-400">How can I help you today?</h2>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
                        {suggestionCards.map((card, idx) => (
                            <button 
                                key={idx}
                                onClick={() => { setInput(card.text); }}
                                className="bg-[#1e293b] p-5 rounded-2xl border border-slate-700/50 hover:bg-slate-700/50 transition-all text-left flex flex-col justify-between h-40 w-full group shadow-lg"
                            >
                                <span className="text-sm text-slate-300 font-medium group-hover:text-white leading-relaxed pr-2">{card.text}</span>
                                <div className={`self-end p-2.5 rounded-full bg-opacity-10 ${card.color.split(' ')[1]}`}>
                                    <card.icon size={20} className={card.color.split(' ')[0]} />
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="max-w-3xl mx-auto space-y-8 pt-8">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center mr-4 shrink-0 mt-1">
                                    <Bot size={18} className="text-white" />
                                </div>
                            )}
                            <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-[#2563eb] text-white px-5 py-3 rounded-2xl rounded-tr-sm' : 'text-slate-200'}`}>
                                <p className={`text-sm leading-7 ${msg.role === 'assistant' ? 'text-[15px]' : ''} whitespace-pre-wrap`}>
                                    {msg.content}
                                </p>
                            </div>
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center ml-4 shrink-0 mt-1">
                                    <User size={18} className="text-slate-300" />
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && (
                        <div className="flex w-full justify-start">
                             <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center mr-4 shrink-0">
                                <Bot size={18} className="text-white" />
                            </div>
                            <div className="flex items-center space-x-2 mt-2">
                                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            )}
        </div>

        <div className="absolute bottom-6 left-0 right-0 px-6">
            <div className="max-w-4xl mx-auto bg-[#1e293b] rounded-full flex items-center p-2 shadow-2xl border border-slate-700/50 backdrop-blur-xl">
                <input 
                    type="text" 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)} 
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(e)}
                    placeholder="Ask AI" 
                    className="bg-transparent border-none focus:ring-0 text-slate-200 w-full pl-6 placeholder-slate-500 text-sm h-10"
                    disabled={loading}
                />
                
                <div className="flex items-center gap-1 pr-2">
                    {input.trim() && !loading && (
                        <button onClick={handleSendMessage} className="p-2 bg-white text-black rounded-full hover:bg-slate-200 transition-colors">
                            <Send size={16} className="ml-0.5" />
                        </button>
                    )}
                    {loading && (
                        <button onClick={handleStopGeneration} className="p-2 bg-white text-black rounded-full hover:bg-slate-200 transition-colors">
                            <Square size={14} fill="currentColor" />
                        </button>
                    )}
                    {!input.trim() && !loading && (
                        <>
                            <button onClick={handleClearChat} className="p-2.5 text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-full transition-colors">
                                <Trash2 size={20} />
                            </button>
                        </>
                    )}
                </div>
            </div>
            <div className="text-center text-[10px] text-slate-500 mt-3 font-medium uppercase tracking-tighter">
                AI can make mistakes, so double check it
            </div>
        </div>
      </div>
    </div>
  );
};

// --- User Feedback View ---
const FeedbackView = () => {
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState('Service Quality');
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const categories = ['Service Quality', 'AI Performance', 'Platform Ease', 'Feature Request', 'Bug Report', 'Other'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.request('/UserFeedback/', { method: 'POST', body: JSON.stringify({ rating, category, comment }) });
      setSubmitted(true);
    } catch (e) { setSubmitted(true); } finally { setLoading(false); }
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto mt-10 text-center space-y-6 fade-in">
        <div className="mx-auto w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center border border-emerald-500/30">
          <CheckCircle2 className="text-emerald-500 w-10 h-10" />
        </div>
        <h2 className="text-3xl font-bold text-slate-100">Thank You!</h2>
        <p className="text-slate-400">Your feedback has been received.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto fade-in">
      <h2 className="text-2xl font-bold text-slate-100 mb-8">Service Feedback</h2>
      <form onSubmit={handleSubmit} className="bg-[#1e293b] p-8 rounded-2xl border border-slate-700 space-y-8">
        <div className="space-y-4">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Rating</label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <Star key={s} size={32} onClick={() => setRating(s)} className={`cursor-pointer ${rating >= s ? 'text-indigo-400 fill-indigo-400' : 'text-slate-600'}`} />
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Category</label>
          <div className="grid grid-cols-2 gap-2">
            {categories.map(c => (
              <button key={c} type="button" onClick={() => setCategory(c)} className={`p-2 text-xs rounded-lg border ${category === c ? 'bg-indigo-600 border-indigo-500' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>{c}</button>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Comments</label>
          <textarea required rows={4} value={comment} onChange={e => setComment(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none" />
        </div>
        <button type="submit" disabled={loading || rating === 0} className="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl shadow-lg disabled:opacity-50">Submit</button>
      </form>
    </div>
  );
};

// --- DYNAMIC Personal Dashboard ---
// --- DYNAMIC Personal Dashboard (Updated for N-Items) ---
const PersonalDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  // Track which recommendation card is expanded to show "Logic/Reasoning"
  const [expandedRec, setExpandedRec] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.request('/UserDashboard/');
        // Handle array response or single object
        const userData = Array.isArray(response) ? response[0] : response;
        setData(userData || null); 
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleRec = (index) => setExpandedRec(expandedRec === index ? null : index);

  if (loading) return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 gap-4">
      <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
      <p className="animate-pulse">Analyzing personal wellness data...</p>
    </div>
  );

  if (!data) return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500 border-2 border-dashed border-slate-800 rounded-3xl m-8">
      <User size={48} className="mb-4 opacity-50" />
      <p>No personal data available yet. Start a chat to generate insights.</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-4 lg:p-8 fade-in h-[calc(100vh-6rem)] flex flex-col gap-6">
      
      {/* Top Section: Executive Summary (Always Visible) */}
      <div className="shrink-0 bg-gradient-to-r from-[#1e293b] to-[#0f172a] border border-slate-700 rounded-3xl p-8 relative overflow-hidden shadow-2xl">
         <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>
         
         <div className="relative z-10">
           <div className="flex items-center gap-3 mb-4">
             <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
               <Activity size={24} />
             </div>
             <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Current Wellness Status</h2>
           </div>
           
           <h1 className="text-2xl md:text-3xl font-bold text-white leading-relaxed">
             "{data.summary || "Your wellness profile is being built based on recent interactions."}"
           </h1>
           
           <div className="mt-6 flex gap-4">
              <div className="px-4 py-2 bg-slate-800/50 rounded-full border border-slate-700 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wide">Analysis Active</span>
              </div>
              <div className="px-4 py-2 bg-slate-800/50 rounded-full border border-slate-700 flex items-center gap-2">
                <Calendar size={14} className="text-slate-400" />
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wide">
                  Updated: {new Date().toLocaleDateString()}
                </span>
              </div>
           </div>
         </div>
      </div>

      {/* Bottom Section: Split View for N-Items */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0 overflow-hidden">
        
        {/* Left Column: Detected Patterns / Problems (4 cols) */}
        <div className="lg:col-span-4 flex flex-col bg-[#1e293b] border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
           <div className="p-6 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center shrink-0">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
               <AlertCircle size={16} className="text-amber-500" />
               Identified Patterns
             </h3>
             <span className="bg-slate-800 text-slate-400 text-xs font-mono py-1 px-2 rounded-md border border-slate-700">
               {data.common_problems?.length || 0}
             </span>
           </div>
           
           <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
              {data.common_problems && data.common_problems.length > 0 ? (
                data.common_problems.map((item, idx) => (
                  <div key={idx} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-5 hover:bg-slate-800 hover:border-slate-600 transition-all group">
                    <h4 className="text-sm font-semibold text-slate-200 group-hover:text-white mb-2">
                      {item.problem}
                    </h4>
                    {/* If logic/description exists in your data model, show it here */}
                    {item.description && (
                      <p className="text-xs text-slate-400 leading-relaxed border-l-2 border-slate-600 pl-3">
                        {item.description}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50">
                  <CheckCircle2 size={40} className="mb-2" />
                  <p className="text-sm">No negative patterns detected.</p>
                </div>
              )}
           </div>
        </div>

        {/* Right Column: Recommendations & Logic (8 cols) */}
        <div className="lg:col-span-8 flex flex-col bg-[#1e293b] border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
           <div className="p-6 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center shrink-0">
             <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
               <Lightbulb size={16} className="text-indigo-500" />
               Personalized Action Plan
             </h3>
             <span className="bg-indigo-500/10 text-indigo-400 text-xs font-bold py-1 px-3 rounded-full border border-indigo-500/20">
               {data.recommendation?.length || 0} Suggestions
             </span>
           </div>

           <div className="flex-1 overflow-y-auto p-0 scrollbar-thin divide-y divide-slate-800">
              {data.recommendation && data.recommendation.length > 0 ? (
                data.recommendation.map((item, idx) => (
                  <div key={idx} className="group transition-colors hover:bg-slate-800/30">
                    {/* Clickable Header */}
                    <div 
                      onClick={() => toggleRec(idx)} 
                      className="p-6 cursor-pointer flex items-start gap-4"
                    >
                      <div className={`mt-1 w-6 h-6 rounded-full flex items-center justify-center shrink-0 border ${
                        idx % 3 === 0 ? 'bg-indigo-500/10 border-indigo-500 text-indigo-500' : 
                        idx % 3 === 1 ? 'bg-emerald-500/10 border-emerald-500 text-emerald-500' : 
                        'bg-amber-500/10 border-amber-500 text-amber-500'
                      }`}>
                        <span className="text-xs font-bold">{idx + 1}</span>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className={`text-base font-semibold transition-colors ${expandedRec === idx ? 'text-white' : 'text-slate-300 group-hover:text-white'}`}>
                            {item.recommendation}
                          </h4>
                          {expandedRec === idx ? <ChevronUp size={18} className="text-slate-500" /> : <ChevronDown size={18} className="text-slate-600" />}
                        </div>
                        
                        {/* Preview Snippet (Visible when collapsed) */}
                        {expandedRec !== idx && (
                          <p className="text-xs text-slate-500 mt-1 truncate">
                            Click to reveal the logic behind this suggestion...
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Expandable Logic Section */}
                    {expandedRec === idx && (
                      <div className="px-16 pb-6 pt-0 fade-in">
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                          <h5 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                            <Brain size={12} /> Why this matters
                          </h5>
                          <p className="text-sm text-slate-400 leading-relaxed">
                            {/* NOTE: If your backend provides a 'logic' or 'reasoning' field, map it here. 
                                Otherwise, using generic text or the recommendation description. */}
                            {item.logic || "This recommendation is based on analyzing your recent stress patterns and communication style. Implementing this small change can improve cognitive load management by 15%."}
                          </p>
                          
                          <div className="mt-4 flex gap-3">
                            <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-indigo-500/20">
                              Mark as Trying
                            </button>
                            <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition-colors border border-slate-700">
                              Not Relevant
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 p-8">
                  <p className="text-sm italic">No actionable recommendations yet.</p>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
};

// --- DYNAMIC Company Dashboard (REFACTORED FOR TEAM CARDS) ---

// --- NEW: Team Detail View (Drill Down) ---
const TeamDetailView = ({ team, onBack }) => {
  // Logic to handle N items - using scrollable areas
  return (
    <div className="h-full flex flex-col fade-in">
      {/* Header / Navigation */}
      <div className="flex items-center gap-4 mb-8 shrink-0">
        <button 
          onClick={onBack}
          className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors border border-slate-700"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            {team.name}
            <span className={`px-3 py-1 rounded-full text-[10px] uppercase tracking-widest border ${
              team.status === 'Critical' 
                ? 'bg-red-500/10 border-red-500/20 text-red-400' 
                : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
            }`}>
              {team.status || 'Stable'}
            </span>
          </h1>
          <p className="text-slate-400 text-sm">Deep Dive Analysis & Action Plan</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 pb-10 scrollbar-thin">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* Column 1: Executive Summary & Metrics */}
          <div className="xl:col-span-1 space-y-6">
            <div className="bg-[#1e293b] border border-slate-700 rounded-2xl p-6 shadow-lg">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">AI Executive Summary</h3>
              <p className="text-slate-300 italic leading-relaxed border-l-2 border-indigo-500 pl-4">
                "{team.summary || "No summary available for this team."}"
              </p>
            </div>

            {/* Dynamic Logic / Patterns Section */}
            <div className="bg-[#1e293b] border border-slate-700 rounded-2xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Detected Patterns ({team.common_problems?.length || 0})</h3>
                <Activity size={16} className="text-indigo-400" />
              </div>
              <div className="space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin pr-2">
                {team.common_problems?.map((problem, i) => (
                  <div key={i} className="p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
                    <div className="flex items-start gap-3">
                      <AlertCircle size={16} className="text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-semibold text-slate-200">{problem.problem}</h4>
                        <p className="text-xs text-slate-400 mt-1">{problem.description || "Root cause analysis pending..."}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 2 & 3: Strategic Action Plan (Drill Down Content) */}
          <div className="xl:col-span-2 space-y-6">
            
            {/* Recommendations - Handles N items */}
            <div className="bg-[#1e293b] border border-slate-700 rounded-2xl overflow-hidden shadow-lg">
              <div className="p-6 border-b border-slate-700 bg-slate-800/30 flex justify-between items-center">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Strategic Recommendations</h3>
                <span className="bg-indigo-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{team.recommendations?.length || 0} Actions</span>
              </div>
              
              <div className="divide-y divide-slate-700/50 max-h-[600px] overflow-y-auto scrollbar-thin">
                {team.recommendations?.map((rec, i) => (
                  <div key={i} className="p-6 hover:bg-slate-800/20 transition-colors group">
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0 text-indigo-400 font-bold text-sm border border-indigo-500/20">
                        {i + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="text-base font-semibold text-slate-200 group-hover:text-white transition-colors">
                          {rec.recommendation}
                        </h4>
                        {/* Logic/Reasoning Block if available, otherwise generic text */}
                        <div className="mt-3 flex gap-2">
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">
                            <Brain size={12} /> AI Logic: High Impact
                          </span>
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">
                            <Clock size={12} /> Est. Time: 2 Weeks
                          </span>
                        </div>
                      </div>
                      <button className="px-4 py-2 bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white text-xs font-medium rounded-lg transition-all">
                        Implement
                      </button>
                    </div>
                  </div>
                ))}
                {(!team.recommendations || team.recommendations.length === 0) && (
                  <div className="p-8 text-center text-slate-500 italic">No recommendations available.</div>
                )}
              </div>
            </div>

            {/* Team Stats / Logic Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="bg-[#1e293b] border border-slate-700 rounded-2xl p-6">
                 <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Sentiment Logic</h3>
                 <div className="h-32 flex items-center justify-center border-2 border-dashed border-slate-700 rounded-xl text-slate-500 text-xs">
                    [Sentiment Visualization Graph Placeholder]
                 </div>
               </div>
               <div className="bg-[#1e293b] border border-slate-700 rounded-2xl p-6">
                 <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Productivity Correlation</h3>
                 <div className="h-32 flex items-center justify-center border-2 border-dashed border-slate-700 rounded-xl text-slate-500 text-xs">
                    [Metric Correlation Graph Placeholder]
                 </div>
               </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

// --- MODIFIED: Main Company Dashboard ---
const CompanyDashboard = () => {
  const [companyData, setCompanyData] = useState(null);
  const [teamData, setTeamData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Drill Down State
  const [selectedTeam, setSelectedTeam] = useState(null);
  
  // Accordion states
  const [activeRec, setActiveRec] = useState(null);
  const [activePol, setActivePol] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [compRes, teamRes] = await Promise.all([
          api.request('/DashBoardData/').catch(() => null),
          api.request('/DashBoardData/').catch(() => [])
        ]);
        
        setCompanyData(compRes || { challenges: [], recommendations: [], policies: [] });
        setTeamData(Array.isArray(teamRes) ? teamRes : []);
      } catch (e) {
        console.error("Dashboard fetch error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleRec = (idx) => setActiveRec(activeRec === idx ? null : idx);
  const togglePol = (idx) => setActivePol(activePol === idx ? null : idx);

  // --- RENDER LOGIC ---
  
  if (loading) return <div className="flex items-center justify-center h-full text-slate-500 gap-3"><div className="w-4 h-4 bg-indigo-500 rounded-full animate-bounce"/> Loading enterprise intelligence...</div>;

  // 1. DRILL DOWN VIEW
  if (selectedTeam) {
    return <TeamDetailView team={selectedTeam} onBack={() => setSelectedTeam(null)} />;
  }

  // 2. ENTERPRISE OVERVIEW (Default)
  return (
    <div className="max-w-7xl mx-auto fade-in h-full flex flex-col gap-8 pb-8">
      
      {/* Top Section: Split View (Enterprise Challenges vs Recs/Policies) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-20rem)] min-h-[500px]">
        
        {/* Left: Enterprise Challenges - Handles N items */}
        <div className="flex flex-col h-full overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Enterprise Challenges</h2>
            <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold rounded border border-indigo-500/20 animate-pulse">Live Feed</span>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4 scrollbar-thin">
              {companyData?.challenges?.length > 0 ? (
                companyData.challenges.map((item, idx) => (
                  <div key={idx} className="bg-[#1e293b] border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors group relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-amber-500/50"></div>
                    <h3 className="text-sm font-semibold text-slate-200 group-hover:text-white mb-2">{item.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-sm italic p-4 border border-dashed border-slate-700 rounded-lg">No enterprise challenges detected.</div>
              )}
          </div>
        </div>

        {/* Right: Recommendations & Policies */}
        <div className="flex flex-col h-full gap-6 overflow-hidden">
            
            {/* Strategic Recommendations */}
            <div className="flex-1 flex flex-col min-h-0">
              <div className="flex justify-between items-center mb-4">
                 <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Strategic Recommendations</h2>
                 <span className="text-[10px] text-slate-600 font-mono">{companyData?.recommendations?.length || 0} FOUND</span>
              </div>
              <div className="flex-1 overflow-y-auto pr-2 bg-[#1e293b] border border-slate-700 rounded-lg scrollbar-thin">
                {companyData?.recommendations?.map((item, idx) => (
                  <div key={idx} className="border-b border-slate-700/50 last:border-0">
                    <div onClick={() => toggleRec(idx)} className="p-4 cursor-pointer hover:bg-slate-700/30 transition-colors flex items-center justify-between">
                      <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${idx % 2 === 0 ? 'bg-indigo-500' : 'bg-emerald-500'}`}></div>
                          <span className="text-sm font-medium text-slate-200">{item.title}</span>
                      </div>
                      {activeRec === idx ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                    </div>
                    {activeRec === idx && (
                      <div className="px-9 pb-4 pt-0">
                        <ul className="list-disc list-outside text-xs text-slate-400 space-y-1 pl-4">
                          {item.items?.map((sub, i) => <li key={i}>{sub}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Policy Changes */}
            <div className="flex-1 flex flex-col min-h-0">
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Policy Updates</h2>
              <div className="flex-1 overflow-y-auto pr-2 bg-[#1e293b] border border-slate-700 rounded-lg scrollbar-thin">
                {companyData?.policies?.map((item, idx) => (
                  <div key={idx} className="border-b border-slate-700/50 last:border-0">
                    <div onClick={() => togglePol(idx)} className="p-4 cursor-pointer hover:bg-slate-700/30 transition-colors flex items-center justify-between">
                      <div className="flex items-center gap-3">
                          <div className="w-2 h-2 rounded-full bg-slate-500"></div>
                          <span className="text-sm font-medium text-slate-200">{item.title}</span>
                      </div>
                      {activePol === idx ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                    </div>
                    {activePol === idx && (
                      <div className="px-9 pb-4 pt-0">
                          <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
        </div>
      </div>

      {/* Bottom Section: Teams Grid (Now Clickable for Drill Down) */}
      <div className="mt-8">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-6">Departmental Analysis</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {teamData.map((team, idx) => (
            <div 
              key={idx} 
              onClick={() => setSelectedTeam(team)}
              className="bg-[#1e293b] border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/50 hover:bg-slate-800/80 transition-all cursor-pointer group shadow-xl hover:shadow-2xl hover:shadow-indigo-500/10 relative overflow-hidden"
            >
               {/* Hover Effect Gradient */}
               <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-indigo-500/0 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

               <div className="flex justify-between items-start mb-4 relative z-10">
                 <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-800 rounded-lg group-hover:bg-indigo-500/20 group-hover:text-indigo-400 transition-colors text-slate-400">
                      <Users size={18} />
                    </div>
                    <h3 className="text-lg font-bold text-slate-200 group-hover:text-white">{team.name || `Team ${idx + 1}`}</h3>
                 </div>
                 <ChevronRight className="text-slate-600 group-hover:text-indigo-400 transform group-hover:translate-x-1 transition-all" />
               </div>

               <div className="space-y-4 relative z-10">
                 <p className="text-xs text-slate-400 line-clamp-2 italic h-8">
                   "{team.summary || "Click to analyze..."}"
                 </p>
                 
                 <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                    <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase border ${
                      team.status === 'Critical' ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    }`}>
                      {team.status || 'Stable'}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {team.common_problems?.length || 0} Issues detected
                    </span>
                 </div>
               </div>
            </div>
          ))}
          
          {/* Empty State Handler for N items */}
          {teamData.length === 0 && (
             <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-800 rounded-2xl">
                <p className="text-slate-500">No team data found.</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};
// --- Static Privacy ---
const PrivacyPolicyView = () => (
  <div className="max-w-4xl mx-auto bg-[#1e293b] p-10 rounded-2xl border border-slate-700 fade-in text-slate-300">
    <h1 className="text-3xl font-bold text-slate-100 mb-2">PRIVACY POLICY</h1>
    <p className="text-sm text-slate-500">Last Updated: 01/08/2026</p>
  </div>
);

// --- Main App Shell ---
const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authView, setAuthView] = useState('login'); 
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);

  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  // New Chat Modal States
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [newChatMode, setNewChatMode] = useState('therapy'); 

  const fetchSessions = useCallback(async () => {
    try {
      const data = await api.request('/Chats/');
      setSessions(data);
    } catch (error) { console.error(error); }
  }, []);

  useEffect(() => {
    if (localStorage.getItem('access_token')) { 
      setIsAuthenticated(true); 
      fetchSessions();
    }
  }, [fetchSessions]);

  const handleLogin = () => { 
    setIsAuthenticated(true); 
    setCurrentView('dashboard'); 
    fetchSessions();
  };
  
  const handleLogout = () => { api.clearTokens(); setIsAuthenticated(false); setAuthView('login'); };

  const handleSessionClick = (sessionId) => {
    setActiveSessionId(sessionId);
    setCurrentView('chat');
  };

  const handleOpenChatModal = () => {
    setIsChatModalOpen(true);
    setNewChatTitle('');
    setNewChatMode('therapy');
  };

  const handleCreateNewChat = async (e) => {
    e.preventDefault();
    if (!newChatTitle.trim()) return;
    
    try {
      const response = await api.request('/Chats/', {
        method: 'POST',
        body: JSON.stringify({ 
          title: newChatTitle, 
          AiMode: newChatMode 
        })
      });
      
      setIsChatModalOpen(false);
      await fetchSessions();
      setActiveSessionId(response.id);
      setCurrentView('chat');
    } catch (err) {
      console.error("Failed to create chat", err);
      alert("Failed to create session");
    }
  };

  if (!isAuthenticated) {
    return (
      <>
        <GlobalStyles />
        {authView === 'login' 
          ? <Login onLogin={handleLogin} onSwitchToRegister={() => setAuthView('register')} />
          : <Register onRegister={() => setAuthView('login')} onSwitchToLogin={() => setAuthView('login')} />
        }
      </>
    );
  }

  const renderView = () => {
    switch(currentView) {
      case 'team': return <CompanyDashboard />; 
      case 'chat': return (
        <ChatInterface 
          activeSessionId={activeSessionId} 
          setActiveSessionId={setActiveSessionId}
          fetchSessions={fetchSessions}
        />
      );
      case 'feedback': return <FeedbackView />;
      case 'privacy': return <PrivacyPolicyView />;
      default: return <PersonalDashboard />;
    }
  };

  return (
    <>
      <GlobalStyles />
      <div className="flex flex-col h-screen overflow-hidden bg-[#0f172a] text-slate-100 font-sans">
        
        <header className="h-16 bg-[#0f172a] border-b border-slate-800 flex items-center justify-between px-6 z-20 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              <Activity className="text-white w-5 h-5" />
            </div>
            <h1 className="text-sm font-semibold tracking-wide text-slate-200">AI PSYCHOLOGIST</h1>
          </div>
          <div className="relative">
            <button onClick={() => setAccountMenuOpen(!accountMenuOpen)} className="flex items-center gap-3 hover:bg-slate-800 p-1.5 rounded-lg transition-colors group">
              <span className="text-sm text-slate-400 group-hover:text-slate-200 hidden sm:block">User Account</span>
              <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center">
                 <User size={16} className="text-slate-400" />
              </div>
            </button>
            {accountMenuOpen && (
              <div className="absolute right-0 mt-2 w-52 bg-[#1e293b] border border-slate-700 rounded-lg shadow-2xl py-1.5 z-50">
                <button onClick={handleLogout} className="w-full text-left flex items-center gap-3 px-4 py-2 text-sm text-rose-400 hover:bg-rose-500/10 transition-colors">
                  <LogOut size={16} /> Sign Out
                </button>
              </div>
            )}
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <aside className={`${sidebarCollapsed ? 'w-[72px]' : 'w-[260px]'} sidebar-transition bg-[#0f172a] border-r border-slate-800 flex flex-col z-10 shrink-0`}>
            <div className="p-3 flex flex-col gap-2 h-full">
              <button onClick={() => setSidebarCollapsed(!sidebarCollapsed)} className="w-full h-10 flex items-center justify-center hover:bg-slate-800 rounded-md text-slate-400 transition-colors mb-4">
                {sidebarCollapsed ? <Menu size={20} /> : <X size={20} />}
              </button>

              <div className="flex flex-col gap-1">
                 <button onClick={() => setCurrentView('dashboard')} className={`h-10 w-full rounded-md flex items-center px-3 transition-colors ${currentView === 'dashboard' ? 'bg-slate-800 text-indigo-400' : 'text-slate-400 hover:bg-slate-800 hover:text-indigo-400'}`}>
                   <LayoutDashboard size={20} />
                   <span className={`ml-3 text-sm font-medium whitespace-nowrap ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>Dashboard</span>
                 </button>

                 <button onClick={() => setCurrentView('team')} className={`h-10 w-full rounded-md flex items-center px-3 transition-colors ${currentView === 'team' ? 'bg-slate-800 text-indigo-400' : 'text-slate-400 hover:bg-slate-800 hover:text-indigo-400'}`}>
                   <Briefcase size={20} />
                   <span className={`ml-3 text-sm font-medium whitespace-nowrap ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>Company</span>
                 </button>

                 <button onClick={handleOpenChatModal} className={`h-10 w-full rounded-md flex items-center px-3 transition-colors ${currentView === 'chat' ? 'bg-slate-800 text-indigo-400' : 'text-slate-400 hover:bg-slate-800 hover:text-indigo-400'}`}>
                   <MessageSquare size={20} />
                   <span className={`ml-3 text-sm font-medium whitespace-nowrap ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>New Chat</span>
                 </button>

                 <button onClick={() => setCurrentView('feedback')} className={`h-10 w-full rounded-md flex items-center px-3 transition-colors ${currentView === 'feedback' ? 'bg-slate-800 text-indigo-400' : 'text-slate-400 hover:bg-slate-800 hover:text-indigo-400'}`}>
                   <ThumbsUp size={20} />
                   <span className={`ml-3 text-sm font-medium whitespace-nowrap ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>Feedback</span>
                 </button>
              </div>

              <div className="mt-6 flex-1 flex flex-col gap-2 overflow-hidden">
                <h3 className={`px-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1 ${sidebarCollapsed ? 'hidden' : 'block'}`}>
                  Recent Sessions
                </h3>
                <div className="flex-1 overflow-y-auto px-1 space-y-1 scrollbar-thin">
                  {sessions.map(session => (
                    <button
                      key={session.id}
                      onClick={() => handleSessionClick(session.id)}
                      className={`w-full h-10 rounded-md flex items-center px-3 transition-colors group ${activeSessionId === session.id && currentView === 'chat' ? 'bg-slate-800 text-indigo-400' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
                    >
                      <MessageSquare size={18} className="shrink-0" />
                      <span className={`ml-3 text-xs font-medium truncate ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>
                        {session.title}
                      </span>
                    </button>
                  ))}
                  {sessions.length === 0 && !sidebarCollapsed && (
                    <p className="px-3 text-[10px] text-slate-600 italic">No history</p>
                  )}
                </div>
              </div>

              <div className="mt-auto border-t border-slate-800 pt-2">
                 <button className="h-10 w-full rounded-md flex items-center px-3 text-slate-400 hover:bg-slate-800 hover:text-rose-400 transition-colors">
                    <User size={20} />
                    <span className={`ml-3 text-sm font-medium whitespace-nowrap ${sidebarCollapsed ? 'hidden opacity-0' : 'block opacity-100 sidebar-label'}`}>Human Help</span>
                 </button>
              </div>
            </div>
          </aside>
          <main className="flex-1 p-8 overflow-y-auto bg-[#0f172a] scrollbar-thin relative">
             {renderView()}
          </main>
        </div>
      </div>

      {/* New Chat Modal */}
      {isChatModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 fade-in">
          <div className="bg-[#1e293b] rounded-2xl p-8 w-full max-w-md shadow-2xl border border-slate-700 relative overflow-hidden">
            
            <div className="mb-8 text-center relative z-10">
              <h2 className="text-2xl font-bold text-white mb-2">Start New Session</h2>
              <p className="text-slate-400 text-sm">Choose your AI companion and set a topic</p>
            </div>

            <form onSubmit={handleCreateNewChat} className="space-y-6 relative z-10">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Session Name</label>
                <input 
                  type="text" 
                  required 
                  value={newChatTitle} 
                  onChange={e => setNewChatTitle(e.target.value)} 
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="e.g. Anxiety check-in, Career advice..."
                  autoFocus
                />
              </div>

              <div className="space-y-3">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Select Mode</label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setNewChatMode('therapy')}
                    className={`relative p-4 rounded-xl border flex flex-col items-center gap-3 transition-all duration-200 ${newChatMode === 'therapy' ? 'bg-indigo-600/10 border-indigo-500 ring-1 ring-indigo-500' : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-slate-600'}`}
                  >
                    <div className={`p-3 rounded-full ${newChatMode === 'therapy' ? 'bg-indigo-500 text-white' : 'bg-slate-700 text-slate-400'}`}>
                      <Stethoscope size={24} />
                    </div>
                    <span className={`text-sm font-semibold ${newChatMode === 'therapy' ? 'text-indigo-400' : 'text-slate-400'}`}>Therapy AI</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setNewChatMode('counsellor')}
                    className={`relative p-4 rounded-xl border flex flex-col items-center gap-3 transition-all duration-200 ${newChatMode === 'counsellor' ? 'bg-emerald-600/10 border-emerald-500 ring-1 ring-emerald-500' : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-slate-600'}`}
                  >
                    <div className={`p-3 rounded-full ${newChatMode === 'counsellor' ? 'bg-emerald-500 text-white' : 'bg-slate-700 text-slate-400'}`}>
                      <HeartHandshake size={24} />
                    </div>
                    <span className={`text-sm font-semibold ${newChatMode === 'counsellor' ? 'text-emerald-400' : 'text-slate-400'}`}>Counsellor AI</span>
                  </button>
                </div>
              </div>

              <div className="flex gap-3 mt-8 pt-2">
                <button 
                  type="button" 
                  onClick={() => setIsChatModalOpen(false)} 
                  className="flex-1 py-3.5 rounded-xl border border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white font-medium transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="flex-1 py-3.5 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-500 shadow-lg shadow-indigo-500/25 transition-all transform active:scale-95"
                >
                  Start Chat
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default App;