// ```javascript
// =====================================================
// Speech Recognition Setup
// =====================================================

let recognition;

let isListening = false;

let lastTranscript = "";

let lastSentText = "";

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

if (!SpeechRecognition) {

    alert(
        "Speech Recognition is not supported in this browser. Please use Google Chrome."
    );

} else {

    recognition = new SpeechRecognition();

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.maxAlternatives = 1;

    // Default language from selector
    const languageSelect =
        document.getElementById(
            "languageSelect"
        );

    if (languageSelect) {

        recognition.lang =
            languageSelect.value;

        languageSelect.addEventListener(
            "change",
            () => {

                recognition.lang =
                    languageSelect.value;

                console.log(
                    "Language Changed:",
                    recognition.lang
                );

                document.getElementById(
                    "status"
                ).innerText =
                    `Language: ${languageSelect.options[
                        languageSelect.selectedIndex
                    ].text}`;
            }
        );

    } else {

        recognition.lang = "en-US";
    }
}


// =====================================================
// Start Listening
// =====================================================

function startListening() {

    if (!recognition) {
        return;
    }

    if (isListening) {
        return;
    }

    try {

        isListening = true;

        document.getElementById(
            "status"
        ).innerText =
            "🎤 Listening...";

        // Barge-In
        speechSynthesis.cancel();

        recognition.start();

    } catch (error) {

        console.error(
            "Start Listening Error:",
            error
        );

        isListening = false;
    }
}


// =====================================================
// Stop Listening
// =====================================================

function stopListening() {

    try {

        if (
            recognition &&
            isListening
        ) {
            recognition.stop();
        }

    } catch (error) {

        console.error(
            "Stop Listening Error:",
            error
        );
    }

    isListening = false;

    document.getElementById(
        "status"
    ).innerText =
        "Ready";
}


// =====================================================
// Speech Recognition Result
// =====================================================

recognition.onresult = (event) => {

    try {

        const result =
            event.results[
                event.results.length - 1
            ];

        if (!result.isFinal) {
            return;
        }

        const text =
            result[0].transcript.trim();

        if (!text) {
            return;
        }

        if (text.length < 3) {

            console.log(
                "Ignored short transcript:",
                text
            );

            return;
        }

        if (
            text.toLowerCase() ===
            lastTranscript.toLowerCase()
        ) {

            console.log(
                "Duplicate transcript ignored"
            );

            return;
        }

        lastTranscript = text;

        addMessage(
            "user",
            text
        );

        sendMessage(text);

    } catch (error) {

        console.error(
            "Speech Processing Error:",
            error
        );
    }

    stopListening();
};


// =====================================================
// Recognition Events
// =====================================================

recognition.onstart = () => {

    document.getElementById(
        "status"
    ).innerText =
        "🎤 Listening...";
};

recognition.onend = () => {

    isListening = false;

    document.getElementById(
        "status"
    ).innerText =
        "Ready";
};

recognition.onerror = (event) => {

    console.error(
        "Speech Recognition Error:",
        event.error
    );

    document.getElementById(
        "status"
    ).innerText =
        `Error: ${event.error}`;

    stopListening();
};


// =====================================================
// Text To Speech
// =====================================================

function speak(text) {

    if (!text) {
        return;
    }

    // Stop current speech
    speechSynthesis.cancel();

    const utterance =
        new SpeechSynthesisUtterance(
            text
        );

    utterance.rate = 1;

    utterance.pitch = 1;

    utterance.volume = 1;

    // Use selected language
    const languageSelect =
        document.getElementById(
            "languageSelect"
        );

    if (languageSelect) {

        utterance.lang =
            languageSelect.value;

    } else {

        utterance.lang =
            recognition
                ? recognition.lang
                : "en-US";
    }

    utterance.onstart = () => {

        document.getElementById(
            "status"
        ).innerText =
            "🔊 Speaking...";
    };

    utterance.onend = () => {

        document.getElementById(
            "status"
        ).innerText =
            "Ready";
    };

    utterance.onerror = (error) => {

        console.error(
            "Speech Synthesis Error:",
            error
        );
    };

    speechSynthesis.speak(
        utterance
    );
}


// =====================================================
// Safe WebSocket Sender
// =====================================================

function sendMessage(text) {

    if (!text) {
        return;
    }

    if (
        text.toLowerCase() ===
        lastSentText.toLowerCase()
    ) {

        console.log(
            "Duplicate send blocked"
        );

        return;
    }

    lastSentText = text;

    if (
        socket &&
        socket.readyState ===
            WebSocket.OPEN
    ) {

        socket.send(
            JSON.stringify({
                text: text
            })
        );

    } else {

        console.error(
            "WebSocket not connected"
        );
    }
}

