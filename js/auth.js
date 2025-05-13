async function checkTokenValidity() {
    console.log('checkTokenValidity');
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Lỗi: Không có token trong localStorage');
        return false;
    }
    try {
        await axios.get(`${API_URL}/proposals`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log('Token hợp lệ');
        return true;
    } catch (error) {
        const errMsg = error.response?.data?.message || 'Unknown error';
        console.error('Lỗi xác thực token:', errMsg);
        if (errMsg.includes('Token expired') || errMsg.includes('Invalid token')) {
            localStorage.clear();
            currentUser = null;
            showLoginForm();
            alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        }
        return false;
    }
}

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
    const errorElement = document.getElementById('loginError');
    if (!errorElement) {
        console.error('Lỗi: Không tìm thấy loginError trong DOM');
        alert('Lỗi giao diện: Không thể hiển thị thông báo lỗi. Vui lòng thử lại.');
        return;
    }
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

function handleLogin() {
    console.log('handleLogin');
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    console.log('Đăng nhập với username:', username);
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
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi đăng nhập:', error.message);
            showLoginError(error.response?.data?.message || 'Lỗi đăng nhập!');
        });
}

function validateToken(token) {
    console.log('validateToken:', token);
    axios.get(`${API_URL}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(response => {
            console.log('Xác thực token thành công');
            const userData = {
                username: localStorage.getItem('username'),
                branch: localStorage.getItem('branch'),
                role: localStorage.getItem('role')
            };
            if (!userData.username || !userData.role) {
                throw new Error('Thông tin người dùng không đầy đủ trong localStorage');
            }
            currentUser = userData;
            console.log('currentUser:', currentUser);
            document.getElementById('mainContent').classList.remove('hidden');
            document.getElementById('loginFormContainer').classList.add('hidden');
            document.getElementById('userName').textContent = `Người dùng: ${currentUser.username}`;
            document.getElementById('userBranch').textContent = currentUser.role === 'accountant' ? 'Kế toán' : `Chi nhánh: ${currentUser.branch}`;
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi xác thực token:', error.message);
            localStorage.clear();
            showLoginForm();
            alert(error.response?.data?.message || 'Lỗi xác thực token');
        });
}