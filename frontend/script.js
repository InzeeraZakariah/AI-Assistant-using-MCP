const API_URL = "http://127.0.0.1:8000";

// ============================================================
// DOM ELEMENTS
// ============================================================
const chat = document.getElementById("chat");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");

// ============================================================
// BACKEND CONNECTION CHECK
// ============================================================
async function checkBackend() {
    try {
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
            statusText.textContent = "Connected";
            statusDot.classList.add("connected");
        } else {
            statusText.textContent = "Backend error";
        }
    } catch (error) {
        statusText.textContent = "Backend offline";
        console.error(error);
    }
}

// ============================================================
// CHAT MESSAGE HANDLING
// ============================================================
function addMessage(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const content = document.createElement("div");
    content.className = "message-content";

    const name = document.createElement("strong");
    name.textContent = sender === "user" ? "You" : "Assistant";

    const text = document.createElement("p");
    text.textContent = message;

    content.appendChild(name);
    content.appendChild(text);
    messageDiv.appendChild(content);
    chat.appendChild(messageDiv);

    // Auto-scroll to bottom
    chat.scrollTop = chat.scrollHeight;
}

// ============================================================
// SEND MESSAGE TO BACKEND
// ============================================================
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Show user message
    addMessage(message, "user");
    messageInput.value = "";
    sendButton.disabled = true;

    // Show loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message assistant";
    loadingDiv.innerHTML = `
        <div class="message-content">
            <strong>Assistant</strong>
            <p class="loading">Thinking...</p>
        </div>
    `;
    chat.appendChild(loadingDiv);
    chat.scrollTop = chat.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        loadingDiv.remove();

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.response, "assistant");

    } catch (error) {
        loadingDiv.remove();
        addMessage("Sorry, I could not connect to the backend.", "assistant");
        console.error("Error:", error);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}


function sendSuggestion(message) {
    messageInput.value = message;
    sendMessage();
}

messageInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !sendButton.disabled) {
        sendMessage();
    }
});


checkBackend();
