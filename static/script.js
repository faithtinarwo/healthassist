document.getElementById("sendMessageButton").addEventListener("click", sendMessage);

async function sendMessage() {
    const userMessage = document.getElementById("userInput").value.trim();
    if (!userMessage) return;

    // Display user's message
    const chatbox = document.querySelector(".chatbox");
    chatbox.innerHTML += `<div><strong>You:</strong> ${userMessage}</div>`;

    // Send the message to Flask backend
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });
    const data = await response.json();

    // Display bot's reply
    if (data.reply) {
        chatbox.innerHTML += `<div><strong>Bot:</strong> ${data.reply}</div>`;
    }
}
