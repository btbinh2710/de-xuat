function applySearch() {
    console.log('applySearch');
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) {
        console.error('Lỗi: Không tìm thấy searchInput');
        return;
    }

    const searchTerm = searchInput.value.toLowerCase();
    console.log('Tìm kiếm với từ khóa:', searchTerm);
    filteredProposals = proposals.filter(proposal => {
        return (
            (proposal.proposer || '').toLowerCase().includes(searchTerm) ||
            (proposal.content || '').toLowerCase().includes(searchTerm)
        );
    });
    currentPage = 1;
    renderTable();
    renderPagination();
}

function sortTable(column) {
    console.log('sortTable:', column);
    if (currentSortColumn === column) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortDirection = 'asc';
    }

    document.querySelectorAll('th[data-sort] .sort-icon').forEach(icon => {
        icon.className = 'sort-icon';
    });
    const currentIcon = document.querySelector(`th[data-sort="${column}"] .sort-icon`);
    if (currentIcon) {
        if (currentSortDirection === 'asc') {
            currentIcon.classList.add('asc');
        } else {
            currentIcon.classList.remove('asc');
        }
    }

    sortData();
    renderTable();
}

function sortData() {
    console.log('sortData:', currentSortColumn, currentSortDirection);
    if (!currentSortColumn) return;

    filteredProposals.sort((a, b) => {
        let valueA = a[currentSortColumn];
        let valueB = b[currentSortColumn];

        if (typeof valueA === 'string' && typeof valueB === 'string') {
            valueA = valueA.toLowerCase();
            valueB = valueB.toLowerCase();
        }

        if (['date', 'payment_date', 'approval_date'].includes(currentSortColumn)) {
            valueA = valueA ? new Date(formatDateToYYYYMMDD(valueA)) : '';
            valueB = valueB ? new Date(formatDateToYYYYMMDD(valueB)) : '';
        }

        valueA = valueA === undefined || valueA === null || valueA === '' ? '' : valueA;
        valueB = valueB === undefined || valueB === null || valueB === '' ? '' : valueB;

        if (currentSortDirection === 'asc') {
            return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
        } else {
            return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
        }
    });
}