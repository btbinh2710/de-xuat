const API_URL = 'https://de-xuat-backend-s1mk.onrender.com/api';
let currentUser = null;

function showLoginForm() {
    console.log('showLoginForm');
    document.getElementById('mainContent').classList.add('hidden');
    document.getElementById('loginFormContainer').classList.remove('hidden');
    document.getElementById('loginForm')?.reset();
    const errorElement = document.getElementById('loginError');
    if (errorElement) {
        errorElement.classList.add('hidden');
    }
}

function showLoginError(message) {
    console.log('showLoginError:', message);
    Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: "#dc3545",
        stopOnFocus: true,
    }).showToast();
}

function handleLogin() {
    console.log('handleLogin');
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginButton = document.querySelector('#loginForm input[type="submit"]');
    const spinner = document.getElementById('loginSpinner');
    
    console.log('Đăng nhập với username:', username);
    
    // Hiển thị spinner và vô hiệu hóa nút
    loginButton.disabled = true;
    spinner.classList.remove('hidden');
    
    axios.post(`${API_URL}/login`, { username, password })
        .then(response => {
            console.log('Đăng nhập thành công:', response.data);
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('username', username);
            localStorage.setItem('branch', response.data.branch);
            localStorage.setItem('role', response.data.role);
            currentUser = {
                username: username,
                branch: response.data.branch,
                role: response.data.role
            };
            document.getElementById('loginFormContainer').classList.add('hidden');
            document.getElementById('mainContent').classList.remove('hidden');
            document.getElementById('userName').textContent = `Người dùng: ${username}`;
            document.getElementById('userBranch').textContent = currentUser.role === 'accountant' ? 'Kế toán' : `Chi nhánh: ${currentUser.branch}`;
            Toastify({
                text: `Đăng nhập thành công với tài khoản ${username}!`,
                duration: 3000,
                close: true,
                gravity: "top",
                position: "right",
                backgroundColor: "#28a745",
                stopOnFocus: true,
            }).showToast();
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi đăng nhập:', error.message);
            showLoginError(error.response?.data?.message || 'Lỗi đăng nhập!');
        })
        .finally(() => {
            // Ẩn spinner và kích hoạt lại nút
            loginButton.disabled = false;
            spinner.classList.add('hidden');
        });
}

function validateToken(token) {
    console.log('validateToken:', token);
    axios.get(`${API_URL}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(response => {
            console.log('Xác thực token thành công');
            const username = localStorage.getItem('username');
            const branch = localStorage.getItem('branch');
            const role = localStorage.getItem('role');
            if (!username || !branch || !role) {
                console.error('Lỗi: Thiếu thông tin người dùng trong localStorage');
                localStorage.clear();
                showLoginForm();
                return;
            }
            currentUser = { username, branch, role };
            document.getElementById('loginFormContainer').classList.add('hidden');
            document.getElementById('mainContent').classList.remove('hidden');
            document.getElementById('userName').textContent = `Người dùng: ${username}`;
            document.getElementById('userBranch').textContent = currentUser.role === 'accountant' ? 'Kế toán' : `Chi nhánh: ${currentUser.branch}`;
            console.log('currentUser:', currentUser);
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi xác thực token:', error.message);
            localStorage.clear();
            showLoginForm();
        });
}