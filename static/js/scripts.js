// Global state
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];
        // On page load, read the saved theme or default to 'light'
		let currentTheme = localStorage.getItem('theme') || 'light';

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateSendButtonState();
            setupVoiceRecording();
        });

        // Theme management

		function applyTheme(theme) {
			document.body.setAttribute('data-theme', theme);
			const themeToggle = document.querySelector('.theme-toggle');
			themeToggle.textContent = theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
		}

		// Initialize theme when page loads
		applyTheme(currentTheme);

		function toggleTheme() {
			currentTheme = currentTheme === 'light' ? 'dark' : 'light';
			applyTheme(currentTheme);

			// Save the current theme in localStorage
			localStorage.setItem('theme', currentTheme);
		}
		
		//
		function autoResize(textarea) {
			textarea.style.height = "auto"; // Reset height
			textarea.style.height = textarea.scrollHeight + "px";
		}



        // Input handling
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        function autoResize(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            updateSendButtonState();
        }

        function updateSendButtonState() {
            const input = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = !input.value.trim();
        }

        // Message handling
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Add user message
            addMessage(message, 'user');
            
            // Clear input
            input.value = '';
            input.style.height = 'auto';
            updateSendButtonState();

            // Show loading
            showLoading();

            // Here you would call your API
            // For demo, we'll simulate a response
            setTimeout(() => {
                hideLoading();
                simulateResponse(message);
            }, 1500);
        }

//        function addMessage(content, sender) {
//            const messagesArea = document.getElementById('messagesArea');
//            const emptyState = messagesArea.querySelector('.empty-state');
//            
//            if (emptyState) {
//                emptyState.remove();
//            }

