function exportSummaryReport(branchType) {
    console.log('exportSummaryReport:', branchType);
    const token = localStorage.getItem('token');
    axios.get(`${API_URL}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(response => {
            console.log('Tải dữ liệu để xuất báo cáo:', response.data);
            const filteredData = response.data.filter(p => p.branch.startsWith(branchType));
            if (filteredData.length === 0) {
                console.log(`Không có dữ liệu cho chi nhánh ${branchType}`);
                alert(`Không có dữ liệu từ các chi nhánh ${branchType} để xuất báo cáo!`);
                return;
            }
            const wb = XLSX.utils.book_new();
            const headers = [
                "STT", "NGÀY THÁNG", "CHI NHÁNH", "PHÒNG BAN", "NGƯỜI ĐỀ NGHỊ", "BỘ PHẬN", "MÃ ĐỀ XUẤT", 
                "NỘI DUNG", "MỤC ĐÍCH", "NHÀ CUNG CẤP", "DỰ TÍNH NGÂN SÁCH", 
                "SỐ TIỀN ĐƯỢC DUYỆT", "MÃ CHUYỂN KHOẢN", "NGÀY THANH TOÁN", "TRẠNG THÁI", 
                "NGƯỜI DUYỆT", "NGÀY DUYỆT", "HOÀN THÀNH", "GHI CHÚ"
            ];
            const data = [headers];
            filteredData.forEach((item, index) => {
                const isAccountant = currentUser.role === 'accountant';
                const isCompleted = item.completed === 'Yes';
                let showRestrictedColumns = false;
                if (isAccountant) {
                    showRestrictedColumns = item.approved_amount != null && item.approved_amount !== '' &&
                                          item.transfer_code && item.transfer_code.trim() !== '' &&
                                          item.payment_date && item.payment_date.trim() !== '' &&
                                          item.status && item.status.trim() !== '' &&
                                          item.approver && item.approver.trim() !== '' &&
                                          item.notes && item.notes.trim() !== '';
                } else {
                    showRestrictedColumns = isCompleted;
                }

                const approvedAmount = showRestrictedColumns ? item.approved_amount || 0 : '';
                const transferCode = showRestrictedColumns ? item.transfer_code || '' : '';
                const paymentDate = showRestrictedColumns ? formatDateToDDMMYYYY(item.payment_date) || '' : '';
                const status = showRestrictedColumns ? getStatusFromCompleted(item.completed) : '';
                const approver = showRestrictedColumns ? item.approver || '' : '';
                const notes = showRestrictedColumns ? item.notes || '' : '';

                data.push([
                    index + 1,
                    formatDateToDDMMYYYY(item.date) || '',
                    item.branch || '',
                    item.room || '',
                    item.proposer || '',
                    item.department || '',
                    item.code || '',
                    item.content || '',
                    item.purpose || '',
                    item.supplier || '',
                    item.estimated_cost || 0,
                    approvedAmount,
                    transferCode,
                    paymentDate,
                    status,
                    approver,
                    formatDateToDDMMYYYY(item.approval_date) || '',
                    item.completed || '',
                    notes
                ]);
            });
            const ws = XLSX.utils.aoa_to_sheet(data);
            XLSX.utils.book_append_sheet(wb, ws, "Report");
            XLSX.writeFile(wb, `BAO_CAO_${branchType}_${new Date().toISOString().split('T')[0]}.xlsx`);
        })
        .catch(error => {
            console.error('Lỗi khi xuất báo cáo:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi xuất báo cáo');
        });
}