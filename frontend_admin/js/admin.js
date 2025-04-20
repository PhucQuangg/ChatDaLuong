window.onload = function() {
    const isLoggedIn = localStorage.getItem("isLoggedIn");
    const token = localStorage.getItem("adminToken");

    if (isLoggedIn === "true" && token) {
        connectWebSocket(); 
        const username = localStorage.getItem("username"); 
        if (username) {
            const usernameElements = document.querySelectorAll('.username-display');
            usernameElements.forEach(function(element) {
                element.textContent = username; 
            });
        }
        fetchAllUsers();
    } else {
        window.location.href = "login.html"; 
    }
};

let socket;
let users = {};
        function connectWebSocket() {
            const token = localStorage.getItem("adminToken");
            if (!token) return;

            socket = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("WS Data:", data);
                if (data.type === "new_conversation" || !users[data.conversation_id]) {
                    createChatBox(data.conversation_id, data.username); 
                }

                if (data.content) {
                    addMessageToChat(data.conversation_id, data.content, data.role);
                }

                if (data.type === "online_users") {
                    const onlineUsers = data.users;
                
                    const userList = document.getElementById('online-users');
                    if (userList) {
                        userList.innerHTML = ''; 
                    }
                
                    onlineUsers.forEach(user => {
                        const li = document.createElement('li');
                        li.textContent = user.username;
                        li.style.cursor = "pointer";
                        li.classList.add("user-item"); 
                        
                        const onlineStatus = document.createElement('span');
                        onlineStatus.classList.add('status-dot');
                        li.appendChild(onlineStatus);
                
                        li.addEventListener("click", () => {
                           openConversation(user.id);
                        });
                
                        userList.appendChild(li);
                    });
                }
                
            };
            socket.onclose = (event) => {
                console.log("WebSocket đã đóng kết nối!");
            };
        }

        function createChatBox(conversationId, username) {
            if (!conversationId || !username) return;
        
            const chatWindows = document.getElementById("chat-windows");
        
            const chatContainer = document.createElement("div");
            chatContainer.className = "chat-container";
            chatContainer.id = `chat-container-${conversationId}`;
            chatContainer.innerHTML = `
              <div class="chat-header">
                    <h4>Chat với user: ${username}</h4>
                    <div class="chat-controls">
                       
                        <button class="close-btn" >X</button>
                    </div>
                </div>
                <div class="chat-box" id="chat-box-${conversationId}"></div>
                <input class="message-input" type="text" id="messageInput-${conversationId}" placeholder="Nhập tin nhắn">
                <button onclick="sendMessage('${conversationId}')">Gửi</button>
            `;
            chatWindows.appendChild(chatContainer);
            users[conversationId] = chatContainer;
            const closeBtn = chatContainer.querySelector(".close-btn");
            closeBtn.addEventListener("click", () => {
                chatContainer.remove(); 
                delete users[conversationId]; 
            });

            const inputField = document.getElementById(`messageInput-${conversationId}`);
            inputField.addEventListener("keydown", function (event) {
                if (event.key === 'Enter') {
                    sendMessage(conversationId);
                }
            });
        }
        

        function sendMessage(conversationId) {
            const inputField = document.getElementById(`messageInput-${conversationId}`);
            const message = inputField.value.trim();
            if (!message.trim()) 
            {
                alert("Tin nhắn không được để trống!");
                return;
            }
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    sender: "admin",
                    role: "admin",
                    content: message,
                    conversation_id: conversationId
                }));
            }
            inputField.value = "";
        }

        function addMessageToChat(conversationId, message, role) {
            const chatBox = document.getElementById(`chat-box-${conversationId}`);
            const messageDiv = document.createElement("div");
            messageDiv.textContent = message;
            console.log("role:", role);
            messageDiv.classList.add("message", role === "admin" ? "admin-message" : "user-message");
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        function adminLogout() {
            localStorage.removeItem("adminToken");
            localStorage.removeItem("isLoggedIn"); 
            localStorage.clear();
            if (socket) socket.close(); 
            const chatWindow = document.getElementById("chat-windows");
            if (chatWindow) {
                chatWindow.innerHTML = "";
            }
            
            users = {};
            window.location.href = "login.html";
        }
       
        
    
        function openConversation(userId) {
            fetch(`http://127.0.0.1:8000/api/start-chat/${userId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem("adminToken")}`
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    createChatBox(data.conversation_id, data.username);
                    fetch(`http://127.0.0.1:8000/api/messages/${data.conversation_id}/`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem("adminToken")}`
                        }
                    })
                    .then(response => response.json())
                    .then(messages => {
                        messages.forEach(msg => {
                            addMessageToChat(data.conversation_id, msg.text, msg.role);
                        });
                    })
                    .catch(error => console.error('Lỗi khi tải tin nhắn cũ:', error));
          
                    const conversationId = data.conversation_id;
                    const inputField = document.getElementById(`messageInput-${conversationId}`);
                    
                    const sendButton = document.querySelector(`#chat-container-${conversationId} button`);
                    sendButton.addEventListener("click", function() {
                        sendMessage(conversationId);
                    });
                    
                } else {
                    alert('Không thể mở cuộc trò chuyện với user này!');
                }
            })
            .catch(error => console.error('Lỗi khi mở cuộc trò chuyện:', error));
        }

        