const recordBtn = document.getElementById('recordBtn');
const statusText = document.getElementById('statusText');
const chatContainer = document.getElementById('chatContainer');
const audioPlayer = document.getElementById('audioPlayer');

const cancelBtn = document.getElementById('cancelBtn');
const exportBtn = document.getElementById('exportBtn');
const textInput = document.getElementById('textInput');
const actionIcon = document.getElementById('actionIcon');
const sidebar = document.getElementById('sidebar');
const menuBtn = document.getElementById('menuBtn');
const closeSidebarBtn = document.getElementById('closeSidebarBtn');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let isCancelled = false;
let conversationHistory = []; // To track for CSV export

if (menuBtn && sidebar && closeSidebarBtn) {
    menuBtn.addEventListener('click', () => {
        sidebar.classList.add('active');
    });
    
    closeSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });
}

// Configuração da API do Backend
const API_URL = '/api/web-chat';

recordBtn.addEventListener('click', handleActionBtn);
cancelBtn.addEventListener('click', cancelRecording);
exportBtn.addEventListener('click', exportToCSV);

textInput.addEventListener('input', () => {
    if (textInput.value.trim().length > 0) {
        actionIcon.textContent = '🚀';
    } else {
        actionIcon.textContent = '🎙️';
    }
});

textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleActionBtn();
    }
});

window.startTopic = function(topicName) {
    if (isRecording || recordBtn.disabled) return;
    
    // Close sidebar on mobile after selection
    if (sidebar && sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
    }

    const message = `Teacher Sarah, let's practice: ${topicName}`;
    textInput.value = message;
    actionIcon.textContent = '🚀';
    handleActionBtn();
};

async function handleActionBtn() {
    if (textInput.value.trim().length > 0) {
        sendTextToServer(textInput.value.trim());
    } else {
        if (!isRecording) {
            await startRecording();
        } else {
            stopRecording();
        }
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = sendAudioToServer;
        mediaRecorder.start();

        isRecording = true;
        isCancelled = false;
        recordBtn.classList.add('recording');
        cancelBtn.style.display = 'block';
        statusText.textContent = 'Recording... Tap to stop';
        statusText.classList.add('recording');
        
    } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Please allow microphone access to practice speaking.');
    }
}

function cancelRecording() {
    isCancelled = true;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    resetRecordingUI();
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop()); // Stop mic
    }
    
    if (!isCancelled) {
        resetRecordingUI(true);
    }
}

function resetRecordingUI(processing = false) {
    isRecording = false;
    recordBtn.classList.remove('recording');
    cancelBtn.style.display = 'none';
    
    if (processing) {
        statusText.textContent = 'Processing...';
        recordBtn.disabled = true; // Disable until response comes
    } else {
        statusText.textContent = 'Tap to talk';
        statusText.classList.remove('recording');
        recordBtn.disabled = false;
    }
}

