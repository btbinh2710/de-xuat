function renderTable() {
    console.log('renderTable');
    const tableBody = document.getElementById('proposalsTableBody');
    if (!tableBody) {
        console.error('Lỗi: Không tìm thấy proposalsTableBody');
        return;
    }

    tableBody.innerHTML = '';
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredProposals.length);
    const currentPageData = filteredProposals.slice(startIndex, endIndex);

    if (currentPageData.length === 0) {
        console.log('Không có dữ liệu để hiển thị');
        tableBody.innerHTML = `<tr><td colspan="20" class="text-center">Không có dữ liệu</td></tr>`;
        return;
    }

    const codeBranchMap = new Map();
    proposals.forEach(proposal => {
        const key = `${proposal.code || ''}-${proposal.branch}`;
        if (!codeBranchMap.has(key)) {
            codeBranchMap.set(key, []);
        }
        codeBranchMap.get(key).push(proposal);
    });

    currentPageData.forEach((proposal, index) => {
        const row = document.createElement('tr');
        const key = `${proposal.code || ''}-${proposal.branch}`;
        const isDuplicate = codeBranchMap.get(key).length > 1;
        if (isDuplicate) {
            row.classList.add('duplicate');
        }

        const formatCurrency = (value) => value ? new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value) : '';
        const isAccountant = currentUser.role === 'accountant';
        const isCompleted = proposal.completed === 'Yes';

        // Kiểm tra điều kiện hiển thị các cột nhạy cảm
        const showRestrictedColumns = isAccountant ? 
            (proposal.approved_amount != null && proposal.approved_amount !== '' &&
             proposal.transfer_code && proposal.transfer_code.trim() !== '' &&
             proposal.payment_date && proposal.payment_date.trim() !== '' &&
             proposal.approver && proposal.approver.trim() !== '' &&
             proposal.approval_date && proposal.approval_date.trim() !== '' &&
             proposal.completed && proposal.completed.trim() !== '' &&
             proposal.notes && proposal.notes.trim() !== '') :
            isCompleted;

        const approvedAmount = showRestrictedColumns ? formatCurrency(proposal.approved_amount) : '';
        const transferCode = showRestrictedColumns ? sanitizeHTML(proposal.transfer_code || '') : '';
        const paymentDate = showRestrictedColumns ? formatDateToDDMMYYYY(proposal.payment_date) : '';
        const status = showRestrictedColumns ? sanitizeHTML(getStatusFromCompleted(proposal.completed)) : '';
        const approver = showRestrictedColumns ? sanitizeHTML(proposal.approver || '') : '';
        const approvalDate = showRestrictedColumns ? formatDateToDDMMYYYY(proposal.approval_date) : '';
        const completed = showRestrictedColumns ? `<span class="completed-btn ${proposal.completed === 'Yes' ? 'completed' : ''}" data-id="${proposal.id}">${proposal.completed === 'Yes' ? 'O' : 'X'}</span>` : '';
        const notes = showRestrictedColumns ? sanitizeHTML(proposal.notes || '') : '';

        row.innerHTML = `
            <td>${proposal.id}</td>
            <td>${formatDateToDDMMYYYY(proposal.date)}</td>
            <td>${sanitizeHTML(proposal.branch || '')}</td>
            <td>${sanitizeHTML(proposal.room || '')}</td>
            <td>${sanitizeHTML(proposal.proposer || '')}</td>
            <td>${sanitizeHTML(proposal.department || '')}</td>
            <td>${sanitizeHTML(proposal.code || '')}</td>
            <td>${sanitizeHTML(proposal.content || '')}</td>
            <td>${sanitizeHTML(proposal.purpose || '')}</td>
            <td>${sanitizeHTML(proposal.supplier || '')}</td>
            <td>${formatCurrency(proposal.estimated_cost)}</td>
            <td>${approvedAmount}</td>
            <td>${transferCode}</td>
            <td>${paymentDate}</td>
            <td>${status}</td>
            <td>${approver}</td>
            <td>${approvalDate}</td>
            <td>${completed}</td>
            <td>${notes}</td>
            <td class="no-print">
                ${currentUser.role !== 'accountant' ? `
                    <button class="btn btn-primary btn-sm edit-btn" data-id="${proposal.id}" aria-label="Edit proposal details">
                        <i class="bi bi-pencil"></i> Sửa
                    </button>
                    <button class="btn btn-danger btn-sm delete-btn ms-1" data-id="${proposal.id}" aria-label="Delete proposal">
                        <i class="bi bi-trash"></i> Xóa
                    </button>
                ` : `
                    <button class="btn btn-primary btn-sm edit-btn" data-id="${proposal.id}" aria-label="Edit proposal details">
                        <i class="bi bi-pencil"></i> Sửa
                    </button>
                `}
            </td>
        `;
        tableBody.appendChild(row);

        if (row.querySelector('.edit-btn')) {
            row.querySelector('.edit-btn').addEventListener('click', () => {
                console.log('Mở modal chỉnh sửa:', proposal.id);
                openEditModal(proposal.id);
            });
        }
        if (row.querySelector('.delete-btn')) {
            row.querySelector('.delete-btn').addEventListener('click', () => {
                console.log('Mở modal xóa:', proposal.id);
                openDeleteModal(proposal.id);
            });
        }
        row.querySelector('.completed-btn')?.addEventListener('click', () => {
            console.log('Thay đổi trạng thái hoàn thành:', proposal.id);
            toggleCompleted(proposal.id, proposal.completed);
        });
    });
}