function exportReport(type) {
    console.log(`exportReport: ${type}`);
    const wb = XLSX.utils.book_new();
    const headers = [
        "STT", "Ngày tháng", "Chi nhánh", "Phòng ban", "Người đề nghị", "Bộ phận",
        "Mã số đề xuất", "Nội dung", "Mục đích", "Nhà cung cấp", "Dự tính ngân sách",
        "Số tiền được duyệt", "Mã chuyển khoản", "Ngày thanh toán", "Trạng thái",
        "Người duyệt", "Ngày duyệt", "Hoàn thành", "Ghi chú"
    ];

    const data = proposals.map(proposal => [
        proposal.id,
        formatDateToDDMMYYYY(proposal.date),
        proposal.branch,
        proposal.room,
        proposal.proposer,
        proposal.department,
        proposal.code,
        proposal.content,
        proposal.purpose,
        proposal.supplier,
        proposal.estimated_cost,
        proposal.approved_amount || '',
        proposal.transfer_code || '',
        formatDateToDDMMYYYY(proposal.payment_date) || '',
        proposal.transfer_code && proposal.transfer_code.trim() !== '' ? 'Hoàn thành' : 'Đang xử lý',
        proposal.approver || '',
        formatDateToDDMMYYYY(proposal.approval_date) || '',
        (proposal.approved_amount != null && proposal.approved_amount !== '' &&
         proposal.transfer_code && proposal.transfer_code.trim() !== '' &&
         proposal.payment_date && proposal.payment_date.trim() !== '' &&
         proposal.approver && proposal.approver.trim() !== '' &&
         proposal.approval_date && proposal.approval_date.trim() !== '') ? 'O' : 'X',
        proposal.notes || ''
    ]);

    const ws = XLSX.utils.aoa_to_sheet([headers, ...data]);
    XLSX.utils.book_append_sheet(wb, ws, type === 'XDV' ? 'Báo cáo XDV' : 'Báo cáo PTT');
    XLSX.writeFile(wb, `Bao_cao_${type}_${new Date().toISOString().slice(0, 10)}.xlsx`);
}

document.getElementById('exportXDVBtn').addEventListener('click', () => exportReport('XDV'));
document.getElementById('exportPTTBtn').addEventListener('click', () => exportReport('PPT'));