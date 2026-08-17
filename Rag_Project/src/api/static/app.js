document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const uploadDropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const documentList = document.getElementById('documentList');
    const btnIngest = document.getElementById('btnIngest');
    const dbStatus = document.getElementById('dbStatus');
    const statusText = document.getElementById('statusText');
    const chatMessages = document.getElementById('chatMessages');
    const btnClearChat = document.getElementById('btnClearChat');
    const inputForm = document.getElementById('inputForm');
    const queryInput = document.getElementById('queryInput');
    const btnSend = document.getElementById('btnSend');

    // Load initial documents list
    fetchDocuments();

    // CLEAR CHAT
    btnClearChat.addEventListener('click', () => {
        chatMessages.innerHTML = `
            <div class="message system-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <h3>Chat Cleared</h3>
                    <p>Ask me any questions about your uploaded documents.</p>
                </div>
            </div>
        `;
    });

    // DRAG AND DROP
    uploadDropzone.addEventListener('click', () => fileInput.click());
    
    uploadDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadDropzone.classList.add('drag-over');
    });

    uploadDropzone.addEventListener('dragleave', () => {
        uploadDropzone.classList.remove('drag-over');
    });

    uploadDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadDropzone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFileUploads(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUploads(fileInput.files);
        }
    });

    // UPLOAD FUNCTION
    async function handleFileUploads(files) {
        uploadProgress.style.display = 'block';
        progressFill.style.width = '0%';
        
        let successCount = 0;
        const total = files.length;
        
        for (let i = 0; i < total; i++) {
            const file = files[i];
            if (file.type !== 'application/pdf') {
                alert(`File ${file.name} is not a PDF.`);
                continue;
            }
            
            progressText.innerText = `Uploading ${file.name}...`;
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    successCount++;
                } else {
                    const error = await response.json();
                    alert(`Failed to upload ${file.name}: ${error.detail || 'Unknown error'}`);
                }
            } catch (err) {
                console.error(err);
                alert(`Network error uploading ${file.name}`);
            }
            
            const percent = Math.round(((i + 1) / total) * 100);
            progressFill.style.width = `${percent}%`;
        }
        
        progressText.innerText = `Completed uploading ${successCount}/${total} files.`;
        setTimeout(() => {
            uploadProgress.style.display = 'none';
        }, 3000);
        
        fetchDocuments();
    }

    // FETCH DOCUMENTS LIST
    async function fetchDocuments() {
        try {
            const response = await fetch('/documents');
            if (response.ok) {
                const data = await response.json();
                renderDocumentList(data.documents);
            }
        } catch (err) {
            console.error('Error fetching documents list:', err);
        }
    }

    function renderDocumentList(documents) {
        documentList.innerHTML = '';
        if (documents.length === 0) {
            documentList.innerHTML = '<li class="empty-list">No PDFs found</li>';
            return;
        }
        
        documents.forEach(doc => {
            const li = document.createElement('li');
            li.className = 'document-item';
            li.innerHTML = `
                <span class="doc-name" title="${doc}">${doc}</span>
                <button class="doc-remove" data-name="${doc}">✕</button>
            `;
            
            li.querySelector('.doc-remove').addEventListener('click', async (e) => {
                e.stopPropagation();
                const docName = e.target.getAttribute('data-name');
                if (confirm(`Remove ${docName}?`)) {
                    await deleteDocument(docName);
                }
            });
            
            documentList.appendChild(li);
        });
    }

    // DELETE DOCUMENT
    async function deleteDocument(docName) {
        try {
            const response = await fetch(`/documents/${encodeURIComponent(docName)}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                fetchDocuments();
            } else {
                const error = await response.json();
                alert(`Failed to delete: ${error.detail}`);
            }
        } catch (err) {
            console.error(err);
        }
    }

    // INGEST & REBUILD DATABASE
    btnIngest.addEventListener('click', async () => {
        setSystemStatus('busy', 'Ingesting documents...');
        btnIngest.disabled = true;
        
        try {
            const response = await fetch('/ingest', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok) {
                alert(`Ingestion succeeded! Database reindexed.`);
                setSystemStatus('healthy', 'System Ready');
            } else {
                alert(`Ingestion failed: ${data.detail}`);
                setSystemStatus('healthy', 'System Ready');
            }
        } catch (err) {
            console.error(err);
            alert('Error running ingestion pipeline.');
            setSystemStatus('healthy', 'System Ready');
        } finally {
            btnIngest.disabled = false;
        }
    });

    function setSystemStatus(status, text) {
        statusText.innerText = text;
        const dot = dbStatus.querySelector('.status-dot');
        dot.className = 'status-dot';
        if (status === 'healthy') {
            dot.classList.add('status-healthy');
        } else if (status === 'busy') {
            dot.classList.add('status-dot', 'status-busy');
        }
    }

    // SUBMIT QUERY
    inputForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;
        
        // Append user message
        appendMessage('user', query);
        queryInput.value = '';
        
        // Append loading assistant message
        const loadingId = appendMessage('assistant', 'Thinking...', true);
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                updateAssistantMessage(loadingId, data.answer, data.sources);
            } else {
                updateAssistantMessage(loadingId, `Error: ${data.detail || 'Failed to generate answer.'}`);
            }
        } catch (err) {
            console.error(err);
            updateAssistantMessage(loadingId, 'Network error communicating with the RAG server.');
        }
    });

    function appendMessage(sender, text, isLoading = false) {
        const id = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        messageDiv.id = id;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(text)}</div>
            </div>
        `;
        
        if (isLoading) {
            messageDiv.querySelector('.message-text').classList.add('loading-pulse');
        }
        
        chatMessages.appendChild(messageDiv);
        scrollChatToBottom();
        return id;
    }

    function updateAssistantMessage(id, answer, sources = []) {
        const messageDiv = document.getElementById(id);
        if (!messageDiv) return;
        
        const contentDiv = messageDiv.querySelector('.message-content');
        
        // Remove loading state
        const textDiv = contentDiv.querySelector('.message-text');
        textDiv.classList.remove('loading-pulse');
        // Render response formatting (linebreaks)
        textDiv.innerHTML = formatMarkdownLikeText(answer);
        
        // If there are sources, render citations list
        if (sources && sources.length > 0) {
            const citationsContainer = document.createElement('div');
            citationsContainer.className = 'citations-container';
            citationsContainer.innerHTML = `<div class="citations-title">Sources Cited:</div>`;
            
            const citationsList = document.createElement('div');
            citationsList.className = 'citations-list';
            
            sources.forEach(src => {
                const badge = document.createElement('span');
                badge.className = 'citation-badge';
                badge.innerHTML = `📄 ${src.file} — Page ${src.page}`;
                citationsList.appendChild(badge);
            });
            
            citationsContainer.appendChild(citationsList);
            contentDiv.appendChild(citationsContainer);
        }
        
        scrollChatToBottom();
    }

    function scrollChatToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.innerText = text;
        return div.innerHTML;
    }

    function formatMarkdownLikeText(text) {
        // Simple formatter for newlines and basic formatting
        let formatted = escapeHtml(text);
        
        // Bold tags replacement: **bold**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert single asterisks to italic: *italic*
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert backticks to code formatting: `code`
        formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Convert list bullets
        formatted = formatted.replace(/^\s*-\s+(.*?)$/gm, '• $1');
        
        // Convert newlines to breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
});