//            const messageDiv = document.createElement('div');
//            messageDiv.className = `message ${sender}`;
//            
//            const avatar = document.createElement('div');
//            avatar.className = `avatar ${sender}`;
//            avatar.textContent = sender === 'user' ? 'U' : 'AI';
//            
//            const content_div = document.createElement('div');
//            content_div.className = 'message-content';
//            content_div.textContent = content;
//            
//            messageDiv.appendChild(avatar);
//            messageDiv.appendChild(content_div);
//            
//            messagesArea.appendChild(messageDiv);
//            messagesArea.scrollTop = messagesArea.scrollHeight;
//        }
function addMessage(content, sender) {
    const messagesArea = document.getElementById('messagesArea');
    const emptyState = messagesArea.querySelector('.empty-state');
    
    if (emptyState) {
        emptyState.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `avatar ${sender}`;
    avatar.textContent = sender === 'user' ? 'U' : 'AI';
    
    const content_div = document.createElement('div');
    content_div.className = 'message-content';

    // Check if content is an object
    if (typeof content === 'object' && content !== null) {
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr><th>Key</th><th>Value</th></tr>
            </thead>
            <tbody>
                ${Object.entries(content).map(([key, value]) => `
                    <tr>
                        <td>${key}</td>
                        <td>${typeof value === 'object' ? JSON.stringify(value) : value}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        content_div.appendChild(table);
    } else {
        // Display as plain text
        content_div.textContent = content;
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content_div);
    
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}


        function showLoading() {
            const messagesArea = document.getElementById('messagesArea');
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot';
            loadingDiv.id = 'loadingMessage';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar bot';
            avatar.textContent = 'AI';
            
            const loadingContent = document.createElement('div');
            loadingContent.className = 'message-content loading';
            loadingContent.innerHTML = '<div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div>';
            
            loadingDiv.appendChild(avatar);
            loadingDiv.appendChild(loadingContent);
            
            messagesArea.appendChild(loadingDiv);
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }

        function hideLoading() {
            const loadingMessage = document.getElementById('loadingMessage');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }

function simulateResponse(userMessage) {
    showLoading(); // 👈 optional loading animation

    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.status === "success") {
            if (data.overview && data.by_category) {
                //console.log("Yes")
                addMessage(data.overall);
                
            } else if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                addMessage("Command executed successfully.", 'bot');
            }
        } else {
            addMessage("I don't know what to do. Please be more clear.", "bot");
        }
    })
    .catch(error => {
        hideLoading();
        console.error("Fetch error:", error);
        addMessage("Could not connect to the server.", "bot");
    });
}

        // Voice recording functionality
        function setupVoiceRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.warn('Voice recording not supported in this browser');
                document.getElementById('voiceBtn').style.display = 'none';
                return;
            }
        }

        async function toggleVoiceRecording() {
            if (isRecording) {
                stopRecording();
            } else {
                await startRecording();
            }
        }
        
async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {audioChunks.push(event.data);};
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    await processAudioTranscription(audioBlob);
                    
                    // Stop all tracks to release microphone
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start();
                isRecording = true;
                updateRecordingUI();
                
            } catch (error) {
                console.error('Error starting recording:', error);
                alert('Could not access microphone. Please check permissions.');
            }
        }

function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            isRecording = false;
            updateRecordingUI();
        }


// Recommended: Using async/await for cleaner code
async function processAudioTranscription(audioBlob) {
    const messageInput = document.getElementById('messageInput');
    messageInput.placeholder = 'Transcribing audio...';
    
    const formData = new FormData();
    // Use a more accurate filename extension
    formData.append("audio_recording", audioBlob, "recording.webm");
    
    try {
        const response = await fetch("/api/transcribe", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
        	messageInput.placeholder = 'Type your message here...';
            // Use the transcription from the server
            messageInput.value = data.transcription || '';

            // Update your UI as needed
            autoResize(messageInput);
            updateSendButtonState();
            messageInput.focus();
            
            //addMessage(data.transcription, "user"); 
        } else {
            // Display the specific error from the server
            const errorMessage = data.error || "Action unclear. Please try again.";
            addMessage(errorMessage, "bot");
        }
    } catch (error) {
        console.error('Transcription error:', error);
        messageInput.placeholder = 'Type your message here...';
        addMessage("Sorry, transcription failed. Please check your connection or try again.", "bot");
    }
}

function updateRecordingUI() {
            const voiceBtn = document.getElementById('voiceBtn');
            const inputContainer = document.getElementById('inputContainer');
            
            if (isRecording) {
                voiceBtn.classList.add('recording');
                voiceBtn.title = 'Stop recording';
                inputContainer.classList.add('recording');
                
                // Add voice status indicator
                const voiceStatus = document.createElement('div');
                voiceStatus.className = 'voice-status';
                voiceStatus.textContent = '🎤 Recording... Click to stop';
                inputContainer.appendChild(voiceStatus);
                
            } else {
                voiceBtn.classList.remove('recording');
                voiceBtn.title = 'Voice recording';
                inputContainer.classList.remove('recording');
                
                // Remove voice status indicator
                const voiceStatus = inputContainer.querySelector('.voice-status');
                if (voiceStatus) {
                    voiceStatus.remove();
                }
            }
        }

function displayStats(result) {
    const messagesArea = document.getElementById('messagesArea');

    let overview = result.overview;
    let categories = result.by_category;

    let overviewHTML = `
        <div class="message bot">
            <div class="avatar bot">AI</div>
            <div class="message-content">
                <strong>📊 Overview:</strong><br>
                Total products: ${overview.total_products}<br>
                Average price: $${overview.average_price}<br>
                Total inventory value: $${overview.total_inventory_value}<br>
                Average quantity: ${overview.average_quantity}
            </div>
        </div>
    `;

    let table = `
        <div class="message bot">
        <div class="avatar bot">AI</div>
        <div class="message-content">
        <strong>📈 Stats by Category:</strong>
        <table>
            <thead>
                <tr>
                    <th>Category</th><th>Count</th><th>Total Value</th><th>Avg Price</th><th>Common Color</th>
                </tr>
            </thead>
            <tbody>
    `;

    categories.forEach(cat => {
        table += `
            <tr>
                <td>${cat.category}</td>
                <td>${cat.product_count}</td>
                <td>$${cat.total_value}</td>
                <td>$${cat.avg_price}</td>
                <td>${cat.most_common_color}</td>
            </tr>
        `;
    });

    table += `</tbody></table></div></div>`;

    messagesArea.innerHTML += overviewHTML + table;
    messagesArea.scrollTop = messagesArea.scrollHeight;
}



