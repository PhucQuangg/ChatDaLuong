document.getElementById('addAccountForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Ngừng hành động mặc định của form

    // Lấy dữ liệu từ các trường trong form
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.querySelector('input[name="role"]:checked').value; 


    if (!username || !email || !password) {
        alert('Vui lòng nhập đầy đủ thông tin!');
        return;
    }

    const data = {
        username: username,
        email: email,
        password: password,
        role: role
    };
    const token = localStorage.getItem("adminToken");
    fetch('http://localhost:8000/api/add-account/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        body: JSON.stringify(data),  
    })
    .then(response => {
        return response.json();  
    })
    .then(data => {
        if (data.message) {
            alert('Tạo tài khoản thành công!');
            window.location.href = 'AccountAdmin.html';  
        } else if (data.error) {
            alert(data.error);  
        }
    })
    .catch(error => {
        console.error('Có lỗi xảy ra:', error);
        alert('Đã xảy ra lỗi, vui lòng thử lại!');  
    });
});
