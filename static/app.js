// The Lenny Growth Assistant - Frontend Client Application
let currentSessionId = null;
let activeArtifact = null;
let activeTab = 'preview';

document.addEventListener('DOMContentLoaded', async () => {
  initElements();
  bindEvents();
  await loadModelConfig();
  await loadSessions();
});

function initElements() {
  window.ui = {
    providerSelect: document.getElementById('providerSelect'),
    modelStatusText: document.getElementById('modelStatusText'),
    btnNewChat: document.getElementById('btnNewChat'),
    sessionsList: document.getElementById('sessionsList'),
    messagesContainer: document.getElementById('messagesContainer'),
    welcomeCard: document.getElementById('welcomeCard'),
    chatForm: document.getElementById('chatForm'),
    chatInput: document.getElementById('chatInput'),
    activeChatTitle: document.getElementById('activeChatTitle'),
    // Artifact Viewer
    artifactPane: document.getElementById('artifactPane'),
    artifactTitle: document.getElementById('artifactTitle'),
    artifactTypeBadge: document.getElementById('artifactTypeBadge'),
    artifactIframe: document.getElementById('artifactIframe'),
    artifactMarkdownView: document.getElementById('artifactMarkdownView'),
    artifactRawCode: document.getElementById('artifactRawCode'),
    artifactViewPreview: document.getElementById('artifactViewPreview'),
    artifactViewCode: document.getElementById('artifactViewCode'),
    tabPreview: document.getElementById('tabPreview'),
    tabCode: document.getElementById('tabCode'),
    btnCopyArtifact: document.getElementById('btnCopyArtifact'),
    btnCloseArtifact: document.getElementById('btnCloseArtifact'),
    btnToggleArtifacts: document.getElementById('btnToggleArtifacts')
  };

  // Initially hide artifact pane until an artifact is generated or opened
  ui.artifactPane.classList.add('closed');
}

function bindEvents() {
  // Model Selector
  ui.providerSelect.addEventListener('change', async (e) => {
    const provider = e.target.value;
    try {
      const res = await fetch('/api/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider })
      });
      const data = await res.json();
      ui.modelStatusText.textContent = `${data.provider.toUpperCase()} (${data.model_name})`;
    } catch (err) {
      console.error('Failed to change model:', err);
    }
  });

  // New Chat
  ui.btnNewChat.addEventListener('click', startNewChat);

  // Chat Form Submission
  ui.chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleUserSubmit();
  });

  // Textarea auto-resize & Enter to send
  ui.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleUserSubmit();
    }
  });

  // Prompt chips
  document.querySelectorAll('.prompt-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const prompt = btn.getAttribute('data-prompt');
      ui.chatInput.value = prompt;
      ui.chatInput.focus();
      handleUserSubmit();
    });
  });

  // Artifact Viewer Tabs
  ui.tabPreview.addEventListener('click', () => setArtifactTab('preview'));
  ui.tabCode.addEventListener('click', () => setArtifactTab('code'));

  // Close Artifact Viewer
  ui.btnCloseArtifact.addEventListener('click', () => {
    ui.artifactPane.classList.add('closed');
  });

  // Toggle Artifact Viewer
  ui.btnToggleArtifacts.addEventListener('click', () => {
    ui.artifactPane.classList.toggle('closed');
  });

  // Copy Artifact Code
  ui.btnCopyArtifact.addEventListener('click', () => {
    if (activeArtifact) {
      navigator.clipboard.writeText(activeArtifact.content);
      ui.btnCopyArtifact.textContent = '✓';
      setTimeout(() => ui.btnCopyArtifact.textContent = '📋', 1500);
    }
  });
}

async function loadModelConfig() {
  try {
    const res = await fetch('/api/models');
    if (res.ok) {
      const data = await res.json();
      ui.providerSelect.value = data.provider;
      ui.modelStatusText.textContent = `${data.provider.toUpperCase()} (${data.model_name})`;
    }
  } catch (err) {
    console.error('Failed to load model config:', err);
  }
}

async function loadSessions() {
  try {
    const res = await fetch('/api/sessions');
    if (res.ok) {
      const sessions = await res.json();
      renderSessionsList(sessions);
    }
  } catch (err) {
    console.error('Failed to load sessions:', err);
  }
}

