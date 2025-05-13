async function openDeleteModal(proposalId) {
    console.log('openDeleteModal:', proposalId);
    const tokenValid = await checkTokenValidity();
    if (!tokenValid) {
        console.error('Lỗi: Token không hợp lệ');
        return;
    }

    if (currentUser.role === 'accountant') {
        console.error('Lỗi: Tài khoản kế toán không có quyền xóa');
        alert('Tài khoản kế toán không có quyền xóa đề xuất!');
        return;
    }

    const token = localStorage.getItem('token');
    axios.get(`${API_URL}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(response => {
            console.log('Tải dữ liệu đề xuất để xóa:', response.data);
            const proposal = response.data.find(p => p.id === proposalId);
            if (!proposal) {
                console.error('Lỗi: Đề xuất không tồn tại');
                alert('Đề xuất không tồn tại!');
                return;
            }
            document.getElementById('deleteModalContent').innerHTML = `
                <strong>Người đề nghị:</strong> ${sanitizeHTML(proposal.proposer || '')}<br>
                <strong>Nội dung:</strong> ${sanitizeHTML(proposal.content || '')}<br>
                <strong>Chi nhánh:</strong> ${sanitizeHTML(proposal.branch || '')}
            `;
            document.getElementById('confirmDeleteBtn').setAttribute('data-id', proposalId);
            console.log('Mở modal xóa');
            new bootstrap.Modal(document.getElementById('deleteModal')).show();
        })
        .catch(error => {
            console.error('Lỗi khi tải đề xuất:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi tải đề xuất');
        });
}

async function deleteProposal(proposalId) {
    console.log('deleteProposal:', proposalId);
    const tokenValid = await checkTokenValidity();
    if (!tokenValid) {
        console.error('Lỗi: Token không hợp lệ');
        return;
    }

    const token = localStorage.getItem('token');
    axios.delete(`${API_URL}/proposals/${proposalId}`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(() => {
            console.log('Xóa đề xuất thành công');
            bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();
            alert('Đã xóa đề xuất!');
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi khi xóa:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi xóa');
        });
}