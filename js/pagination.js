function renderPagination() {
    console.log('renderPagination');
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) {
        console.error('Lỗi: Không tìm thấy paginationContainer');
        return;
    }

    paginationContainer.innerHTML = '';
    const totalPages = Math.ceil(filteredProposals.length / itemsPerPage);

    if (totalPages <= 1) return;

    const prevButton = document.createElement('button');
    prevButton.classList.add('pagination-button');
    prevButton.innerHTML = '«';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            console.log('Chuyển về trang trước:', currentPage - 1);
            currentPage--;
            renderTable();
            renderPagination();
        }
    });
    paginationContainer.appendChild(prevButton);

    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.classList.add('pagination-button');
        if (i === currentPage) pageButton.classList.add('active');
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            console.log('Chuyển đến trang:', i);
            currentPage = i;
            renderTable();
            renderPagination();
        });
        paginationContainer.appendChild(pageButton);
    }

    const nextButton = document.createElement('button');
    nextButton.classList.add('pagination-button');
    nextButton.innerHTML = '»';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            console.log('Chuyển đến trang tiếp theo:', currentPage + 1);
            currentPage++;
            renderTable();
            renderPagination();
        }
    });
    paginationContainer.appendChild(nextButton);
}