// sendMessage.js
document.addEventListener('DOMContentLoaded', () => {
    const chat = document.getElementById('chat');
    const inputMessage = document.getElementById('input-message');
    const sendButton = document.getElementById('send-button');

    function sendMessage() {
        const message = inputMessage.value.trim();
        if (message) {
            addMessageToChat('user-message', message);
            inputMessage.value = '';

            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            })
            .then(response => response.json())
            .then(data => {
                addMessageToChat('response-message', data.response);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    sendButton.addEventListener('click', sendMessage);

    inputMessage.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submit action if inside a form
            sendMessage();
        }
    });

    function addMessageToChat(className, message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = message;
        chat.appendChild(messageElement);
        chat.scrollTop = chat.scrollHeight;
    }
});
