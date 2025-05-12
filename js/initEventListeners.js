document.addEventListener("DOMContentLoaded", function() {
    console.log('DOMContentLoaded');
    const token = localStorage.getItem('token');
    if (token) {
        console.log('Tìm thấy token, bắt đầu validateToken');
        validateToken(token);
    } else {
        console.log('Không có token, hiển thị form đăng nhập');
        showLoginForm();
    }

    document.getElementById('loginForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });

    document.getElementById('logoutBtn')?.addEventListener('click', function() {
        console.log('Đăng xuất');
        localStorage.clear();
        currentUser = null;
        showLoginForm();
    });

    document.getElementById('searchBtn')?.addEventListener('click', applySearch);

    document.getElementById('clearSearchBtn')?.addEventListener('click', function() {
        console.log('Xóa tìm kiếm');
        document.getElementById('searchInput').value = '';
        applySearch();
    });

    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', function() {
            console.log('Sắp xếp:', this.getAttribute('data-sort'));
            sortTable(this.getAttribute('data-sort'));
        });
    });

    document.getElementById('confirmUploadBtn')?.addEventListener('click', handleExcelUpload);

    document.getElementById('downloadTemplateBtn')?.addEventListener('click', downloadExcelTemplate);

    document.getElementById('exportXDVBtn')?.addEventListener('click', function() {
        console.log('Xuất báo cáo XDV');
        exportSummaryReport('XDV');
    });

    document.getElementById('exportPTTBtn')?.addEventListener('click', function() {
        console.log('Xuất báo cáo PTT');
        exportSummaryReport('PTT');
    });

    document.getElementById('confirmDeleteBtn')?.addEventListener('click', function() {
        const proposalId = parseInt(this.getAttribute('data-id'));
        console.log('Xác nhận xóa đề xuất:', proposalId);
        if (!isNaN(proposalId)) {
            deleteProposal(proposalId);
        }
    });

    document.getElementById('saveEditBtn')?.addEventListener('click', function() {
        console.log('Lưu chỉnh sửa đề xuất');
        saveEditChanges(bootstrap.Modal.getInstance(document.getElementById('editModal')));
    });

    const uploadModal = document.getElementById('uploadModal');
    uploadModal.addEventListener('hidden.bs.modal', function () {
        console.log('Modal upload đóng');
        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.focus();
        }
    });
});