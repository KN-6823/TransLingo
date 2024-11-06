class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.messages = [];
        this.option = ""; // Store the selected option
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox));

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });

        // Show default message when the chatbox is opened
        this.showDefaultMessage(chatBox);
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active');
            this.showDefaultMessage(chatbox); // Show default message when opened
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }

    showDefaultMessage(chatbox) {
        // Only show default message if the chatbox is being opened for the first time
        if (this.messages.length === 0) {
            const defaultMessage = { name: "Sam", message: "Welcome! Please type 'start' to see options." };
            this.messages.push(defaultMessage);
            this.updateChatText(chatbox);
        }
    }
    

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let message = textField.value;

        if (message.trim() === "") {
            return;
        }

        // Add user message to chat
        let userMessage = { name: "User", message: message };
        this.messages.push(userMessage);
        this.updateChatText(chatbox);

        // Send the user message to the backend
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message, option: this.option }) // Passing the message and the selected option
        })
        .then(response => response.json())
        .then(data => {
            // Add bot response to chat
            let botMessage = { name: "Sam", message: data.response };
            this.messages.push(botMessage);
            this.updateChatText(chatbox);

            // Show option buttons if returned from the server
            if (data.options) {
                this.showOptions(chatbox, data.options);
            }

            // Clear the input field after sending the message
            textField.value = '';
        })
        .catch(error => {
            console.error("Error:", error);
            textField.value = '';
        });
    }

    showOptions(chatbox, options) {
        // Create a div for options buttons
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'options';

        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'optionButton';
            button.textContent = option.label;
            button.setAttribute('data-option', option.value);
            button.addEventListener('click', () => this.selectOption(option.value, chatbox));
            optionsDiv.appendChild(button);
        });

        // Clear previous options before adding new ones
        const existingOptions = chatbox.querySelector('.options');
        if (existingOptions) {
            existingOptions.remove();
        }

        chatbox.querySelector('.chatbox__messages div').appendChild(optionsDiv);
    }

    selectOption(option, chatbox) {
        this.option = option; // Save selected option
        const message = `You selected: ${option}`;
        let botMessage = { name: "Sam", message: message };
        this.messages.push(botMessage);
        this.updateChatText(chatbox);

        // Clear the input field and remove options after selection
        chatbox.querySelector('input').value = '';
        const existingOptions = chatbox.querySelector('.options');
        if (existingOptions) {
            existingOptions.remove();
        }

        // Optionally, send an empty message to trigger the functionality for the selected option
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: "", option: this.option }) // Trigger the selected option
        })
        .then(response => response.json())
        .then(data => {
            let optionResponse = { name: "Sam", message: data.response };
            this.messages.push(optionResponse);
            this.updateChatText(chatbox);
        })
        .catch(error => console.error("Error:", error));
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.forEach(item => {
            if (item.name === "Sam") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages div');
        chatmessage.innerHTML = html;
        chatmessage.scrollTop = chatmessage.scrollHeight; // Scroll to the bottom
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const chatbox = new Chatbox();
    chatbox.display();
});
