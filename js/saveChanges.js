function saveEditChanges(modal) {
    console.log('saveEditChanges');
    const form = document.getElementById('editForm');
    if (!form || !form.checkValidity()) {
        console.error('Lỗi: Form không hợp lệ hoặc không tồn tại');
        form.reportValidity();
        return;
    }

    const proposalId = parseInt(document.getElementById('editProposalId').value);
    const completed = document.getElementById('editCompleted').value;
    const updatedProposal = {
        proposer: document.getElementById('editProposer').value,
        room: document.getElementById('editRoom').value,
        department: document.getElementById('editDepartment').value,
        date: document.getElementById('editDate').value,
        code: document.getElementById('editCode').value,
        content: document.getElementById('editContent').value,
        purpose: document.getElementById('editPurpose').value,
        supplier: document.getElementById('editSupplier').value,
        estimated_cost: parseFloat(document.getElementById('editEstimatedCost').value) || 0,
        approved_amount: document.getElementById('editApprovedAmount').value ? parseFloat(document.getElementById('editApprovedAmount').value) : null,
        transfer_code: document.getElementById('editTransferCode').value || null,
        payment_date: document.getElementById('editPaymentDate').value || null,
        notes: document.getElementById('editNotes').value || null,
        status: document.getElementById('editStatus').value || null,
        approver: document.getElementById('editApprover').value || null,
        approval_date: document.getElementById('editApprovalDate').value || null,
        completed: completed
    };
    console.log('Dữ liệu cập nhật đề xuất:', updatedProposal);

    const token = localStorage.getItem('token');
    axios.put(`${API_URL}/proposals/${proposalId}`, updatedProposal, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(() => {
            console.log('Cập nhật đề xuất thành công');
            modal.hide();
            alert('Đã cập nhật đề xuất!');
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi khi cập nhật:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi cập nhật');
        });
}