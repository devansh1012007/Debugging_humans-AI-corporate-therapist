
// CONFIGURATION
const API_BASE = 'http://127.0.0.1:8000'; // Change this to your backend URL

// STATE
let currentChatId = null;
let currentUser = null;
// --- AUTHENTICATION ---
// Check if logged in on load
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        showApp();
    } else {
        showLogin();
    }
});
// INTEGRATED LOGIN LOGIC (Matches your snippet structure)
const loginForm = document.querySelector('.login-form');
const showLoginLink = document.getElementById('showLogin');
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Note: Preserving your ID spelling 'loginUserame'
    const username = document.getElementById('loginUserame').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    // Basic validation
    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    console.log('Login attempt:', { username, rememberMe });
    // API Call
    try {
        const response = await fetch(`${API_BASE}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (!response.ok) {
            throw new Error('Login failed: Invalid credentials');
        }
        const data = await response.json();
        
        // Store tokens
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        localStorage.setItem('username', username);
        // UI Updates
        showToast('Login successful!');
        this.reset();
        showApp();
    } catch (err) {
        console.error(err);
        showToast(err.message);
    }
});
function logout() {
    localStorage.clear();
    showLogin();
}
// --- API HELPERS ---
async function authenticatedFetch(endpoint, options = {}) {
    let token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });
    if (response.status === 401) {
        // Token expired - simple logout handling for now
        logout();
        throw new Error("Session expired");
    }
    return response;
}
// --- UI NAVIGATION ---
function showLogin() {
    document.getElementById('login-view').classList.remove('hidden');
    document.getElementById('app-view').classList.add('hidden');
}
function showApp() {
    document.getElementById('login-view').classList.add('hidden');
    document.getElementById('app-view').classList.remove('hidden');
    document.getElementById('current-user-display').textContent = localStorage.getItem('username') || 'User';
    
    // Load initial data
    loadChatHistory();
}
function switchTab(tabName) {
    // Reset Sidebar styles
    document.getElementById('nav-chat').className = "block px-4 py-2 hover:bg-gray-800 text-gray-300 border-l-4 border-transparent hover:border-indigo-500 transition";
    document.getElementById('nav-dashboard').className = "block px-4 py-2 hover:bg-gray-800 text-gray-300 border-l-4 border-transparent hover:border-indigo-500 transition";
    // Hide all tabs
    document.getElementById('tab-chat').classList.add('hidden');
    document.getElementById('tab-dashboard').classList.add('hidden');
    // Show selected
    document.getElementById(`tab-${tabName}`).classList.remove('hidden');
    if (tabName === 'chat') {
        document.getElementById('nav-chat').className = "block px-4 py-2 bg-gray-800 text-white border-l-4 border-indigo-500";
    } else {
        document.getElementById('nav-dashboard').className = "block px-4 py-2 bg-gray-800 text-white border-l-4 border-indigo-500";
        loadTeamDashboard();
    }
}
function showToast(msg) {
    const toast = document.getElementById('toast');
    document.getElementById('toast-msg').innerText = msg;
    toast.classList.remove('translate-x-full');
    setTimeout(() => toast.classList.add('translate-x-full'), 3000);
}
