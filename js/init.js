function initializeApp() {
    console.log('initializeApp');
    const token = localStorage.getItem('token');
    if (token) {
        validateToken(token);
    } else {
        console.log('Không có token, hiển thị form đăng nhập');
        showLoginForm();
    }

    // Ẩn/hiển thị các nút dựa trên vai trò người dùng
    const role = localStorage.getItem('role');
    const buttons = document.querySelectorAll('[data-role]');
    buttons.forEach(button => {
        const buttonRole = button.getAttribute('data-role');
        if (buttonRole === 'non-accountant' && role === 'accountant') {
            button.style.display = 'none';
        } else if (buttonRole === 'accountant' && role !== 'accountant') {
            button.style.display = 'none';
        } else if (buttonRole === 'all') {
            button.style.display = 'inline-block';
        }
    });
}