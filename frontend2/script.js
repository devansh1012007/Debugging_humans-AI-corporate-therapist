const container = document.getElementById("container");
const registerBtn = document.getElementById("register");
const loginBtn = document.getElementById("login");

// --- UI Toggles ---
registerBtn.addEventListener("click", () => container.classList.add("active"));
loginBtn.addEventListener("click", () => container.classList.remove("active"));

// --- Google Initialization ---
window.onload = function () {
    google.accounts.id.initialize({
        client_id: "931160189506-mv2b13sg9r1l853c381e262k00bqlqqt.apps.googleusercontent.com",
        callback: handleGoogleResponse
    });

    const btnOptions = { theme: "outline", size: "large", width: "250" };
    google.accounts.id.renderButton(document.getElementById("googleSignInButton"), btnOptions);
    google.accounts.id.renderButton(document.getElementById("googleSignUpButton"), btnOptions);

    // Auto-load profile if tokens exist
    if (localStorage.getItem('accessToken')) {
        displayUserProfile();
    }
};

// --- Authentication Handlers ---
async function handleGoogleResponse(response) {
    const res = await fetch('http://localhost:8000/api/auth/google/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: response.credential })
    });
    
    const data = await res.json();
    //console.log("Backend Response:", data);
    if (res.ok) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        displayUserProfile(); 
    }
}

document.getElementById('signInForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    const password = e.target.querySelector('input[type="password"]').value;
    
    const res = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password: password })
    });
    
    const data = await res.json();
    if (res.ok) {
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        displayUserProfile();
    } else {
        alert("Login Failed: " + (data.detail || "Check credentials"));
    }
});

// --- UI & Token Helpers ---
async function displayUserProfile() {
    const response = await authorizedFetch('http://localhost:8000/Chats/');//const response = await authorizedFetch('http://localhost:8000/api/profile/');
    if (response.ok) {
        const userData = await response.json();
        /*
        // Show Profile UI and set email
        document.getElementById('userProfile').style.display = 'flex';
        document.getElementById('userEmailDisplay').textContent = userData.email;
        */
        // Hide Login UI
        document.querySelector('.sign-in').style.display = 'none';
        document.querySelector('.sign-up').style.display = 'none';
        document.querySelector('.toggle-container').style.display = 'none';
    }
}

function logout() {
    localStorage.clear();
    window.location.reload();
}

// --- JWT Authorized Fetch ---
async function authorizedFetch(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    options.headers = { ...options.headers, 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    
    let response = await fetch(url, options);
    if (response.status === 401) {
        const newToken = await refreshAccessToken();
        if (newToken) {
            options.headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, options);
        }
    }
    return response;
}

async function refreshAccessToken() {
    const refresh = localStorage.getItem('refreshToken');
    if (!refresh) return null;
    const res = await fetch('http://localhost:8000/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
    });
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('accessToken', data.access);
        return data.access;
    }
    return null;
}