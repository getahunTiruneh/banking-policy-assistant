const API_URL = 'http://localhost:5000/query';

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    
    showTypingIndicator();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });
        
        const data = await response.json();
        if (data.answer) {
            addMessage(data.answer, 'bot');
            if (data.sources) {
                addMessage(`Sources: ${data.sources.join(', ')}`, 'bot', true);
            }
        } else {
            addMessage("Sorry, I couldn't process your request.", 'bot');
        }
    } catch (error) {
        addMessage("Error connecting to the server.", 'bot');
    } finally {
        hideTypingIndicator();
    }
}

function addMessage(text, sender, isSmall = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    if (isSmall) messageDiv.style.fontSize = '0.8em';
    messageDiv.innerHTML = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = 'Typing...';
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) typingDiv.remove();
}