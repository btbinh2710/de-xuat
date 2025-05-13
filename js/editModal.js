function openEditModal(proposalId) {
    console.log('openEditModal:', proposalId);
    const token = localStorage.getItem('token');
    axios.get(`https://de-xuat-backend-s1mk.onrender.com/api/proposals`, { headers: { Authorization: `Bearer ${token}` } })
        .then(response => {
            console.log('Tải dữ liệu đề xuất để chỉnh sửa:', response.data);
            const proposal = response.data.find(p => p.id === proposalId);
            if (!proposal) {
                console.error('Lỗi: Đề xuất không tồn tại');
                Toastify({
                    text: 'Đề xuất không tồn tại!',
                    duration: 3000,
                    close: true,
                    gravity: "top",
                    position: "right",
                    backgroundColor: "#dc3545",
                    stopOnFocus: true,
                }).showToast();
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
                 proposal.approver && proposal.approver.trim() !== '' &&
                 proposal.approval_date && proposal.approval_date.trim() !== '') :
                isCompleted;

            if (!showRestrictedFields) {
                document.getElementById('editApprovedAmount').value = '';
                document.getElementById('editTransferCode').value = '';
                document.getElementById('editPaymentDate').value = '';
                document.getElementById('editStatus').value = '';
                document.getElementById('editApprover').value = '';
                document.getElementById('editApprovalDate').value = '';
                document.getElementById('editCompleted').value = '';
                document.getElementById('editNotes').value = '';
                document.getElementById('editApprovedAmount').setAttribute('readonly', 'readonly');
                document.getElementById('editTransferCode').setAttribute('readonly', 'readonly');
                document.getElementById('editPaymentDate').setAttribute('readonly', 'readonly');
                document.getElementById('editStatus').setAttribute('readonly', 'readonly');
                document.getElementById('editApprover').setAttribute('readonly', 'readonly');
                document.getElementById('editApprovalDate').setAttribute('readonly', 'readonly');
                document.getElementById('editCompleted').setAttribute('readonly', 'readonly');
                document.getElementById('editNotes').setAttribute('readonly', 'readonly');
            } else {
                document.getElementById('editApprovedAmount').removeAttribute('readonly');
                document.getElementById('editTransferCode').removeAttribute('readonly');
                document.getElementById('editPaymentDate').removeAttribute('readonly');
                document.getElementById('editStatus').removeAttribute('readonly');
                document.getElementById('editApprover').removeAttribute('readonly');
                document.getElementById('editApprovalDate').removeAttribute('readonly');
                document.getElementById('editCompleted').removeAttribute('readonly');
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
            }

            // Xử lý nút Upload lên nhanh
            const quickUploadBtn = document.getElementById('quickUploadBtn');
            if (quickUploadBtn && isAccountant) {
                quickUploadBtn.addEventListener('click', () => {
                    console.log('Quick upload cho đề xuất:', proposalId);
                    const quickData = {
                        approved_amount: parseFloat(document.getElementById('editApprovedAmount').value) || proposal.estimated_cost,
                        transfer_code: document.getElementById('editTransferCode').value || `CK${Date.now()}`,
                        payment_date: document.getElementById('editPaymentDate').value || new Date().toLocaleDateString('vi-VN'),
                        status: document.getElementById('editTransferCode').value ? 'Hoàn thành' : 'Đang xử lý',
                        approver: document.getElementById('editApprover').value || currentUser.username,
                        approval_date: document.getElementById('editApprovalDate').value || new Date().toLocaleDateString('vi-VN'),
                        completed: (document.getElementById('editApprovedAmount').value && 
                                    document.getElementById('editTransferCode').value && 
                                    document.getElementById('editPaymentDate').value && 
                                    document.getElementById('editApprover').value && 
                                    document.getElementById('editApprovalDate').value) ? 'O' : 'X',
                        notes: document.getElementById('editNotes').value || 'Đã duyệt bởi kế toán'
                    };

                    // Kiểm tra các trường bắt buộc
                    if (!quickData.approved_amount || quickData.approved_amount <= 0 ||
                        !quickData.transfer_code || !quickData.payment_date || 
                        !quickData.approver || !quickData.approval_date) {
                        Toastify({
                            text: 'Vui lòng điền đầy đủ các trường bắt buộc: Số tiền được duyệt, Mã chuyển khoản, Ngày thanh toán, Người duyệt, Ngày duyệt!',
                            duration: 3000,
                            close: true,
                            gravity: "top",
                            position: "right",
                            backgroundColor: "#dc3545",
                            stopOnFocus: true,
                        }).showToast();
                        return;
                    }

                    axios.put(`https://de-xuat-backend-s1mk.onrender.com/api/proposals/${proposalId}`, quickData, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                        .then(() => {
                            console.log('Quick upload thành công:', proposalId);
                            Toastify({
                                text: 'Đã cập nhật đề xuất thành công!',
                                duration: 3000,
                                close: true,
                                gravity: "top",
                                position: "right",
                                backgroundColor: "#28a745",
                                stopOnFocus: true,
                            }).showToast();
                            loadProposalData();
                            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
                        })
                        .catch(error => {
                            console.error('Lỗi quick upload:', error);
                            Toastify({
                                text: error.response?.data?.message || 'Lỗi khi cập nhật đề xuất!',
                                duration: 3000,
                                close: true,
                                gravity: "top",
                                position: "right",
                                backgroundColor: "#dc3545",
                                stopOnFocus: true,
                            }).showToast();
                        });
                });
            }

            console.log('Mở modal chỉnh sửa');
            new bootstrap.Modal(document.getElementById('editModal')).show();
        })
        .catch(error => {
            console.error('Lỗi khi tải đề xuất:', error.message);
            Toastify({
                text: error.response?.data?.message || 'Lỗi khi tải đề xuất!',
                duration: 3000,
                close: true,
                gravity: "top",
                position: "right",
                backgroundColor: "#dc3545",
                stopOnFocus: true,
            }).showToast();
        });
}