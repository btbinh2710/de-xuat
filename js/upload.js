function handleExcelUpload() {
    console.log('Bắt đầu handleExcelUpload');
    const uploadModal = document.getElementById('uploadModal');
    if (!uploadModal || !uploadModal.classList.contains('show')) {
        console.error('Lỗi: Modal upload không hiển thị');
        alert('Lỗi giao diện: Vui lòng mở modal tải lên trước khi nhấn Tải lên!');
        return;
    }
    if (!currentUser) {
        console.error('Lỗi: currentUser không tồn tại');
        showUploadError("Vui lòng đăng nhập để tải lên đề xuất!");
        return;
    }
    console.log('currentUser:', currentUser);
    if (currentUser.role === 'accountant') {
        console.error('Lỗi: Tài khoản kế toán không được phép tải lên');
        showUploadError("Tài khoản kế toán không được phép tải lên đề xuất!");
        return;
    }
    const fileInput = document.getElementById('excelFile');
    if (!fileInput) {
        console.error('Lỗi: Không tìm thấy fileInput');
        showUploadError("Lỗi giao diện: Không tìm thấy trường chọn file!");
        return;
    }
    const file = fileInput.files[0];
    if (!file) {
        console.error('Lỗi: Không có file Excel được chọn');
        showUploadError("Vui lòng chọn file Excel!");
        return;
    }
    console.log('File được chọn:', file.name);
    const reader = new FileReader();
    reader.onload = function(e) {
        console.log('Đọc file Excel thành công');
        try {
            const data = new Uint8Array(e.target.result);
            console.log('Dữ liệu file:', data.slice(0, 50));
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheetName = workbook.SheetNames[0];
            console.log('Sheet đầu tiên:', firstSheetName);
            const worksheet = workbook.Sheets[firstSheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            console.log('Dữ liệu Excel:', jsonData);

            if (jsonData.length < 2) {
                console.error('Lỗi: File Excel không chứa dữ liệu');
                showUploadError("File không chứa dữ liệu hoặc không đúng định dạng!");
                return;
            }

            const headers = jsonData[0];
            console.log('Tiêu đề:', headers);
            const requiredColumns = ["NGƯỜI ĐỀ NGHỊ", "PHÒNG BAN", "BỘ PHẬN", "NGÀY THÁNG", "MÃ ĐỀ XUẤT", "NỘI DUNG", "NHÀ CUNG CẤP", "DỰ TÍNH NGÂN SÁCH"];
            const missingColumns = requiredColumns.filter(col => !headers.includes(col));

            if (missingColumns.length > 0) {
                console.error('Lỗi: Thiếu cột bắt buộc', missingColumns);
                showUploadError(`File thiếu các cột bắt buộc: ${missingColumns.join(', ')}`);
                return;
            }

            const token = localStorage.getItem('token');
            if (!token) {
                console.error('Lỗi: Token không tồn tại');
                showUploadError("Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại!");
                return;
            }
            console.log('Token:', token.slice(0, 20) + '...');

            const newProposals = [];
            const duplicates = new Set();
            const existingCodes = new Set(proposals.map(p => `${p.code || ''}-${p.branch}`));
            console.log('Mã đề xuất hiện có:', existingCodes);

            for (let i = 1; i < jsonData.length; i++) {
                const row = jsonData[i];
                console.log(`Xử lý hàng ${i + 1}:`, row);
                if (row.length === 0 || row.every(cell => cell === null || cell === undefined || cell === '')) {
                    console.log(`Hàng ${i + 1} trống, bỏ qua`);
                    continue;
                }

                const proposal = {};
                headers.forEach((header, index) => {
                    if (index < row.length) {
                        proposal[header] = row[index];
                    }
                });
                console.log(`Dữ liệu hàng ${i + 1}:`, proposal);

                const formattedProposal = {
                    proposer: String(proposal["NGƯỜI ĐỀ NGHỊ"] || '').trim(),
                    room: String(proposal["PHÒNG BAN"] || '').trim(),
                    branch: currentUser.branch,
                    department: String(proposal["BỘ PHẬN"] || '').trim(),
                    date: formatDateToDDMMYYYY(proposal["NGÀY THÁNG"]) || '',
                    code: String(proposal["MÃ ĐỀ XUẤT"] || '').trim(),
                    content: String(proposal["NỘI DUNG"] || '').trim(),
                    purpose: String(proposal["MỤC ĐÍCH"] || '').trim(),
                    supplier: String(proposal["NHÀ CUNG CẤP"] || '').trim(),
                    estimated_cost: parseFloat(proposal["DỰ TÍNH NGÂN SÁCH"]) || 0,
                    approved_amount: 0,
                    transfer_code: '',
                    payment_date: '',
                    notes: '',
                    status: 'Đang xử lý',
                    approver: '',
                    approval_date: '',
                    completed: 'No'
                };
                console.log(`Đề xuất định dạng hàng ${i + 1}:`, formattedProposal);

                const requiredFields = [
                    { key: 'proposer', name: 'NGƯỜI ĐỀ NGHỊ' },
                    { key: 'room', name: 'PHÒNG BAN' },
                    { key: 'department', name: 'BỘ PHẬN' },
                    { key: 'date', name: 'NGÀY THÁNG' },
                    { key: 'code', name: 'MÃ ĐỀ XUẤT' },
                    { key: 'content', name: 'NỘI DUNG' },
                    { key: 'supplier', name: 'NHÀ CUNG CẤP' },
                    { key: 'estimated_cost', name: 'DỰ TÍNH NGÂN SÁCH' }
                ];
                const missingFields = requiredFields.filter(field => {
                    if (field.key === 'estimated_cost') {
                        return isNaN(formattedProposal[field.key]) || formattedProposal[field.key] <= 0;
                    }
                    return !formattedProposal[field.key] || String(formattedProposal[field.key]).trim() === '';
                });
                if (missingFields.length > 0) {
                    console.error(`Lỗi: Hàng ${i + 1} thiếu trường bắt buộc`, missingFields);
                    showUploadError(`Hàng ${i + 1} thiếu hoặc không hợp lệ các trường bắt buộc: ${missingFields.map(f => f.name).join(', ')}`);
                    return;
                }

                if (formattedProposal.date && !formattedProposal.date.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                    console.error(`Lỗi: Hàng ${i + 1} NGÀY THÁNG sai định dạng`);
                    showUploadError(`Hàng ${i + 1}: NGÀY THÁNG phải có định dạng DD/MM/YYYY`);
                    return;
                }

                if (isNaN(formattedProposal.estimated_cost) || formattedProposal.estimated_cost < 0) {
                    console.error(`Lỗi: Hàng ${i + 1} DỰ TÍNH NGÂN SÁCH không hợp lệ`);
                    showUploadError(`Hàng ${i + 1}: DỰ TÍNH NGÂN SÁCH phải là số không âm`);
                    return;
                }

                const key = `${formattedProposal.code || ''}-${currentUser.branch}`;
                if (existingCodes.has(key)) {
                    console.log(`Hàng ${i + 1} trùng mã đề xuất: ${key}`);
                    duplicates.add(key);
                    continue;
                }
                existingCodes.add(key);
                console.log(`Thêm đề xuất mới hàng ${i + 1}:`, formattedProposal);
                newProposals.push(axios.post(`${API_URL}/proposals`, formattedProposal, {
                    headers: { Authorization: `Bearer ${token}` }
                }));
            }

            if (newProposals.length === 0) {
                console.error('Lỗi: Không có đề xuất mới để tải lên');
                showUploadError("Không có đề xuất mới để tải lên hoặc tất cả đề xuất trùng lặp!");
                return;
            }
            console.log('Gửi', newProposals.length, 'yêu cầu POST /api/proposals');

            Promise.all(newProposals)
                .then(() => {
                    console.log('Tải lên thành công', newProposals.length, 'đề xuất');
                    showUploadSuccess(`Đã tải lên thành công ${newProposals.length} đề xuất mới từ chi nhánh ${currentUser.branch}!`);
                    fileInput.value = '';
                    loadProposalData();
                    if (duplicates.size > 0) {
                        alert(`Có ${duplicates.size} đề xuất trùng lặp đã bị bỏ qua và không được thêm vào.`);
                    }
                })
                .catch(error => {
                    console.error('Lỗi khi gửi yêu cầu POST /api/proposals:', error);
                    let errorMessage = 'Lỗi khi tải lên đề xuất. Vui lòng kiểm tra dữ liệu và thử lại.';
                    if (error.response?.data?.message) {
                        if (error.response.data.message.includes('Mã đề xuất đã tồn tại')) {
                            errorMessage = 'Một hoặc nhiều mã đề xuất đã tồn tại cho chi nhánh này!';
                        } else if (error.response.data.message.includes('Dữ liệu không hợp lệ')) {
                            errorMessage = `Dữ liệu không hợp lệ: ${error.response.data.message}`;
                        } else {
                            errorMessage = error.response.data.message;
                        }
                    }
                    showUploadError(errorMessage);
                });
        } catch (error) {
            console.error('Lỗi xử lý file Excel:', error);
            showUploadError("Lỗi khi xử lý file Excel: " + error.message);
        }
    };

    reader.onerror = function() {
        console.error('Lỗi đọc file Excel');
        showUploadError("Lỗi khi đọc file!");
    };

    console.log('Bắt đầu đọc file Excel');
    reader.readAsArrayBuffer(file);
}

function downloadExcelTemplate() {
    console.log('downloadExcelTemplate');
    const wb = XLSX.utils.book_new();
    const headers = [
        "NGƯỜI ĐỀ NGHỊ", "PHÒNG BAN", "BỘ PHẬN", "NGÀY THÁNG", "MÃ ĐỀ XUẤT", 
        "NỘI DUNG", "MỤC ĐÍCH", "NHÀ CUNG CẤP", "DỰ TÍNH NGÂN SÁCH"
    ];
    const sampleData = [
        headers,
        ["Nguyễn Văn A", "Kinh Doanh", "KD", "01/05/2025", "DX001", "Mua laptop phục vụ công việc", 
         "Phục vụ công việc hàng ngày", "Công ty ABC", 15000000],
        ["Trần Thị B", "Hành Chính Nhân Sự", "HCNS", "02/05/2025", "DX002", "Mua máy in phục vụ văn phòng", 
         "Phục vụ in ấn tài liệu", "Công ty XYZ", 5000000]
    ];
    const ws = XLSX.utils.aoa_to_sheet(sampleData);
    XLSX.utils.book_append_sheet(wb, ws, "Template");
    XLSX.writeFile(wb, "DE_XUAT_THANH_TOAN_TEMPLATE.xlsx");
}