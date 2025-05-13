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
        if (buttonRole === 'accountant' && role !== 'accountant') {
            button.style.display = 'none';
        } else if (buttonRole === 'all') {
            button.style.display = 'inline-block';
        }
    });
}

function formatDateToDDMMYYYY(date) {
    if (!date || date === 'null' || date === null) {
        console.log('formatDateToDDMMYYYY: Ngày không hợp lệ, trả về rỗng');
        return '';
    }
    console.log('formatDateToDDMMYYYY:', date);
    const d = new Date(date);
    if (isNaN(d.getTime())) {
        return '';
    }
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

function getStatusFromCompleted(completed) {
    console.log('getStatusFromCompleted:', completed);
    if (!completed || completed === 'No' || completed === 'X') {
        return 'Đang xử lý';
    }
    if (completed === 'Yes' || completed === 'O') {
        return 'Hoàn thành';
    }
    return 'Đang xử lý'; // Giá trị mặc định nếu completed không xác định
}