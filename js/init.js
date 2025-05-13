const API_URL = 'https://de-xuat-ea0h.onrender.com/api';
let currentUser = null;
let proposals = [];
let filteredProposals = [];
let currentPage = 1;
const itemsPerPage = 10;
let currentSortColumn = '';
let currentSortDirection = 'asc';

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDateToDDMMYYYY(dateStr) {
    console.log('formatDateToDDMMYYYY:', dateStr);
    if (!dateStr) return '';
    if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        const [year, month, day] = dateStr.split('-');
        return `${day}/${month}/${year}`;
    }
    if (dateStr.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        return dateStr;
    }
    try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return '';
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    } catch {
        return '';
    }
}

function formatDateToYYYYMMDD(dateStr) {
    console.log('formatDateToYYYYMMDD:', dateStr);
    if (!dateStr) return '';
    if (dateStr.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month}-${day}`;
    }
    return dateStr;
}

function getStatusFromCompleted(completed) {
    console.log('getStatusFromCompleted:', completed);
    return completed === 'Yes' ? 'Đã xong' : 'Đang xử lý';
}

function showUploadError(message) {
    console.log('showUploadError:', message);
    const errorElement = document.getElementById('uploadError');
    const successElement = document.getElementById('uploadSuccess');
    if (!errorElement || !successElement) {
        console.error('Lỗi: Không tìm thấy uploadError hoặc uploadSuccess trong DOM');
        alert('Lỗi giao diện: Không thể hiển thị thông báo lỗi. Vui lòng thử lại.');
        return;
    }
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
    successElement.classList.add('hidden');
}

function showUploadSuccess(message) {
    console.log('showUploadSuccess:', message);
    const errorElement = document.getElementById('uploadError');
    const successElement = document.getElementById('uploadSuccess');
    if (!errorElement || !successElement) {
        console.error('Lỗi: Không tìm thấy uploadError hoặc uploadSuccess trong DOM');
        alert('Lỗi giao diện: Không thể hiển thị thông báo thành công. Vui lòng thử lại.');
        return;
    }
    successElement.textContent = message;
    successElement.classList.remove('hidden');
    errorElement.classList.add('hidden');
    setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
        if (modal) modal.hide();
    }, 2000);
}