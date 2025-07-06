document.addEventListener("DOMContentLoaded", function () {
    const contactList = document.getElementById("contactList");
    const addContactButton = document.getElementById("addContactButton");
    const sosButton = document.getElementById("sosButton");
    const sosVoiceButton = document.getElementById("sosVoiceButton");
    const stopVoiceButton = document.getElementById("stopVoiceButton");
    const contactName = document.getElementById("contactName");
    const contactEmail = document.getElementById("contactEmail");

    let contacts = [];
    let recordedCommand = localStorage.getItem("savedVoiceCommand");
    let recognition;
    let isListening = false;
    let sosTimeout = null;

    function getCSRFToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    }

    function fetchContacts() {
        fetch("/get-contacts/", { method: "GET" })
            .then(response => response.json())
            .then(data => {
                contacts = data.contacts;
                updateContactList();
            })
            .catch(error => console.error("Error fetching contacts:", error));
    }

    function updateContactList() {
        contactList.innerHTML = "";
        contacts.forEach(contact => {
            const listItem = document.createElement("li");
            listItem.textContent = `${contact.name}: ${contact.email}`;

            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "❌";
            deleteBtn.style.marginLeft = "10px";
            deleteBtn.addEventListener("click", () => deleteContact(contact.id));

            listItem.appendChild(deleteBtn);
            contactList.appendChild(listItem);
        });

        const enableButtons = contacts.length >= 5;
        sosButton.disabled = !enableButtons;
        sosVoiceButton.disabled = !enableButtons;
    }

    function addContact() {
        const name = contactName.value.trim();
        const email = contactEmail.value.trim();

        if (!name || !email) {
            alert("Please enter both name and email.");
            return;
        }

        if (contacts.length >= 5) {
            alert("You can only add up to 5 contacts.");
            return;
        }

        if (contacts.find(contact => contact.email === email)) {
            alert("This email is already added.");
            return;
        }

        fetch("/add-contact/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ name, email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                contacts.push({ id: data.id, name, email });
                updateContactList();
                contactName.value = "";
                contactEmail.value = "";
            } else {
                alert("Failed to add contact.");
            }
        })
        .catch(error => console.error("Error adding contact:", error));
    }

    function deleteContact(contactId) {
        fetch(`/delete-contact/${contactId}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                contacts = contacts.filter(contact => contact.id !== contactId);
                updateContactList();
            } else {
                alert("Failed to delete contact.");
            }
        })
        .catch(error => console.error("Error deleting contact:", error));
    }

    function getLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => callback(position),
                error => {
                    console.error("Error getting location:", error);
                    callback(null);
                }
            );
        } else {
            console.error("Geolocation is not supported by this browser.");
            callback(null);
        }
    }

    function sendSOSAlert() {
        getLocation(position => {
            let location = { latitude: null, longitude: null };
            let locationMessage = "📍 Location not available";

            if (position) {
                location.latitude = position.coords.latitude;
                location.longitude = position.coords.longitude;
                locationMessage = `📍 Location: https://www.google.com/maps?q=${location.latitude},${location.longitude}`;
            }

            fetch("/send-sos-email/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({ contacts, location, message: `🚨 SOS alert triggered!\n\n${locationMessage}` })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("🚀 SOS alert sent successfully!");
                } else {
                    alert("❌ Failed to send SOS alert.");
                }
            })
            .catch(error => console.error("Error sending SOS alert:", error));
        });
    }

    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Your browser does not support voice recognition.");
            return null;
        }

        let recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.lang = "en-US";
        recognition.interimResults = false;

        return recognition;
    }

    function recordVoiceCommand() {
        console.log("🎙️ Starting voice command recording...");

        let tempRecognition = initSpeechRecognition();
        if (!tempRecognition) return;

        tempRecognition.onstart = function () {
            alert("🎤 Speak your SOS command now...");
        };

        tempRecognition.onspeechend = function () {
            tempRecognition.stop();
        };

        tempRecognition.onresult = function (event) {
            let spokenText = event.results[0][0].transcript.toLowerCase().trim();
            console.log("🔊 Recorded voice command:", spokenText);
            alert(`✅ Voice command saved: "${spokenText}"`);

            localStorage.setItem("savedVoiceCommand", spokenText);
            recordedCommand = spokenText;

            startListeningForCommand();
        };

        tempRecognition.onerror = function (event) {
            console.error("❌ Voice recognition error:", event.error);
            alert("⚠️ Error: " + event.error);
        };

        tempRecognition.start();
    }

    function startListeningForCommand() {
        recordedCommand = localStorage.getItem("savedVoiceCommand");
        if (!recordedCommand) {
            alert("⚠️ No voice command recorded. Please record a command first.");
            return;
        }

        recognition = initSpeechRecognition();
        if (!recognition) return;

        console.log("🎤 Always Listening for voice command...");
        recognition.start();
        isListening = true;

        recognition.onresult = function (event) {
            const spokenCommand = event.results[0][0].transcript.toLowerCase().trim();
            console.log(`🔊 Detected command: "${spokenCommand}"`);

            if (spokenCommand === recordedCommand) {
                showConfirmationPopup();
            }
        };

        recognition.onend = function () {
            console.log("⏳ Restarting recognition to keep listening...");
            if (isListening) {
                setTimeout(() => recognition.start(), 100);
            }
        };

        recognition.onerror = function (event) {
            console.error("❌ Error detecting voice:", event.error);
            if (event.error === "no-speech" || event.error === "network") {
                setTimeout(() => recognition.start(), 100);
            }
        };
    }

    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
            isListening = false;
            alert("Voice recognition stopped.");
        }
    }

    function showConfirmationPopup() {
        const confirmation = confirm("🔴 Detected your voice command! Send SOS alert?");
        
        if (confirmation) {
            sendSOSAlert();
        } else {
            sosTimeout = setTimeout(() => {
                const finalCheck = confirm("⏳ No response detected! Sending SOS alert now...");
                if (finalCheck) {
                    sendSOSAlert();
                }
            }, 5000);
        }
    }

    addContactButton.addEventListener("click", addContact);
    sosButton.addEventListener("click", sendSOSAlert);
    sosVoiceButton.addEventListener("click", recordVoiceCommand);
    stopVoiceButton.addEventListener("click", stopListening);

    fetchContacts();

    if (recordedCommand) {
        startListeningForCommand();
    }
});