function renderSessionsList(sessions) {
  ui.sessionsList.innerHTML = '';
  if (!sessions || sessions.length === 0) {
    ui.sessionsList.innerHTML = '<div style="font-size:12px;color:var(--text-dim);padding:8px;">No previous sessions</div>';
    return;
  }

  sessions.forEach(s => {
    const div = document.createElement('div');
    div.className = `session-item ${s.id === currentSessionId ? 'active' : ''}`;
    div.innerHTML = `
      <span class="session-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</span>
      <button class="session-del-btn" title="Delete conversation">&times;</button>
    `;

    div.querySelector('.session-title').addEventListener('click', () => selectSession(s.id));
    div.querySelector('.session-del-btn').addEventListener('click', async (e) => {
      e.stopPropagation();
      await deleteSession(s.id);
    });

    ui.sessionsList.appendChild(div);
  });
}

async function startNewChat() {
  currentSessionId = null;
  ui.messagesContainer.innerHTML = '';
  ui.messagesContainer.appendChild(ui.welcomeCard);
  ui.activeChatTitle.textContent = 'The Lenny Growth Assistant';
  ui.chatInput.value = '';
  ui.artifactPane.classList.add('closed');
  activeArtifact = null;
  await loadSessions();
}

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  ui.welcomeCard.remove();
  ui.messagesContainer.innerHTML = '';

  try {
    const res = await fetch(`/api/sessions/${sessionId}`);
    if (res.ok) {
      const data = await res.json();
      ui.activeChatTitle.textContent = data.session.title;
      data.messages.forEach(msg => {
        appendMessageBubble(msg.role, msg.content, msg.citations, msg.artifacts);
      });
      await loadSessions();
      scrollToBottom();
    }
  } catch (err) {
    console.error('Failed to load session details:', err);
  }
}

async function deleteSession(sessionId) {
  try {
    await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
    if (currentSessionId === sessionId) {
      startNewChat();
    } else {
      loadSessions();
    }
  } catch (err) {
    console.error('Failed to delete session:', err);
  }
}

async function handleUserSubmit() {
  const query = ui.chatInput.value.trim();
  if (!query) return;

  ui.chatInput.value = '';
  ui.chatInput.style.height = 'auto';

  // Remove welcome card if visible
  if (ui.welcomeCard.parentNode) {
    ui.welcomeCard.remove();
  }

  // Append User message to UI
  appendMessageBubble('user', query);
  scrollToBottom();

  // Show loading indicator
  const loadingId = 'loading-' + Date.now();
  appendLoadingBubble(loadingId);
  scrollToBottom();

  try {
    const provider = ui.providerSelect.value;
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentSessionId,
        query: query,
        provider: provider
      })
    });

    removeLoadingBubble(loadingId);

    if (res.ok) {
      const data = await res.json();
      currentSessionId = data.session_id;

      appendMessageBubble('assistant', data.answer, data.citations, data.artifacts);

      // If an artifact was generated, open the Artifact Viewer automatically!
      if (data.artifacts && data.artifacts.length > 0) {
        openArtifact(data.artifacts[0]);
      }

      await loadSessions();
      scrollToBottom();
    } else {
      const err = await res.json();
      appendMessageBubble('assistant', `⚠️ **Error:** ${err.detail || 'Failed to generate response.'}`);
    }
  } catch (err) {
    removeLoadingBubble(loadingId);
    appendMessageBubble('assistant', `⚠️ **Network / Connection Error:** ${err.message}`);
  }
}