function appendUserMessage(text, id = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user-message';
    if (id) msgDiv.id = id;
    msgDiv.innerHTML = `<div class="message-bubble">${text}</div>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return msgDiv;
}

window.playAudio = function(url) {
    audioPlayer.src = url;
    audioPlayer.play();
};

function appendAIMessage(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    
    // Bubble with text and replay button
    let html = `<div class="message-bubble">
        <div class="ai-text">${data.text}</div>`;
        
    if (data.audio_base64) {
        const audioSrc = "data:audio/mp3;base64," + data.audio_base64;
        html += `<button class="replay-btn" onclick="playAudio('${audioSrc}')" title="Replay Audio">🔄 Replay</button>`;
    }
    html += `</div>`;
    
    // Feedback Card (Inline)
    let hasFeedback = (data.errors && data.errors.length > 0) || (data.suggestions && data.suggestions.length > 0) || data.vocab_word;
    
    if (hasFeedback) {
        html += `<div class="feedback-card">`;
        
        if (data.vocab_word) {
            html += `<div class="feedback-section wiki-card">`;
            if (data.wiki_image) {
                html += `<img src="${data.wiki_image}" alt="${data.vocab_word}" class="wiki-image">`;
            }
            html += `<div class="wiki-info">
                        <h4>📘 ${data.vocab_word}</h4>
                        <p>${data.vocab_meaning}</p>
                        ${data.vocab_example ? `<p class="vocab-example"><em>"${data.vocab_example}"</em></p>` : ''}
                    </div>
                 </div>`;
        }

        if (data.errors && data.errors.length > 0) {
            html += `<div class="feedback-section errors">
                        <h4>⚠️ Grammar Feedback</h4>
                        <ul>${data.errors.map(e => `<li>${e}</li>`).join('')}</ul>
                     </div>`;
        }
        if (data.suggestions && data.suggestions.length > 0) {
            html += `<div class="feedback-section suggestions">
                        <h4>💡 Study Tips</h4>
                        <ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
                     </div>`;
        }
        html += `</div>`;
    }
    
    msgDiv.innerHTML = html;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message typing-id';
    msgDiv.id = 'typingIndicator';
    msgDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendTextToServer(text) {
    if (text.length > 300) {
        text = text.substring(0, 300);
    }
    textInput.value = '';
    actionIcon.textContent = '🎙️';
    
    const msgId = 'user-msg-' + Date.now();
    appendUserMessage(text, msgId);
    showTypingIndicator();
    
    resetRecordingUI(true);

    const formData = new FormData();
    formData.append('text', text);
    
    const recentHistory = conversationHistory.slice(-4).map(h => `User: ${h.user}\nTeacher Sarah: ${h.ai}`).join('\n\n');
    formData.append('history', recentHistory);

    await processServerResponse(formData, msgId, text);
}

async function sendAudioToServer() {
    if (isCancelled) return; // Abort if cancelled

    const msgId = 'user-msg-' + Date.now();
    // Adiciona placeholder
    appendUserMessage("🎙️ Transcribing...", msgId);
    showTypingIndicator();

    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    const recentHistory = conversationHistory.slice(-4).map(h => `User: ${h.user}\nTeacher Sarah: ${h.ai}`).join('\n\n');
    formData.append('history', recentHistory);

    await processServerResponse(formData, msgId, null);
}

async function processServerResponse(formData, msgId, originalText = null) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorMsg = 'Server error';
            try {
                const errData = await response.json();
                if (errData.error) errorMsg = errData.error;
            } catch(e) {}
            throw new Error(errorMsg);
        }

        const data = await response.json();
        removeTypingIndicator();
        
        // Atualiza a mensagem do usuário com a transcrição (se for áudio)
        const userMsgEl = document.getElementById(msgId);
        if (userMsgEl && data.transcription) {
            userMsgEl.querySelector('.message-bubble').textContent = data.transcription;
        } else if (userMsgEl && !originalText) {
            userMsgEl.querySelector('.message-bubble').textContent = "🎤 Audio Sent";
        }
        
        // Exibe a resposta da AI + Feedback + Replay
        if(data.text) {
            appendAIMessage(data);
            
            // Push to history
            const transcription = data.transcription || originalText || 'Audio Sent';
            conversationHistory.push({
                user: transcription,
                ai: data.text,
                errors: data.errors ? data.errors.join(' | ') : '',
                tips: data.suggestions ? data.suggestions.join(' | ') : ''
            });
        }

        // Toca o áudio original
        if(data.audio_base64) {
            const audioSrc = "data:audio/mp3;base64," + data.audio_base64;
            playAudio(audioSrc);
        }

    } catch (error) {
        console.error('Error communicating with server:', error);
        removeTypingIndicator();
        let msgText = "Sorry, I had a technical problem! Check my connection.";
        if (error.message && error.message !== 'Server error' && error.message !== 'Failed to fetch') {
            msgText = error.message;
        }
        appendAIMessage({text: "⚠️ " + msgText});
    } finally {
        if (!isCancelled) {
            resetRecordingUI(false);
        }
    }
}

function exportToCSV() {
    if (conversationHistory.length === 0) {
        alert("No conversation to export yet!");
        return;
    }

    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "User Transcription,Teacher Response,Grammar Feedback,Study Tips\n";
    
    conversationHistory.forEach(row => {
        // Escape quotes
        const u = `"${row.user.replace(/"/g, '""')}"`;
        const a = `"${row.ai.replace(/"/g, '""')}"`;
        const e = `"${row.errors.replace(/"/g, '""')}"`;
        const t = `"${row.tips.replace(/"/g, '""')}"`;
        csvContent += `${u},${a},${e},${t}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "teacher_sarah_history.csv");
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
}
