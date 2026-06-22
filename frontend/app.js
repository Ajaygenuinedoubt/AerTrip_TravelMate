// javascript
const socket = new WebSocket("ws://localhost:8000/ws");

const chat = document.getElementById("chat");

function addMessage(role, text, latency = null) {
    const div = document.createElement("div");

    div.classList.add("message");
    div.classList.add(role === "user" ? "user" : "bot");

    div.innerHTML = `
        <b>${role.toUpperCase()}</b><br>
        ${text}
    `;

    if (latency !== null) {
        div.innerHTML += `
            <div class="latency">
                Latency: ${latency}s
            </div>
        `;
    }

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

socket.onopen = () => {
    console.log("Connected to TravelMate AI");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "greeting") {
        addMessage("bot", data.message);
        speak(data.message);
    } 
    else if (data.type === "response") {
        addMessage(
            "bot",
            data.message,
            data.latency
        );

        speak(data.message);

        const status =
            document.getElementById("status");

        if (status) {
            status.innerText =
                `Intent: ${data.intent}`;
        }
    }
};

socket.onerror = (error) => {
    console.error(
        "WebSocket Error:",
        error
    );
};

socket.onclose = () => {
    console.log(
        "WebSocket disconnected"
    );
};

function sendMessage(text) {

    if (
        socket.readyState !==
        WebSocket.OPEN
    ) {
        console.error(
            "WebSocket not connected"
        );
        return;
    }

    socket.send(
        JSON.stringify({
            text: text
        })
    );
}

const micBtn =
    document.getElementById("micBtn");

if (micBtn) {
    micBtn.addEventListener(
        "click",
        startListening
    );
}

const stopBtn =
    document.getElementById("stopBtn");

if (stopBtn) {
    stopBtn.addEventListener(
        "click",
        () => {
            speechSynthesis.cancel();
            stopListening();
        }
    );
}

