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

        // Gắn sự kiện cho form đăng nhập
        document.getElementById('loginForm')?.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form đăng nhập được submit');
            handleLogin();
        });

        // Gắn sự kiện cho nút đăng xuất
        document.getElementById('logoutBtn')?.addEventListener('click', function() {
            console.log('Đăng xuất');
            localStorage.clear();
            currentUser = null;
            showLoginForm();
        });

        // Gắn sự kiện cho nút tìm kiếm
        document.getElementById('searchBtn')?.addEventListener('click', applySearch);

        // Gắn sự kiện cho nút xóa tìm kiếm
        document.getElementById('clearSearchBtn')?.addEventListener('click', function() {
            console.log('Xóa tìm kiếm');
            document.getElementById('searchInput').value = '';
            applySearch();
        });

        // Gắn sự kiện cho các tiêu đề cột để sắp xếp
        document.querySelectorAll('th[data-sort]').forEach(th => {
            th.addEventListener('click', function() {
                console.log('Sắp xếp:', this.getAttribute('data-sort'));
                sortTable(this.getAttribute('data-sort'));
            });
        });

        // Gắn sự kiện cho nút upload Excel
        document.getElementById('confirmUploadBtn')?.addEventListener('click', handleExcelUpload);

        // Gắn sự kiện cho nút tải mẫu Excel
        document.getElementById('downloadTemplateBtn')?.addEventListener('click', downloadExcelTemplate);

        // Gắn sự kiện cho nút xuất báo cáo XDV
        document.getElementById('exportXDVBtn')?.addEventListener('click', function() {
            console.log('Xuất báo cáo XDV');
            exportSummaryReport('XDV');
        });

        // Gắn sự kiện cho nút xuất báo cáo PTT
        document.getElementById('exportPTTBtn')?.addEventListener('click', function() {
            console.log('Xuất báo cáo PTT');
            exportSummaryReport('PTT');
        });

        // Gắn sự kiện cho nút xác nhận xóa
        document.getElementById('confirmDeleteBtn')?.addEventListener('click', function() {
            const proposalId = parseInt(this.getAttribute('data-id'));
            console.log('Xác nhận xóa đề xuất:', proposalId);
            if (!isNaN(proposalId)) {
                deleteProposal(proposalId);
            }
        });

        // Gắn sự kiện cho nút lưu chỉnh sửa
        document.getElementById('saveEditBtn')?.addEventListener('click', function() {
            console.log('Lưu chỉnh sửa đề xuất');
            saveEditChanges(bootstrap.Modal.getInstance(document.getElementById('editModal')));
        });

        // Gắn sự kiện khi modal upload đóng
        const uploadModal = document.getElementById('uploadModal');
        uploadModal?.addEventListener('hidden.bs.modal', function() {
            console.log('Modal upload đóng');
            const uploadBtn = document.getElementById('uploadBtn');
            if (uploadBtn) {
                uploadBtn.focus();
            }
        });
    });