function downloadExcelTemplate() {
    console.log('downloadExcelTemplate');
    const wb = XLSX.utils.book_new();
    const headers = [
        "NGƯỜI ĐỀ NGHỊ", "PHÒNG BAN", "BỘ PHẬN", "NGÀY THÁNG", 
        "MÃ ĐỀ XUẤT", "NỘI DUNG", "MỤC ĐÍCH", "NHÀ CUNG CẤP", 
        "DỰ TÍNH NGÂN SÁCH"
    ];
    const sampleData = [
        headers,
        ["Nguyễn Văn A", "Phòng Kinh Doanh", "Bộ phận Bán hàng", "01/05/2025", "DX003", "Mua máy chiếu", "Hỗ trợ thuyết trình", "Công ty DEF", 8000000],
        ["Trần Thị B", "Phòng Hành Chính", "Bộ phận Nhân sự", "03/05/2025", "DX004", "Mua tủ hồ sơ", "Lưu trữ tài liệu", "Công ty GHI", 3000000]
    ];
    const ws = XLSX.utils.aoa_to_sheet(sampleData);
    XLSX.utils.book_append_sheet(wb, ws, "Template");
    XLSX.writeFile(wb, 'Mau_Excel_De_Xuat.xlsx');
}