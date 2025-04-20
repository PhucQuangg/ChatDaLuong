function loadAdminList() {
    fetch('http://127.0.0.1:8000/api/admin-list/')
      .then(response => {
        if (!response.ok) throw new Error('Lỗi khi gọi API admin!');
        return response.json();
      })
      .then(data => {
        const tbody = document.querySelector('.table-wrapper tbody');
        tbody.innerHTML = '';
        data.forEach((admin,index) => {
          const row = `
            <tr>
              <td>${index + 1}</td>
              <td>${admin.id}</td>
              <td>${admin.username}</td>
              <td>${admin.email}</td>
              <td>${admin.date_joined ? admin.date_joined.split('T')[0] : ''}</td>
              <td>
                <button class="btn btn-sm btn-primary" onclick="window.location.href='UpdateAccount.html?id=${admin.id}'">Sửa</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUserOrAdmin(${admin.id}, loadAdminList)">Xóa</button>
              </td>
            </tr>
          `;
          tbody.insertAdjacentHTML('beforeend', row);
        });
      })
      .catch(error => {
        alert('Không thể tải danh sách admin!');
        console.error(error);
      });
  }
  
  function loadUserList() {
    fetch('http://127.0.0.1:8000/api/user-list/')
      .then(response => {
        if (!response.ok) throw new Error('Lỗi khi gọi API user!');
        return response.json();
      })
      .then(data => {
        const tbody = document.querySelector('.table-wrapper tbody');
        tbody.innerHTML = '';
        
        data.forEach((user,index) => {
        
          const row = `
            <tr>
              <td>${index + 1}</td>
              <td>${user.id}</td>   
              <td>${user.username}</td>
              <td>${user.email}</td>
              <td>${user.date_joined ? user.date_joined.split('T')[0] : ''}</td>
              <td>
                <button class="btn btn-sm btn-primary" onclick="window.location.href='UpdateAccount.html?id=${user.id}'">Sửa</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUserOrAdmin(${user.id}, loadUserList)">Xóa</button>
              </td>
            </tr>
          `;
          tbody.insertAdjacentHTML('beforeend', row);
        });
      })
      .catch(error => {
        alert('Không thể tải danh sách người dùng!');
        console.error(error);
      });
  }

function fetchAllUsers() {
  fetch('http://127.0.0.1:8000/api/user-list/')
      .then(response => response.json()) 
      .then(users => {
          const allUsersList = document.getElementById('all-users'); 
          allUsersList.innerHTML = '';

          
          users.forEach(user => {
              const li = document.createElement('li');
              li.textContent = user.username; 
           
              li.onclick = function() {
                  openConversation(user.id); 
              };
              allUsersList.appendChild(li);  
      })
      .catch(error => console.error('Lỗi khi tải dữ liệu người dùng:', error));
      })
}
