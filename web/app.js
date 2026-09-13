/* ==========================================================================
   REACT TRAVEL AGENT CHATBOT UI - STREAMING ENGINE & FORMATTER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const presetChips = document.getElementById('presetChips');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');
    const sidebar = document.getElementById('sidebar');
    const openWaterfallBtn = document.getElementById('openWaterfallBtn');
    const traceTree = document.getElementById('traceTree');
    
    const statusProvider = document.getElementById('statusProvider');
    const statusModel = document.getElementById('statusModel');
    const statusServer = document.getElementById('statusServer');

    let currentMode = 'react';
    let isProcessing = false;
    let traceHistory = [];

    // Mode Selector Handler
    document.querySelectorAll('input[name="agentMode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentMode = e.target.value;
            document.querySelectorAll('.mode-card').forEach(card => card.classList.remove('active'));
            e.target.closest('.mode-card').classList.add('active');
        });
    });

    // Sidebar Toggles
    toggleSidebarBtn.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
    closeSidebarBtn.addEventListener('click', () => sidebar.classList.add('collapsed'));
    openWaterfallBtn.addEventListener('click', () => sidebar.classList.remove('collapsed'));

    // Fetch Status API
    fetchStatus();
    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                statusProvider.textContent = data.provider;
                statusModel.textContent = data.model;
                statusServer.textContent = data.server_name;
            }
        } catch (e) {
            console.log('Status API Offline, using default status.');
        }
    }

    // Clear Chat
    clearChatBtn.addEventListener('click', () => {
        messagesContainer.innerHTML = `
            <div class="welcome-card">
                <div class="welcome-icon"><i class="fa-solid fa-paper-plane"></i></div>
                <h3>Phiên trò chuyện mới đã bắt đầu!</h3>
                <p>Chọn 1 trong 5 Test Cases hoặc nhập câu hỏi bên dưới để xem Agent suy luận và gọi Tool.</p>
            </div>
        `;
        traceTree.innerHTML = '<div class="empty-trace">Chưa có phiên tương tác nào...</div>';
        traceHistory = [];
    });

    // Preset Chips Handler
    presetChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (!chip || isProcessing) return;
        const prompt = chip.getAttribute('data-prompt');
        userInput.value = prompt;
        sendMessage();
    });

    // Send Message on Enter
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', () => sendMessage());

    async function sendMessage() {
        const prompt = userInput.value.trim();
        if (!prompt || isProcessing) return;

        // Clear welcome card on first message
        const welcomeCard = messagesContainer.querySelector('.welcome-card');
        if (welcomeCard) welcomeCard.remove();

        // Render User Message Bubble
        appendUserMessage(prompt);
        userInput.value = '';
        isProcessing = true;
        sendBtn.disabled = true;

        // Create Agent Message Wrapper
        const agentWrapper = createAgentMessageWrapper();
        const stepsContainer = agentWrapper.querySelector('.react-steps');
        const bubble = agentWrapper.querySelector('.message-bubble');

        try {
            const response = await fetch('/api/chat-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, mode: currentMode })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.trim()) continue;

                    let eventType = 'message';
                    let eventData = '';

                    const lineParts = line.split('\n');
                    for (const part of lineParts) {
                        if (part.startsWith('event:')) {
                            eventType = part.replace('event:', '').trim();
                        } else if (part.startsWith('data:')) {
                            eventData = part.replace('data:', '').trim();
                        }
                    }

                    if (eventData) {
                        try {
                            const payload = JSON.parse(eventData);
                            handleStreamEvent(eventType, payload, stepsContainer, bubble);
                        } catch (err) {
                            console.error('JSON Parse Error:', err);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Stream Fetch Error:', error);
            bubble.innerHTML = `<div class="alert-box"><i class="fa-solid fa-triangle-exclamation"></i> Không thể kết nối Web Server. Vui lòng kiểm tra lại server.</div>`;
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
        }
    }

    function appendUserMessage(text) {
        const item = document.createElement('div');
        item.className = 'message-item user';
        item.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-content-wrapper">
                <div class="message-bubble">${escapeHtml(text)}</div>
            </div>
        `;
        messagesContainer.appendChild(item);
        scrollToBottom();
    }

    function createAgentMessageWrapper() {
        const item = document.createElement('div');
        item.className = 'message-item agent';
        item.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-compass"></i></div>
            <div class="message-content-wrapper">
                <div class="react-steps"></div>
                <div class="message-bubble typing-cursor">Đang kết nối ReAct Engine...</div>
            </div>
        `;
        messagesContainer.appendChild(item);
        scrollToBottom();
        return item;
    }

    function handleStreamEvent(event, data, stepsContainer, bubble) {
        if (event === 'step') {
            const stepType = data.type;

            if (stepType === 'thought') {
                const card = document.createElement('div');
                card.className = 'step-card thought';
                card.innerHTML = `
                    <div class="step-header thought">
                        <i class="fa-solid fa-brain"></i> Thought (Suy luận Step ${data.step || 1})
                        ${data.latency_ms ? `<span class="trace-time">${data.latency_ms}ms</span>` : ''}
                    </div>
                    <div class="step-body">${escapeHtml(data.content)}</div>
                `;
                stepsContainer.appendChild(card);
                updateTraceTree('Thought', data.content, data.latency_ms);
            }
            else if (stepType === 'action') {
                const card = document.createElement('div');
                card.className = 'step-card action';
                card.innerHTML = `
                    <div class="step-header action">
                        <i class="fa-solid fa-gears"></i> Action Proposed: ${data.tool_name}
                    </div>
                    <div class="code-block">${data.tool_name}(${JSON.stringify(data.arguments)})</div>
                `;
                stepsContainer.appendChild(card);
                updateTraceTree('Action', `${data.tool_name}(${JSON.stringify(data.arguments)})`, data.latency_ms);
            }
            else if (stepType === 'observation') {
                const card = document.createElement('div');
                card.className = 'step-card observation';
                const obsStr = JSON.stringify(data.observation, null, 2);
                card.innerHTML = `
                    <div class="step-header observation">
                        <i class="fa-solid fa-eye"></i> Observation từ MCP Server
                    </div>
                    <div class="code-block">${escapeHtml(obsStr)}</div>
                `;
                stepsContainer.appendChild(card);
                updateTraceTree('Observation', `Status: ${data.observation?.status}`, null);
            }
            else if (stepType === 'final_answer') {
                bubble.classList.remove('typing-cursor');
                renderFormattedFinalAnswer(data.content, data.raw_data, bubble);
            }
        }
        else if (event === 'done') {
            bubble.classList.remove('typing-cursor');
        }
        scrollToBottom();
    }

    // STREAMING TOKEN EFFECT & RICH CARD FORMATTER
    function renderFormattedFinalAnswer(content, rawData, bubbleElement) {
        bubbleElement.innerHTML = '';
        
        // Formatted Rich Cards logic
        if (rawData && rawData.status === 'SUCCESS' && Array.isArray(rawData.data)) {
            // Homestay / Accommodations Cards
            const title = document.createElement('div');
            title.style.fontWeight = 'bold';
            title.style.marginBottom = '8px';
            title.innerHTML = `<i class="fa-solid fa-hotel"></i> Danh sách gợi ý nơi lưu trú tại ${rawData.location}:`;
            bubbleElement.appendChild(title);

            const grid = document.createElement('div');
            grid.className = 'card-grid';
            rawData.data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'hotel-card';
                card.innerHTML = `
                    <div class="hotel-name"><i class="fa-solid fa-house-chimney"></i> ${escapeHtml(item.name)}</div>
                    <div class="hotel-price"><i class="fa-solid fa-tag"></i> ${item.price_per_night.toLocaleString('vi-VN')} VNĐ / đêm</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(item.address)}</div>
                    <div style="font-size: 0.8rem; color: var(--text-main); margin-top: 4px;">${escapeHtml(item.features)}</div>
                    <div class="hotel-rating"><i class="fa-solid fa-star"></i> ${item.rating} / 5.0 (Đánh giá tuyệt vời)</div>
                `;
                grid.appendChild(card);
            });
            bubbleElement.appendChild(grid);
            return;
        }

        if (rawData && rawData.status === 'NOT_FOUND') {
            bubbleElement.innerHTML = `
                <div class="alert-box">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <div>
                        <strong>${escapeHtml(rawData.message || 'Không tìm thấy dữ liệu')}</strong>
                        <div style="font-size: 0.8rem; margin-top: 4px; color: var(--text-muted);">
                            💡 Lời khuyên an toàn: Bạn hãy kiểm tra lại chính xác tên địa điểm du lịch và tham khảo từ các nguồn uy tín trước khi khởi hành.
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        // Streaming Typing Animation for Text/Itinerary
        streamTextTokenByToken(content, bubbleElement);
    }

    function streamTextTokenByToken(text, container) {
        container.innerHTML = '';
        const formattedText = escapeHtml(text).replace(/\n/g, '<br>');
        let i = 0;
        const speed = 12; // ms per token char

        function type() {
            if (i < formattedText.length) {
                if (formattedText.substr(i, 4) === '<br>') {
                    container.innerHTML += '<br>';
                    i += 4;
                } else {
                    container.innerHTML += formattedText.charAt(i);
                    i++;
                }
                scrollToBottom();
                setTimeout(type, speed);
            }
        }
        type();
    }

    function updateTraceTree(type, detail, latency) {
        if (traceTree.querySelector('.empty-trace')) {
            traceTree.innerHTML = '';
        }
        const item = document.createElement('div');
        item.className = `trace-item ${type.toLowerCase()}`;
        item.innerHTML = `
            <div><strong>${type}</strong> ${latency ? `<span class="trace-time">${latency}ms</span>` : ''}</div>
            <div style="color: var(--text-muted); font-size: 0.7rem;">${escapeHtml(detail.substring(0, 70))}...</div>
        `;
        traceTree.prepend(item);
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
