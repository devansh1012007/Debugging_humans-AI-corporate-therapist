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
const API_BASE = 'http://localhost:8000'; 

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
const PersonalDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedCard, setExpandedCard] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.request('/UserPsycoDataViewSet/');
        setData(response[0] || null); 
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleCard = (index) => setExpandedCard(expandedCard === index ? null : index);

  if (loading) return <div className="text-center text-slate-500 mt-10">Loading insights...</div>;
  if (!data) return <div className="text-center text-slate-500 mt-10">No personal data available.</div>;

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 fade-in h-[calc(100vh-8rem)]">
      <div className="flex flex-col h-full overflow-hidden">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Personal Patterns</h2>
        <div className="flex-1 overflow-y-auto pr-2 space-y-4 scrollbar-thin">
           {data.common_problems && data.common_problems.map((item, idx) => (
             <div key={idx} className="bg-[#1e293b] border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors">
               <h3 className="text-sm font-medium text-slate-200">{item.problem}</h3>
             </div>
           ))}
        </div>
      </div>
      <div className="flex flex-col h-full gap-6 overflow-hidden">
         <div className="flex-1 flex flex-col min-h-0">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Recommendations</h2>
            <div className="flex-1 overflow-y-auto pr-2 bg-[#1e293b] border border-slate-700 rounded-lg scrollbar-thin">
              {data.recommendation && data.recommendation.map((item, idx) => (
                <div key={idx} className="border-b border-slate-700/50 last:border-0">
                  <div onClick={() => toggleCard(idx)} className="p-4 cursor-pointer hover:bg-slate-700/30 transition-colors flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${idx % 3 === 0 ? 'bg-indigo-500' : idx % 3 === 1 ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
                        <span className="text-sm font-medium text-slate-200">{item.recommendation}</span>
                    </div>
                    {expandedCard === idx ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                  </div>
                  {expandedCard === idx && (
                    <div className="px-9 pb-4 pt-0">
                      <p className="text-sm text-slate-400">Actionable insight: {item.recommendation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
         </div>
         <div className="shrink-0">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Current Status</h2>
            <div className="bg-[#1e293b] border border-slate-700 rounded-lg p-6">
               <h3 className="text-3xl font-bold text-slate-100 mb-4">Well-being Status</h3>
               <p className="text-slate-300 text-lg leading-relaxed italic border-l-2 border-indigo-500 pl-6">"{data.summary}"</p>
            </div>
         </div>
      </div>
    </div>
  );
};

// --- DYNAMIC Company Dashboard (REFACTORED FOR TEAM CARDS) ---
const CompanyDashboard = () => {
  const [companyData, setCompanyData] = useState(null);
  const [teamData, setTeamData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Accordion states
  const [activeRec, setActiveRec] = useState(null);
  const [activePol, setActivePol] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [compRes, teamRes] = await Promise.all([
          api.request('/CompanyData/').catch(() => null),
          api.request('/TeamData/').catch(() => [])
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

  if (loading) return <div className="text-center text-slate-500 mt-10">Loading enterprise data...</div>;

  return (
    <div className="max-w-7xl mx-auto fade-in h-full flex flex-col gap-8 pb-8">
      {/* Top Section: Split View (Enterprise Challenges vs Recs/Policies) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-20rem)] min-h-[500px]">
        
        {/* Left: Enterprise Challenges */}
        <div className="flex flex-col h-full overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Enterprise Challenges</h2>
            <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold rounded border border-indigo-500/20">Active Analysis</span>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4 scrollbar-thin">
              {companyData?.challenges?.length > 0 ? (
                companyData.challenges.map((item, idx) => (
                  <div key={idx} className="bg-[#1e293b] border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors group">
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
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Strategic Recommendations</h2>
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
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Policy Changes</h2>
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

      {/* Bottom Section: Individual Team Analysis (NEW LAYOUT) */}
      <div className="mt-8 space-y-10">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-6">Detailed Team Breakdown</h2>
        
        {teamData.map((team, idx) => (
          <div key={idx} className="bg-[#1e293b]/20 border border-slate-800 rounded-[2rem] p-8 fade-in shadow-xl">
            
            {/* Team Header */}
            <div className="flex items-center gap-3 mb-8 px-2">
              <div className="p-2 bg-indigo-500/10 rounded-lg">
                <Users className="text-indigo-400" size={20} />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">{team.name || `Team ${idx + 1}`}</h3>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Left Column: Systemic Team Patterns (1/3 Width) */}
              <div className="lg:col-span-4 space-y-4">
                <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 ml-1">Systemic Team Patterns</h4>
                {team.common_problems?.map((p, i) => (
                  <div key={i} className="bg-[#1e293b] border border-slate-700/50 p-6 rounded-2xl hover:border-slate-600 transition-colors">
                    <h5 className="text-sm font-bold text-slate-200 mb-2">{p.problem}</h5>
                    <p className="text-xs text-slate-400 leading-relaxed">{p.description || "Pattern analysis in progress."}</p>
                  </div>
                ))}
              </div>

              {/* Right Column: Recommendations and Health (2/3 Width) */}
              <div className="lg:col-span-8 flex flex-col gap-6">
                
                {/* Top: Leadership Recommendations */}
                <div className="bg-[#1e293b] border border-slate-700/50 rounded-2xl overflow-hidden">
                  <div className="p-4 bg-slate-800/30 border-b border-slate-700/50">
                    <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Leadership Recommendations</h4>
                  </div>
                  <div className="divide-y divide-slate-700/50">
                    {team.recommendations?.map((rec, i) => (
                      <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-700/30 transition-colors cursor-pointer group">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]" />
                          <span className="text-sm font-medium text-slate-200 group-hover:text-white">{rec.recommendation}</span>
                        </div>
                        <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400" />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bottom: Team Health (Scores Removed) */}
                <div className="bg-[#1e293b] border border-slate-700/50 rounded-2xl p-8 flex flex-col justify-center min-h-[200px]">
                  <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6">Overall Team Health</h4>
                  
                  <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-indigo-500 to-purple-500 rounded-full" />
                    <p className="text-slate-300 text-lg leading-relaxed italic pl-8 pr-4">
                      "{team.summary || "Health data is being synthesized from current team activity."}"
                    </p>
                  </div>

                  <div className="flex gap-2 mt-8">
                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                      team.status === 'Critical' 
                      ? 'bg-red-500/10 border-red-500/20 text-red-400' 
                      : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    }`}>
                      {team.status || 'Stable Performance'}
                    </span>
                    <span className="px-4 py-1.5 bg-slate-700/30 border border-slate-600/30 rounded-full text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Active Analysis
                    </span>
                  </div>
                </div>

              </div>
            </div>
          </div>
        ))}
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