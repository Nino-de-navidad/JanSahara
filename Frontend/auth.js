const API_BASE_URL = 'http://localhost:5000';

function showMessage(message, type = 'error') {
  const box = document.getElementById('message');
  if (!box) return;
  box.textContent = message;
  box.className = `message ${type}`;
}

function setLoading(button, loading, text) {
  if (!button) return;
  button.disabled = loading;
  button.textContent = loading ? 'Please wait...' : text;
}

// Password visibility
for (const button of document.querySelectorAll('.toggle-pass')) {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.target);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    button.textContent = input.type === 'password' ? 'Show' : 'Hide';
  });
}

// Registration
const registerForm = document.getElementById('registerForm');
registerForm?.addEventListener('submit', async (event) => {
  event.preventDefault();

  const email = document.getElementById('email').value.trim().toLowerCase();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const button = registerForm.querySelector('.submit');

  if (password.length < 6) {
    showMessage('Password must contain at least 6 characters.');
    return;
  }

  if (password !== confirmPassword) {
    showMessage('Passwords do not match.');
    return;
  }

  setLoading(button, true, 'Create Account');
  showMessage('Creating your account...', 'info');

  try {
    const response = await fetch(`${API_BASE_URL}/api/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok || data.status !== 'success') {
      throw new Error(data.message || 'Registration failed.');
    }

    localStorage.setItem('jansahara_user_id', data.user_id);
    localStorage.setItem('jansahara_email', email);

    showMessage(`Account created successfully. Your User ID is ${data.user_id}. Please sign in to complete your profile.`, 'success');

    setTimeout(() => {
      window.location.href = 'login.html';
    }, 1200);
  } catch (error) {
    showMessage(error.message || 'Unable to connect to JanSahara server.');
  } finally {
    setLoading(button, false, 'Create Account');
  }
});

// Login
const loginForm = document.getElementById('loginForm');
loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();

  const email = document.getElementById('email').value.trim().toLowerCase();
  const password = document.getElementById('password').value;
  const remember = document.getElementById('remember')?.checked;
  const button = loginForm.querySelector('.submit');

  setLoading(button, true, 'Sign In');
  showMessage('Signing you in...', 'info');

  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok || data.status !== 'success') {
      throw new Error(data.message || 'Login failed.');
    }

    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('jansahara_user_id', data.user_id);
    storage.setItem('jansahara_email', data.email);

    // Remove an older session so the two storage mechanisms cannot conflict.
    (remember ? sessionStorage : localStorage).removeItem('jansahara_user_id');
    (remember ? sessionStorage : localStorage).removeItem('jansahara_email');

    showMessage('Login successful. Opening your dashboard...', 'success');

    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 700);
  } catch (error) {
    showMessage(error.message || 'Unable to connect to JanSahara server.');
  } finally {
    setLoading(button, false, 'Sign In');
  }
});

// Forgot password is not implemented in the Flask API yet.
document.getElementById('forgot')?.addEventListener('click', (event) => {
  event.preventDefault();
  showMessage('Password recovery will be added in a later stage.', 'info');
});
