// --- CHAT LOGIC ---
async function loadChatHistory() {
    const container = document.getElementById('chat-history-list');
    container.innerHTML = '<div class="text-center text-xs text-gray-500">Loading...</div>';
    try {
        const res = await authenticatedFetch('/Chats/');
        if (!res.ok) throw new Error('Failed to load chats');
        const chats = await res.json();
        container.innerHTML = '';
        
        if (chats.length === 0) {
            container.innerHTML = '<div class="text-center text-xs text-gray-500 py-2">No history</div>';
            return;
        }
        chats.forEach(chat => {
            const item = document.createElement('a');
            item.href = "#";
            item.onclick = (e) => { e.preventDefault(); loadConversation(chat.id, chat.title, chat.AiMode); };
            item.className = "block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white truncate transition";
            item.innerHTML = `<i class="far fa-comments mr-2 text-gray-500"></i> ${chat.title}`;
            container.appendChild(item);
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="text-center text-xs text-red-400">Error loading history</div>';
    }
}
async function createNewChat() {
    const title = prompt("Name your new session:", "New Therapy Session");
    if (!title) return;
    try {
        const res = await authenticatedFetch('/Chats/', {
            method: 'POST',
            body: JSON.stringify({ title: title, AiMode: 'therapy' }) // Default mode
        });
        if (res.ok) {
            loadChatHistory();
            const newChat = await res.json();
            loadConversation(newChat.id, newChat.title, newChat.AiMode);
        }
    } catch (err) {
        showToast("Could not create chat");
    }
}
async function loadConversation(homepageId, title, mode) {
    currentChatId = homepageId;
    document.getElementById('active-chat-title').textContent = title;
    document.getElementById('active-chat-mode').textContent = mode + " mode";
    document.getElementById('active-chat-mode').classList.remove('hidden');
    
    // Enable inputs
    document.getElementById('user-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    document.getElementById('ai-mode-select').value = mode;
    const msgContainer = document.getElementById('messages-container');
    msgContainer.innerHTML = '<div class="flex justify-center mt-10"><div class="loader"></div></div>';
    try {
        // To get messages, we likely need to query ChatData. 
        // Based on backend, ChatData is the model with 'content'.
        // Ideally, backend should support filtering ChatData by homepageId, 
        // but ChatViewSet returns ALL chats for user. 
        // We will fetch all and find the matching one. (Not efficient for prod, but fits current backend)
        
        const res = await authenticatedFetch('/ChatData/');
        const chatDataList = await res.json();
        
        // Find the specific chat entry linked to this homepageId
        // NOTE: Backend 'ChatSerializer' returns 'chat' field which is the ID of UserHomepageDB
        const activeChatData = chatDataList.find(c => c.chat === homepageId);
        
        msgContainer.innerHTML = ''; // Clear loader
        if (activeChatData && activeChatData.content && Array.isArray(activeChatData.content)) {
            activeChatData.content.forEach(msg => renderMessage(msg));
        } else {
            renderSystemMessage("Start the conversation by typing below.");
        }
        
        scrollToBottom();
    } catch (err) {
        msgContainer.innerHTML = '<div class="text-center text-red-500">Failed to load messages</div>';
    }
}
function renderMessage(msg) {
    const container = document.getElementById('messages-container');
    const div = document.createElement('div');
    const isUser = msg.role === 'user';
    
    div.className = `flex ${isUser ? 'justify-end' : 'justify-start'}`;
    
    div.innerHTML = `
        <div class="${isUser ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200 text-gray-800'} max-w-lg rounded-lg px-4 py-2 shadow-sm text-sm">
            ${msg.content}
        </div>
    `;
    container.appendChild(div);
}
function renderSystemMessage(text) {
    const container = document.getElementById('messages-container');
    container.innerHTML += `<div class="text-center text-xs text-gray-400 my-4">${text}</div>`;
}
function scrollToBottom() {
    const container = document.getElementById('messages-container');
    container.scrollTop = container.scrollHeight;
}
// Handle Sending Message
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('user-input');
    const mode = document.getElementById('ai-mode-select').value;
    const text = input.value.trim();
    if (!text || !currentChatId) return;
    // Optimistic UI Update
    renderMessage({ role: 'user', content: text });
    input.value = '';
    scrollToBottom();
    // Add loading indicator
    const container = document.getElementById('messages-container');
    const loaderId = 'temp-loader-' + Date.now();
    container.insertAdjacentHTML('beforeend', `
        <div id="${loaderId}" class="flex justify-start">
            <div class="bg-gray-100 rounded-lg px-4 py-2 text-gray-500 text-sm italic">
                Typing...
            </div>
        </div>
    `);
    scrollToBottom();
    try {
        // Hitting the 'continue_chat' action
        const res = await authenticatedFetch('/ChatData/continue_chat/', {
            method: 'POST',
            body: JSON.stringify({
                prompt: text,
                mode: mode,
                ChatID: currentChatId // Passing the HomepageDB UUID
            })
        });
        document.getElementById(loaderId).remove();
        if (!res.ok) throw new Error('AI Error');
        
        const data = await res.json();
        renderMessage({ role: 'ai', content: data.response });
        scrollToBottom();
    } catch (err) {
        document.getElementById(loaderId)?.remove();
        showToast("Failed to get response");
    }
});
