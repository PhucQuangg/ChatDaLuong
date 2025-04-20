function deleteUserOrAdmin(userId, reloadFunction) {
    const token = localStorage.getItem("adminToken");
  
  
    if (!confirm("Bạn có chắc muốn xóa người dùng này?")) return;
    
  
    fetch(`http://127.0.0.1:8000/api/delete-user/${userId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (!response.ok) throw new Error("Xóa thất bại!");
        alert("Đã xóa thành công!");
        reloadFunction(); 
      })
      .catch(error => {
        alert("Lỗi khi xóa!");
        console.error(error);
      });
  }
  