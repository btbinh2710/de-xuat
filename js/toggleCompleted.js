function toggleCompleted(proposalId, currentStatus) {
    console.log('toggleCompleted:', proposalId, currentStatus);
    const newStatus = currentStatus === 'Yes' ? 'No' : 'Yes';
    const token = localStorage.getItem('token');
    axios.put(`${API_URL}/proposals/${proposalId}`, { 
        completed: newStatus,
        status: getStatusFromCompleted(newStatus)
    }, {
        headers: { Authorization: `Bearer ${token}` }
    })
        .then(() => {
            console.log('Cập nhật trạng thái hoàn thành thành công');
            loadProposalData();
        })
        .catch(error => {
            console.error('Lỗi khi cập nhật trạng thái hoàn thành:', error.message);
            alert(error.response?.data?.message || 'Lỗi khi cập nhật trạng thái');
        });
}