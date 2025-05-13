function loadProposalData() {
    console.log('loadProposalData');
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Lỗi: Không có token, chuyển về form đăng nhập');
        showLoginForm();
        return;
    }
    axios.get(`${API_URL}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(response => {
            console.log('Tải dữ liệu đề xuất thành công:', response.data);
            proposals = response.data;
            filteredProposals = [...proposals];
            sortData();
            renderTable();
            renderPagination();
        })
        .catch(error => {
            console.error('Lỗi khi tải dữ liệu:', error.message);
            let errMsg = 'Lỗi không xác định';
            if (error.response) {
                errMsg = error.response.data?.message || 'Lỗi server';
                if (errMsg.includes('Token expired') || errMsg.includes('Invalid token')) {
                    localStorage.clear();
                    showLoginForm();
                    alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
                }
            } else {
                errMsg = error.message;
            }
            alert(`Lỗi khi tải dữ liệu: ${errMsg}`);
        });
}