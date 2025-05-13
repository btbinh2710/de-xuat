function openEditModal(proposalId) {
    console.log('openEditModal:', proposalId);
    const token = localStorage.getItem('token');
    axios.get(`${API_URL}/proposals`, { headers: { Authorization: `Bearer ${token}` } })
        .then(response => {
            console.log('Tải dữ liệu đề xuất để chỉnh sửa:', response.data);
            const proposal = response.data.find(p => p.id === proposalId);
            if (!proposal) {
                console.error('Lỗi: Đề xuất không tồn tại');
                alert('Đề xuất không tồn tại!');
                return;
            }
            document.getElementById('editProposalId').value = proposal.id;
            document.getElementById('editProposer').value = proposal.proposer || '';
            document.getElementById('editRoom').value = proposal.room || '';
            document.getElementById('editBranch').value = proposal.branch || '';
            document.getElementById('editDepartment').value = proposal.department || '';
            document.getElementById('editDate').value = formatDateToDDMMYYYY(proposal.date) || '';
            document.getElementById('editCode').value = proposal.code || '';
            document.getElementById('editContent').value = proposal.content || '';
            document.getElementById('editPurpose').value = proposal.purpose || '';
            document.getElementById('editSupplier').value = proposal.supplier || '';
            document.getElementById('editEstimatedCost').value = proposal.estimated_cost || 0;
            document.getElementById('editApprovedAmount').value = proposal.approved_amount || '';
            document.getElementById('editTransferCode').value = proposal.transfer_code || '';
            document.getElementById('editPaymentDate').value = formatDateToDDMMYYYY(proposal.payment_date) || '';
            document.getElementById('editStatus').value = getStatusFromCompleted(proposal.completed);
            document.getElementById('editApprover').value = proposal.approver || '';
            document.getElementById('editApprovalDate').value = formatDateToDDMMYYYY(proposal.approval_date) || '';
            document.getElementById('editCompleted').value = proposal.completed || '';
            document.getElementById('editNotes').value = proposal.notes || '';

            const isAccountant = currentUser.role === 'accountant';
            const isCompleted = proposal.completed === 'Yes';
            const showRestrictedFields = isAccountant ? 
                (proposal.approved_amount != null && proposal.approved_amount !== '' && 
                 proposal.transfer_code && proposal.transfer_code.trim() !== '' && 
                 proposal.payment_date && proposal.payment_date.trim() !== '' && 
                 proposal.status && proposal.status.trim() !== '' && 
                 proposal.approver && proposal.approver.trim() !== '' && 
                 proposal.notes && proposal.notes.trim() !== '') : 
                isCompleted;

            if (!showRestrictedFields) {
                document.getElementById('editApprovedAmount').value = '';
                document.getElementById('editTransferCode').value = '';
                document.getElementById('editPaymentDate').value = '';
                document.getElementById('editStatus').value = '';
                document.getElementById('editApprover').value = '';
                document.getElementById('editNotes').value = '';
                document.getElementById('editApprovedAmount').setAttribute('readonly', 'readonly');
                document.getElementById('editTransferCode').setAttribute('readonly', 'readonly');
                document.getElementById('editPaymentDate').setAttribute('readonly', 'readonly');
                document.getElementById('editStatus').setAttribute('readonly', 'readonly');
                document.getElementById('editApprover').setAttribute('readonly', 'readonly');
                document.getElementById('editNotes').setAttribute('readonly', 'readonly');
            } else {
                document.getElementById('editApprovedAmount').removeAttribute('readonly');
                document.getElementById('editTransferCode').removeAttribute('readonly');
                document.getElementById('editPaymentDate').removeAttribute('readonly');
                document.getElementById('editStatus').removeAttribute('readonly');
                document.getElementById('editApprover').removeAttribute('readonly');
                document.getElementById('editNotes').removeAttribute('readonly');
            }

            if (isAccountant) {
                document.getElementById('editProposer').setAttribute('readonly', 'readonly');
                document.getElementById('editRoom').setAttribute('readonly', 'readonly');
                document.getElementById('editBranch').setAttribute('readonly', 'readonly');
                document.getElementById('editDepartment').setAttribute('readonly', 'readonly');
                document.getElementById('editDate').setAttribute('readonly', 'readonly');
                document.getElementById('editCode').setAttribute('readonly', 'readonly');
                document.getElementById('editContent').setAttribute('readonly', 'readonly');
                document.getElementById('editPurpose').setAttribute('readonly', 'readonly');
                document.getElementById('editSupplier').setAttribute('readonly', 'readonly');
                document.getElementById('editEstimatedCost').setAttribute('readonly', 'readonly');
                document.getElementById('editApprovalDate').setAttribute('readonly', 'readonly');
                document.getElementById('editCompleted').setAttribute('readonly', 'readonly');
            } else {
                document.getElementById('editProposer').removeAttribute('readonly');
                document.getElementById('editRoom').removeAttribute('readonly');
                document.getElementById('editBranch').setAttribute('readonly', 'readonly');
                document.getElementById('editDepartment').removeAttribute('readonly');
                document.getElementById('editDate').removeAttribute('readonly');
                document.getElementById('editCode').removeAttribute('readonly');
                document.getElementById('editContent').removeAttribute('readonly');
                document.getElementById('editPurpose').removeAttribute('readonly');
                document.getElementById('editSupplier').removeAttribute('readonly');
                document.getElementById('editEstimatedCost').removeAttribute('readonly');
                document.getElementById('editApprovalDate').setAttribute('readonly', 'readonly');
                document.getElementById('editCompleted').setAttribute('readonly', 'readonly');
            }

            console.log('Mở modal chỉnh sửa');
            new bootstrap.Modal(document.getElementById('editModal')).show();
        })
        .catch(error => {
            console.error('Lỗi khi tải đề xuất:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi tải đề xuất');
        });
}