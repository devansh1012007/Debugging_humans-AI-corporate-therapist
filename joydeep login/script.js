// Get form elements
const loginForm = document.querySelector('.login-form');
const showLoginLink = document.getElementById('showLogin');

// Handle login form submission
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUserame').value;
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    // Basic validation
    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }
    
    // send data to the server here
    console.log('Login attempt:', {
        username: username,
        password: password,
        rememberMe: rememberMe
    });
    
    alert('Login successful! (This is a demo)');
    
    // Clear form
    this.reset();
});

