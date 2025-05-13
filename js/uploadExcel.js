function handleExcelUpload() {
    console.log('Bắt đầu handleExcelUpload');
    const uploadModal = document.getElementById('uploadModal');
    const uploadButton = document.getElementById('confirmUploadBtn');
    const spinner = document.getElementById('uploadSpinner');

    if (!uploadModal || !uploadModal.classList.contains('show')) {
        console.error('Lỗi: Modal upload không hiển thị');
        Toastify({
            text: 'Lỗi giao diện: Vui lòng mở modal upload trước khi nhấn Upload!',
            duration: 3000,
            close: true,
            gravity: "top",
            position: "right",
            backgroundColor: "#dc3545",
            stopOnFocus: true,
        }).showToast();
        return;
    }
    if (!currentUser) {
        console.error('Lỗi: currentUser không tồn tại');
        showUploadError("Vui lòng đăng nhập để upload đề xuất!");
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

    // Hiển thị spinner và vô hiệu hóa nút
    uploadButton.disabled = true;
    spinner.classList.remove('hidden');

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
            const requiredColumns = ["STT", "MÃ SỐ ĐỀ XUẤT", "SỐ TIỀN ĐƯỢC DUYỆT", "MÃ CHUYỂN KHOẢN", "NGÀY THANH TOÁN", "TRẠNG THÁI", "NGƯỜI DUYỆT", "NGÀY DUYỆT", "HOÀN THÀNH", "GHI CHÚ"];
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

            const updates = [];
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
                    id: parseInt(proposal["STT"]) || 0,
                    code: String(proposal["MÃ SỐ ĐỀ XUẤT"] || '').trim(),
                    approved_amount: parseFloat(proposal["SỐ TIỀN ĐƯỢC DUYỆT"]) || 0,
                    transfer_code: String(proposal["MÃ CHUYỂN KHOẢN"] || '').trim(),
                    payment_date: formatDateToDDMMYYYY(proposal["NGÀY THANH TOÁN"]) || '',
                    status: String(proposal["TRẠNG THÁI"] || 'Đang xử lý').trim(),
                    approver: String(proposal["NGƯỜI DUYỆT"] || '').trim(),
                    approval_date: formatDateToDDMMYYYY(proposal["NGÀY DUYỆT"]) || '',
                    completed: String(proposal["HOÀN THÀNH"] || 'X').trim(),
                    notes: String(proposal["GHI CHÚ"] || '').trim()
                };
                console.log(`Đề xuất định dạng hàng ${i + 1}:`, formattedProposal);

                const requiredFields = [
                    { key: 'id', name: 'STT' },
                    { key: 'code', name: 'MÃ SỐ ĐỀ XUẤT' },
                    { key: 'approved_amount', name: 'SỐ TIỀN ĐƯỢC DUYỆT' },
                    { key: 'transfer_code', name: 'MÃ CHUYỂN KHOẢN' },
                    { key: 'payment_date', name: 'NGÀY THANH TOÁN' },
                    { key: 'approver', name: 'NGƯỜI DUYỆT' },
                    { key: 'approval_date', name: 'NGÀY DUYỆT' }
                ];
                const missingFields = requiredFields.filter(field => {
                    if (field.key === 'approved_amount') {
                        return isNaN(formattedProposal[field.key]) || formattedProposal[field.key] <= 0;
                    }
                    return !formattedProposal[field.key] || String(formattedProposal[field.key]).trim() === '';
                });
                if (missingFields.length > 0) {
                    console.error(`Lỗi: Hàng ${i + 1} thiếu trường bắt buộc`, missingFields);
                    showUploadError(`Hàng ${i + 1} thiếu hoặc không hợp lệ các trường bắt buộc: ${missingFields.map(f => f.name).join(', ')}`);
                    return;
                }

                if (formattedProposal.payment_date && !formattedProposal.payment_date.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                    console.error(`Lỗi: Hàng ${i + 1} NGÀY THANH TOÁN sai định dạng`);
                    showUploadError(`Hàng ${i + 1}: NGÀY THANH TOÁN phải có định dạng DD/MM/YYYY`);
                    return;
                }

                if (formattedProposal.approval_date && !formattedProposal.approval_date.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                    console.error(`Lỗi: Hàng ${i + 1} NGÀY DUYỆT sai định dạng`);
                    showUploadError(`Hàng ${i + 1}: NGÀY DUYỆT phải có định dạng DD/MM/YYYY`);
                    return;
                }

                updates.push(axios.put(`https://de-xuat-backend-s1mk.onrender.com/api/proposals/${formattedProposal.id}`, formattedProposal, {
                    headers: { Authorization: `Bearer ${token}` }
                }));
            }

            if (updates.length === 0) {
                console.error('Lỗi: Không có đề xuất nào để cập nhật');
                showUploadError("Không có đề xuất nào để cập nhật hoặc tất cả hàng không hợp lệ!");
                return;
            }
            console.log('Gửi', updates.length, 'yêu cầu PUT /api/proposals');

            Promise.all(updates)
                .then(() => {
                    console.log('Cập nhật thành công', updates.length, 'đề xuất');
                    showUploadSuccess(`Đã cập nhật thành công ${updates.length} đề xuất!`);
                    fileInput.value = '';
                    loadProposalData();
                })
                .catch(error => {
                    console.error('Lỗi khi gửi yêu cầu PUT /api/proposals:', error);
                    let errorMessage = 'Lỗi khi cập nhật đề xuất. Vui lòng kiểm tra dữ liệu và thử lại.';
                    if (error.response?.data?.message) {
                        errorMessage = error.response.data.message;
                    }
                    showUploadError(errorMessage);
                })
                .finally(() => {
                    // Ẩn spinner và kích hoạt lại nút
                    uploadButton.disabled = false;
                    spinner.classList.add('hidden');
                });
        } catch (error) {
            console.error('Lỗi xử lý file Excel:', error);
            showUploadError("Lỗi khi xử lý file Excel: " + error.message);
        } finally {
            // Ẩn spinner và kích hoạt lại nút trong trường hợp lỗi xử lý file
            uploadButton.disabled = false;
            spinner.classList.add('hidden');
        }
    };

    reader.onerror = function() {
        console.error('Lỗi đọc file Excel');
        showUploadError("Lỗi khi đọc file!");
        uploadButton.disabled = false;
        spinner.classList.add('hidden');
    };

    console.log('Bắt đầu đọc file Excel');
    reader.readAsArrayBuffer(file);
}

function showUploadError(message) {
    console.log('showUploadError:', message);
    Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: "#dc3545",
        stopOnFocus: true,
    }).showToast();
}

function showUploadSuccess(message) {
    console.log('showUploadSuccess:', message);
    Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "right",
        backgroundColor: "#28a745",
        stopOnFocus: true,
    }).showToast();
}