function appendMessageBubble(role, content, citations = [], artifacts = []) {
  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';

  const header = document.createElement('div');
  header.className = 'bubble-header';
  header.innerHTML = `
    <span>${role === 'user' ? '👤 You' : '🎙️ Lenny Growth Assistant'}</span>
    <span>${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
  `;
  bubble.appendChild(header);

  // Markdown Render
  const contentDiv = document.createElement('div');
  contentDiv.className = 'bubble-content';
  
  // Clean raw XML artifact tags from chat stream text for clean viewing
  const cleanedText = content.replace(/<artifact[\s\S]*?<\/artifact>/gi, '');
  contentDiv.innerHTML = window.marked ? window.marked.parse(cleanedText) : escapeHtml(cleanedText);
  bubble.appendChild(contentDiv);

  // Render Artifact Callout Cards if present
  if (artifacts && artifacts.length > 0) {
    artifacts.forEach(art => {
      const artCard = document.createElement('div');
      artCard.className = 'artifact-callout-card';
      artCard.innerHTML = `
        <div class="artifact-callout-info">
          <h4>📑 ${escapeHtml(art.title)}</h4>
          <p>Click to open interactive ${art.type.toUpperCase()} artifact in side viewer</p>
        </div>
        <button class="btn-open-artifact">View Artifact ↗</button>
      `;
      artCard.addEventListener('click', () => openArtifact(art));
      bubble.appendChild(artCard);
    });
  }

  // Render Citations
  if (citations && citations.length > 0) {
    const citBox = document.createElement('div');
    citBox.className = 'citations-box';
    citBox.innerHTML = `
      <div class="citations-title">
        <span>📚 Grounded Transcript Citations (${citations.length})</span>
      </div>
      <div class="citations-grid">
        ${citations.map(c => `
          <div class="citation-card">
            <div class="citation-meta">
              <span class="citation-guest">[${c.source_index}] ${escapeHtml(c.guest)} (${escapeHtml(c.title)})</span>
              <span class="citation-ts">${escapeHtml(c.timestamp || '')}</span>
            </div>
            <div class="citation-snippet">"${escapeHtml(c.snippet)}"</div>
          </div>
        `).join('')}
      </div>
    `;
    bubble.appendChild(citBox);
  }

  row.appendChild(bubble);
  ui.messagesContainer.appendChild(row);
}

function appendLoadingBubble(id) {
  const row = document.createElement('div');
  row.className = 'message-row assistant';
  row.id = id;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.innerHTML = `
    <div class="loading-indicator">
      <div class="spinner"></div>
      <span>Searching Lenny's Podcast transcripts & reasoning...</span>
    </div>
  `;
  row.appendChild(bubble);
  ui.messagesContainer.appendChild(row);
}

function removeLoadingBubble(id) {
  const elem = document.getElementById(id);
  if (elem) elem.remove();
}

function openArtifact(artifact) {
  activeArtifact = artifact;
  ui.artifactTitle.textContent = artifact.title;
  ui.artifactTypeBadge.textContent = `${artifact.type.toUpperCase()} ARTIFACT`;
  ui.artifactRawCode.textContent = artifact.content;

  if (artifact.type === 'html') {
    ui.artifactIframe.classList.remove('hidden');
    ui.artifactMarkdownView.classList.add('hidden');

    // Secure Sandboxed Injection
    // Uses isolated iframe with safe styling boilerplate
    const doc = ui.artifactIframe.contentDocument || ui.artifactIframe.contentWindow.document;
    doc.open();
    doc.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 24px; color: #1f2937; line-height: 1.6; }
        </style>
      </head>
      <body>
        ${artifact.content}
      </body>
      </html>
    `);
    doc.close();
  } else {
    // Markdown preview
    ui.artifactIframe.classList.add('hidden');
    ui.artifactMarkdownView.classList.remove('hidden');
    ui.artifactMarkdownView.innerHTML = window.marked ? window.marked.parse(artifact.content) : escapeHtml(artifact.content);
  }

  setArtifactTab('preview');
  ui.artifactPane.classList.remove('closed');
}

function setArtifactTab(tab) {
  activeTab = tab;
  if (tab === 'preview') {
    ui.tabPreview.classList.add('active');
    ui.tabCode.classList.remove('active');
    ui.artifactViewPreview.classList.remove('hidden');
    ui.artifactViewCode.classList.add('hidden');
  } else {
    ui.tabPreview.classList.remove('active');
    ui.tabCode.classList.add('active');
    ui.artifactViewPreview.classList.add('hidden');
    ui.artifactViewCode.classList.remove('hidden');
  }
}

function scrollToBottom() {
  ui.messagesContainer.scrollTop = ui.messagesContainer.scrollHeight;
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
