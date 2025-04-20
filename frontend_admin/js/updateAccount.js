window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const userId = params.get('id');
    if (userId) {
        editUserOrAdmin(userId);
    }
});
function editUserOrAdmin(userId) {
    const token = localStorage.getItem("adminToken");

    fetch(`http://127.0.0.1:8000/api/get-user/${userId}/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('username').value = data.username;
        document.getElementById('email').value = data.email;

        if (data.is_admin) {
            document.querySelector("input[name='role'][value='1']").checked = true;
        } else {
            document.querySelector("input[name='role'][value='0']").checked = true;
        }

        const form = document.getElementById('UpdateAccountForm');
        form.setAttribute('data-user-id', userId);  

    })
    .catch(error => {
        alert('Không thể tải thông tin người dùng!');
        console.error(error);
    });
}

function updateUserOrAdmin() {
    const token = localStorage.getItem("adminToken");
    const form = document.getElementById('UpdateAccountForm');
    const userId = form.getAttribute('data-user-id'); 

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const role = document.querySelector("input[name='role']:checked").value;

    fetch(`http://127.0.0.1:8000/api/update-account/${userId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            username: username,
            email: email,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`${data.error}`);
        } else {
            alert("✅ Cập nhật thành công!");
            if (role == '1') {
                window.location.href = "AccountAdmin.html";  
            }else {
                window.location.href = "AccountUser.html";  
            }
        
        }
    })
    .catch(error => {
        alert("Lỗi khi cập nhật người dùng!");
        console.error(error);
    });
}

