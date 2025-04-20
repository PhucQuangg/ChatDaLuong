function adminLogin() {
    const email = document.getElementById("admin-email").value;
    const password = document.getElementById("admin-password").value;

    fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            if (data.role === "admin"){
                localStorage.setItem("adminToken", data.access);
                localStorage.setItem("username", data.user); 
                localStorage.setItem("isLoggedIn", "true");
                window.location.href = "index.html";
            } else {
                alert("Bạn không có quyền truy cập vào trang này!");
            }          
        } else {
            alert("Đăng nhập thất bại!");
        }
    });
}