function downloadExcelTemplate() {
    console.log('downloadExcelTemplate');
    const wb = XLSX.utils.book_new();
    const headers = [
        "NGƯỜI ĐỀ NGHỊ", "PHÒNG BAN", "BỘ PHẬN", "NGÀY THÁNG", 
        "MÃ ĐỀ XUẤT", "NỘI DUNG", "MỤC ĐÍCH", "NHÀ CUNG CẤP", 
        "DỰ TÍNH NGÂN SÁCH"
    ];
    const ws = XLSX.utils.aoa_to_sheet([headers]);
    XLSX.utils.book_append_sheet(wb, ws, "Template");
    XLSX.writeFile(wb, 'Mau_Excel_De_Xuat.xlsx');
}