let chat = document.getElementById('chat');
let inputMessage = document.getElementById('input-message');
let sendButton = document.getElementById('send-button');
let currentDB = 'db1';

const messageHistories = {
    db1: [],
    db2: [],
    db3: []
};

function updateChat() {
    chat.innerHTML = '';
    messageHistories[currentDB].forEach(msg => {
        addMessageToChat(msg.type, msg.text);
    });
    chat.scrollTop = chat.scrollHeight;
}

// Function to handle sending messages
function sendMessage() {
    
    /* 
        { type: 'user-message', text: message}
        { type: 'response',  text: message }   
    */
    
    const message = inputMessage.value.trim();
    if (message) {
        addMessageToChat('user-message', message);
        inputMessage.value = '';
        messageHistories[currentDB].push({ type: 'user-message', text: message });

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                currentDB
            }),
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChat('response-message', data.response);
            messageHistories[currentDB].push({ type: 'response-message', text: data.response });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

// Event listener for the Send button
sendButton.addEventListener('click', sendMessage);

// Event listener for the Enter key
inputMessage.addEventListener('keypress', (event) => {
    if (event.key === 'Enter'  && event.shiftKey) {
        event.preventDefault(); // Prevent default form submit action if inside a form
        sendMessage();
    }
});

// Function to add message to chat area
function addMessageToChat(className, message) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.innerHTML = message.replace(/\n/g, '<br>');
    chat.appendChild(messageElement);
    chat.scrollTop = chat.scrollHeight;
}


window.onload = function() {
    fetch('/clear_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.status);  
        messageHistories.db1 = [];
        messageHistories.db2 = [];
        messageHistories.db3 = [];
        updateChat();
    })
    .catch(error => {
        console.error('Error:', error);
    });
};
