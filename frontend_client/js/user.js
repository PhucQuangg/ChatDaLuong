let socket;
let conversationId;

function login() {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem("accessToken", data.access);
            conversationId = data.conversation_id;
            localStorage.setItem("conversationId", conversationId);
            localStorage.setItem("username", data.user);
            window.location.href = "index.html";

        } else {
            alert("Đăng nhập thất bại!");
        }
    });
}

function register() {
    event.preventDefault();
    const emailInput = document.getElementById("email-register");
    const passwordInput = document.getElementById("password-register");
    const usernameInput = document.getElementById("username-register");

    const email = emailInput.value;
    const password = passwordInput.value;
    const username = usernameInput.value;

    fetch("http://localhost:8000/api/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => {
        if (response.status === 201) {
            alert("Đăng ký thành công!");

            emailInput.value = "";
            passwordInput.value = "";
            usernameInput.value = "";

            return response.json();
        } else {
            return response.json().then(data => {
                alert("Đăng ký thất bại");
            });
        }
    })
    .catch(() => {
        alert("Đã xảy ra lỗi! Vui lòng thử lại.");
    });
}


function logout() {
    localStorage.clear();

    if (socket) {
        socket.close();
        socket = null;
    }

    conversationId = null;

    const authArea = document.getElementById("auth-area");
    if (authArea) {
        authArea.innerHTML = `
            <li><a href="#signin-modal" data-toggle="modal">Sign in / Sign up</a></li>
        `;
    }
}

function connectWebSocket() {
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    socket = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.role === 'AI' || data.role === 'admin') {
            addMessageToChat(data.content, data.role);
        }
    };
}

function sendMessage(inputField) {
    const message = inputField.value.trim();
    if (!message.trim()) {
        alert("Tin nhắn không được để trống!");
        return;
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            content: message,
            conversation_id: conversationId
        }));

        addMessageToChat(message, "user");

        inputField.value = "";

    }
}

function addMessageToChat(message, role) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.textContent = message;

    if (role === "user") {
        messageDiv.classList.add("message", "user-message");
        chatBox.appendChild(messageDiv);
    } 
    else if (role === "AI") {
        messageDiv.classList.add("message", "ai-message");
        chatBox.appendChild(messageDiv);
    } 
    else if (role === "admin") {
        messageDiv.classList.add("message", "admin-message");
        chatBox.appendChild(messageDiv);
    } 
    else {
        messageDiv.classList.add("message", "unknown-message"); 
        chatBox.appendChild(messageDiv);
    }

    chatBox.scrollTop = chatBox.scrollHeight; 
}

let isChatOpen = false;

        function toggleChat() {
            const chatWidget = document.getElementById("chat-widget");
            isChatOpen = !isChatOpen;
            if (isChatOpen) {
                chatWidget.style.display = "flex";
            } else {
                chatWidget.style.display = "none";
            }
        }

        function loadMessagesFromServer() {
            const token = localStorage.getItem("accessToken");
            const conversationId = localStorage.getItem("conversationId");
        
            if (!token || !conversationId) return;
        
            fetch(`http://localhost:8000/api/messages/${conversationId}/`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            })
            .then(response => response.json())
            .then(messages => {
                messages.forEach(msg => {
                    addMessageToChat(msg.text, msg.role);
                });
            })
            .catch(error => {
                console.error("Lỗi khi tải tin nhắn:", error);
            });
        }
        

        document.addEventListener("DOMContentLoaded", function () {
            const inputFields = document.querySelectorAll(".messageInput"); // Lấy tất cả các ô nhập tin nhắn
            inputFields.forEach(inputField => {
                inputField.addEventListener("keydown", function (event) {
                    if (event.key === "Enter") {
                        sendMessage(inputField); // Truyền inputField vào hàm gửi tin nhắn
                    }
                });
            });
        });
        