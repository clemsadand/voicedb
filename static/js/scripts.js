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

    // Call the API
    simulateResponse(message);
}

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
    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.status === "success") {
            // Check if this is a statistics response
            if (data.is_statistics && data.overview && data.by_category) {
                console.log("📊 Displaying statistics");
                displayStats(data);
            } else if (data.response) {
                addMessage(data.response, 'bot');
                
                // If there's data (products), display them
                if (data.data && data.data.length > 0) {
                    displayProductData(data.data);
                }
            } else {
                addMessage("Command executed successfully.", 'bot');
            }
        } else {
            addMessage(data.message || "I don't know what to do. Please be more clear.", "bot");
        }
    })
    .catch(error => {
        hideLoading();
        console.error("Fetch error:", error);
        addMessage("Could not connect to the server.", "bot");
    });
}

function displayStats(result) {
    const messagesArea = document.getElementById('messagesArea');
    
    // Display overview statistics
    const overviewDiv = document.createElement('div');
    overviewDiv.className = 'message bot';
    overviewDiv.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="message-content">
            <strong>📊 Database Overview:</strong><br>
            • Total products: ${result.overview.total_products}<br>
            • Average price: $${result.overview.average_price}<br>
            • Total inventory value: $${result.overview.total_inventory_value}<br>
            • Average quantity: ${result.overview.average_quantity}
        </div>
    `;
    
    messagesArea.appendChild(overviewDiv);
    
    // Display category statistics in a table
    if (result.by_category && result.by_category.length > 0) {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'message bot';
        
        let tableHTML = `
            <div class="avatar bot">AI</div>
            <div class="message-content">
                <strong>📈 Statistics by Category:</strong>
                <table style="width: 100%; margin-top: 10px; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: var(--bg-secondary);">
                            <th style="padding: 8px; text-align: left; border: 1px solid var(--border-color);">Category</th>
                            <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Count</th>
                            <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Total Value</th>
                            <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Avg Price</th>
                            <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Common Color</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        result.by_category.forEach(cat => {
            tableHTML += `
                <tr>
                    <td style="padding: 8px; border: 1px solid var(--border-color);">${cat.category}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">${cat.product_count}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">$${cat.total_value}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">$${cat.avg_price}</td>
                    <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">${cat.most_common_color || 'N/A'}</td>
                </tr>
            `;
        });
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        categoryDiv.innerHTML = tableHTML;
        messagesArea.appendChild(categoryDiv);
    }
    
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function displayProductData(products) {
    const messagesArea = document.getElementById('messagesArea');
    
    if (products.length === 0) return;
    
    const productsDiv = document.createElement('div');
    productsDiv.className = 'message bot';
    
    let tableHTML = `
        <div class="avatar bot">AI</div>
        <div class="message-content">
            <strong>🛍️ Product Details:</strong>
            <table style="width: 100%; margin-top: 10px; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: var(--bg-secondary);">
                        <th style="padding: 8px; text-align: left; border: 1px solid var(--border-color);">ID</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid var(--border-color);">Name</th>
                        <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Category</th>
                        <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Color</th>
                        <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Quantity</th>
                        <th style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">Price</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    products.slice(0, 10).forEach(product => { // Limit to first 10 products
        tableHTML += `
            <tr>
                <td style="padding: 8px; border: 1px solid var(--border-color);">${product.id}</td>
                <td style="padding: 8px; border: 1px solid var(--border-color);">${product.name}</td>
                <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">${product.category}</td>
                <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">${product.color}</td>
                <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">${product.quantity}</td>
                <td style="padding: 8px; text-align: center; border: 1px solid var(--border-color);">$${product.price}</td>
            </tr>
        `;
    });
    
    if (products.length > 10) {
        tableHTML += `
            <tr>
                <td colspan="6" style="padding: 8px; text-align: center; border: 1px solid var(--border-color); font-style: italic;">
                    ... and ${products.length - 10} more products
                </td>
            </tr>
        `;
    }
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    productsDiv.innerHTML = tableHTML;
    messagesArea.appendChild(productsDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
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

async function processAudioTranscription(audioBlob) {
    const messageInput = document.getElementById('messageInput');
    messageInput.placeholder = 'Transcribing audio...';
    
    const formData = new FormData();
    formData.append("audio_recording", audioBlob, "recording.webm");
    
    try {
        const response = await fetch("/api/transcribe", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
            messageInput.placeholder = 'Type your message here...';
            messageInput.value = data.transcription || '';

            autoResize(messageInput);
            updateSendButtonState();
            messageInput.focus();
        } else {
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


// Help setup
function openHelpModal() {
    document.getElementById('helpModal').style.display = 'block';
    localStorage.setItem('helpShown', 'true');  // Set the flag
}


function closeHelpModal() {
    document.getElementById('helpModal').style.display = 'none';
}

// Optional: Close on click outside the modal
window.onclick = function(event) {
    const modal = document.getElementById('helpModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

document.addEventListener('DOMContentLoaded', function() {
    updateSendButtonState();
    setupVoiceRecording();

    // Auto-open help for first-time users
    if (!localStorage.getItem('helpShown')) {
        openHelpModal();
    }
});

