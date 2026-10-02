// AgentZ Web Client Engine (AI Agent Edition)
const ICONS = {
  sparkle: `<svg class="icon icon-sparkle" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C12 7.523 7.523 12 2 12C7.523 12 12 16.477 12 22C12 16.477 16.477 12 22 12C16.477 12 12 7.523 12 2Z"/></svg>`,
  sparkleSm: `<svg class="icon icon-sparkle-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C12 7.523 7.523 12 2 12C7.523 12 12 16.477 12 22C12 16.477 16.477 12 22 12C16.477 12 12 7.523 12 2Z"/></svg>`,
  plus: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
  laptop: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"></rect><line x1="2" y1="20" x2="22" y2="20"></line></svg>`,
  phone: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>`,
  auto: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.4 4.8 5.2.8-3.8 3.7.9 5.2L12 14l-4.7 2.5.9-5.2-3.8-3.7 5.2-.8L12 2z"/></svg>`,
  battery: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="7" width="16" height="10" rx="2"></rect><line x1="22" y1="11" x2="22" y2="13"></line></svg>`,
  bolt: `<svg class="icon icon-bolt" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
  cpu: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>`,
  ram: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 7h20v10H2z"></path><path d="M6 17v2m4-2v2m4-2v2m4-2v2M6 7V5m4 2V5m4 2V5m4 2V5"></path></svg>`,
  screen: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>`,
  shield: `<svg class="icon icon-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`,
  browser: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`,
  youtube: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="4"></rect><polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon></svg>`,
  eye: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
  cursor: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m3 3 7.07 16.97 2.51-7.39 7.39-2.51L3 3z"></path></svg>`,
  edit: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`,
  gauge: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"></path><path d="M12 6v6l4 2"></path></svg>`,
  car: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9L16.4 9H7.6L3.5 11.1C2.7 11.3 2 12.1 2 13v3c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><path d="M9 17h6"></path><circle cx="17" cy="17" r="2"></circle></svg>`,
  camera: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>`,
  speaker: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`,
  speakerMuted: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>`,
  mic: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`,
  send: `<svg class="icon icon-send" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>`,
  stop: `<svg class="icon icon-stop" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"></rect></svg>`,
  close: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
  check: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  checkCircle: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 9 11 14 8 11"></polyline></svg>`,
  alert: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
  error: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
  spinner: `<svg class="icon spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10"></path></svg>`,
  pending: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="6"></circle></svg>`,
  chat: `<svg class="icon icon-history" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
  zoom: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>`
};

let conversationId = "conv_" + Math.random().toString(36).substring(2, 9);
let currentTaskId = null;
let currentDevice = "LAPTOP";
let isRunning = false;
let executionAborted = false;
let ttsEnabled = false;

// Voice & Microphone Engine State
let voiceModeActive = false;
let isAwakened = false;
let isSpeaking = false;
let recognition = null;
let isRecognitionRunning = false;
let audioContext = null;

document.addEventListener("DOMContentLoaded", () => {
    initUI();
    fetchDevices();
    fetchTelemetry();
    fetchWebKnowledgeStats();
    setInterval(fetchTelemetry, 3500);
});

function initUI() {
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const stopBtn = document.getElementById("stop-btn");
    const voiceBtn = document.getElementById("voice-btn");
    const newChatBtn = document.getElementById("new-chat-btn");
    const themeToggle = document.getElementById("theme-toggle");

    // Enforce Light Theme
    document.body.setAttribute("data-theme", "light");

    // Auto-resize input
    input.addEventListener("input", () => {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 140) + "px";
    });

    // Enter to submit
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    sendBtn.addEventListener("click", handleSend);
    stopBtn.addEventListener("click", handleStop);
    newChatBtn.addEventListener("click", handleNewChat);

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            themeToggle.title = "AgentZ Theme Active";
        });
    }

    // Device picker
    document.querySelectorAll(".device-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            document.querySelectorAll(".device-chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            currentDevice = chip.getAttribute("data-device");
            const badge = document.getElementById("target-badge");
            if (badge) {
                badge.textContent = `Target: ${chip.getAttribute("data-name")}`;
            }
        });
    });

    // Initialize Voice & Microphone Engine
    initVoiceEngine();

    // Voice mode header pill toggle
    const voiceModeBtn = document.getElementById("voice-mode-btn");
    if (voiceModeBtn) {
        voiceModeBtn.addEventListener("click", () => {
            if (voiceModeActive) {
                stopVoiceMode();
            } else {
                startVoiceMode(true);
            }
        });
    }

    // Voice bar close button
    const voiceBarClose = document.getElementById("voice-bar-close-btn");
    if (voiceBarClose) {
        voiceBarClose.addEventListener("click", () => {
            stopVoiceMode();
        });
    }

    // TTS voice button toggle
    const ttsBtn = document.getElementById("tts-btn");
    if (ttsBtn) {
        ttsBtn.innerHTML = ICONS.speaker;
        ttsBtn.addEventListener("click", () => {
            ttsEnabled = !ttsEnabled;
            ttsBtn.innerHTML = ttsEnabled ? ICONS.speaker : ICONS.speakerMuted;
            ttsBtn.title = ttsEnabled ? "Voice Output Active (Click to mute)" : "Voice Output Muted (Click to enable)";
            ttsBtn.style.color = ttsEnabled ? "var(--accent-blue)" : "var(--text-secondary)";
            if (ttsEnabled) {
                speakText("Voice output enabled.");
            } else if ("speechSynthesis" in window) {
                window.speechSynthesis.cancel();
            }
        });
    }

    // Telemetry card click -> open diagnostics modal
    const telemCard = document.getElementById("telemetry-card");
    if (telemCard) {
        telemCard.addEventListener("click", async () => {
            try {
                const res = await fetch("/agent/telemetry");
                if (res.ok) {
                    const data = await res.json();
                    openDiagnosticsModal(data);
                }
            } catch (e) {
                console.error("Failed to load diagnostics", e);
            }
        });
    }

    // View screen capture button
    const viewScreenBtn = document.getElementById("view-screen-btn");
    if (viewScreenBtn) {
        viewScreenBtn.addEventListener("click", async () => {
            const originalHTML = viewScreenBtn.innerHTML;
            viewScreenBtn.innerHTML = `${ICONS.camera} <span>Capturing...</span>`;
            try {
                const res = await fetch("/agent/screen/capture");
                if (res.ok) {
                    const data = await res.json();
                    if (data.url) {
                        openImageModal(data.url);
                    }
                }
            } catch (e) {
                console.error("Screen capture failed", e);
            } finally {
                viewScreenBtn.innerHTML = originalHTML;
            }
        });
    }
}

async function fetchDevices() {
    try {
        const res = await fetch("/agent/devices");
        if (res.ok) {
            const data = await res.json();
            console.log("Connected devices:", data);
        }
    } catch (e) {
        console.warn("Device status check failed", e);
    }
}

async function fetchTelemetry() {
    try {
        const res = await fetch("/agent/telemetry");
        if (!res.ok) return;
        const data = await res.json();
        const stats = data.stats || {};

        if (stats.battery) {
            const battEl = document.getElementById("telem-battery");
            const barBatt = document.getElementById("bar-battery");
            const p = stats.battery.percent || 0;
            if (battEl) {
                battEl.innerHTML = `${p}% ${stats.battery.power_plugged ? ICONS.bolt : ""}`;
            }
            if (barBatt) {
                barBatt.style.width = `${Math.min(100, Math.max(0, p))}%`;
            }
        }

        if (stats.cpu_percent !== undefined) {
            const cpuEl = document.getElementById("telem-cpu");
            const barCpu = document.getElementById("bar-cpu");
            const p = stats.cpu_percent || 0;
            if (cpuEl) cpuEl.textContent = `${p}%`;
            if (barCpu) barCpu.style.width = `${Math.min(100, Math.max(0, p))}%`;
        }

        if (stats.ram && stats.ram.percent_used !== undefined) {
            const ramEl = document.getElementById("telem-ram");
            const barRam = document.getElementById("bar-ram");
            const p = stats.ram.percent_used || 0;
            if (ramEl) ramEl.textContent = `${p}%`;
            if (barRam) barRam.style.width = `${Math.min(100, Math.max(0, p))}%`;
        }

        const androidEl = document.getElementById("telem-android");
        if (androidEl) {
            const devs = data.android_devices || [];
            if (devs.length > 0) {
                androidEl.textContent = devs[0].id;
                androidEl.style.color = "var(--risk-low)";
            } else {
                androidEl.textContent = "Standby (No phone)";
                androidEl.style.color = "var(--text-muted)";
            }
        }
    } catch (e) {
        // silent fallback
    }
}

function handleNewChat() {
    conversationId = "conv_" + Math.random().toString(36).substring(2, 9);
    currentTaskId = null;
    isRunning = false;
    executionAborted = false;
    const messages = document.getElementById("messages-container");
    messages.innerHTML = `
      <div class="empty-state" id="empty-state">
        <div class="agent-hero-badge">
          ${ICONS.sparkle}
        </div>
        <h1 class="agent-title">
          <span class="agent-gradient-text">Hello</span>
        </h1>
        <h2 class="agent-subtitle">Where would you like to start?</h2>
        <p class="agent-desc">
          Autonomous cross-device intelligence running natively on your <strong>Laptop</strong> (Windows 11) and <strong>Android Phone</strong>.
        </p>

        <div class="suggestion-grid">
          <div class="suggestion-card" onclick="sendSuggestion('Open YouTube')">
            <div class="card-icon-badge tint-red">${ICONS.youtube}</div>
            <div class="card-text">
              <div class="title">Open YouTube</div>
              <div class="subtitle">Launches and displays YouTube directly in your browser</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Open Chrome and open YouTube')">
            <div class="card-icon-badge tint-blue">${ICONS.browser}</div>
            <div class="card-text">
              <div class="title">Open Chrome & YouTube</div>
              <div class="subtitle">Launches Chrome and opens YouTube directly</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Read my laptop screen')">
            <div class="card-icon-badge tint-purple">${ICONS.eye}</div>
            <div class="card-text">
              <div class="title">Inspect Screen Text (OCR)</div>
              <div class="subtitle">Extracts text and inspects visible application windows</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Move cursor to center of screen')">
            <div class="card-icon-badge tint-teal">${ICONS.cursor}</div>
            <div class="card-text">
              <div class="title">Move Mouse Cursor</div>
              <div class="subtitle">Smoothly moves cursor across screen to exact coordinates</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Open Notepad and type \'AgentZ is executing real work live!\'')">
            <div class="card-icon-badge tint-amber">${ICONS.edit}</div>
            <div class="card-text">
              <div class="title">Automated Typing in Notepad</div>
              <div class="subtitle">Launches app, brings window to focus, and injects keystrokes</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Check laptop battery and CPU stats')">
            <div class="card-icon-badge tint-indigo">${ICONS.gauge}</div>
            <div class="card-text">
              <div class="title">Hardware Telemetry</div>
              <div class="subtitle">Queries live battery level, CPU utilization, and RAM load</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Book me a Rapido from my current location to LPU')">
            <div class="card-icon-badge tint-green">${ICONS.car}</div>
            <div class="card-text">
              <div class="title">Book Rapido Ride</div>
              <div class="subtitle">Autonomous ride execution with mandatory safety confirmation</div>
            </div>
          </div>

          <div class="suggestion-card" onclick="sendSuggestion('Search latest AI news 2026 on Google')">
            <div class="card-icon-badge tint-sky">${ICONS.browser}</div>
            <div class="card-text">
              <div class="title">Search the Web</div>
              <div class="subtitle">Performs autonomous Google searches in your browser</div>
            </div>
          </div>
        </div>
      </div>
    `;
    setExecuting(false);
}

function setExecuting(executing) {
    isRunning = executing;
    const sendBtn = document.getElementById("send-btn");
    const stopBtn = document.getElementById("stop-btn");
    const chatInput = document.getElementById("chat-input");

    if (sendBtn) sendBtn.style.display = executing ? "none" : "flex";
    if (stopBtn) stopBtn.style.display = executing ? "flex" : "none";
    if (chatInput) {
        chatInput.disabled = executing;
        if (!executing) {
            chatInput.focus();
        }
    }
}

function appendUserMessage(text) {
    const container = document.getElementById("messages-container");
    if (!container) return null;

    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `
        <div class="user-bubble">
            ${escapeHtml(text)}
        </div>
    `;
    container.appendChild(row);
    scrollToBottom();
    return row;
}

function appendAgentMessage(text, suggestions = [], type = null, typeLabel = null, spoken = null) {
    const container = document.getElementById("messages-container");
    if (!container) return null;

    const row = document.createElement("div");
    row.className = "message-row agent";

    let badgeHtml = "";
    if (type === "error") {
        badgeHtml = `<div class="status-pill error">${ICONS.error} <span>${escapeHtml(typeLabel || 'Error')}</span></div>`;
    } else if (type === "warning") {
        badgeHtml = `<div class="status-pill warning">${ICONS.alert} <span>${escapeHtml(typeLabel || 'Notice')}</span></div>`;
    } else if (type === "success") {
        badgeHtml = `<div class="status-pill success">${ICONS.checkCircle} <span>${escapeHtml(typeLabel || 'Task Complete')}</span></div>`;
    }

    let suggestionsHtml = "";
    if (suggestions && suggestions.length > 0) {
        suggestionsHtml = `
            <div class="options-container">
                ${suggestions.map(opt => `<button class="option-btn" onclick="sendSuggestion('${escapeHtml(opt)}')">${escapeHtml(opt)}</button>`).join("")}
            </div>
        `;
    }

    row.innerHTML = `
        <div class="agent-avatar">${ICONS.sparkle}</div>
        <div class="agent-bubble">
            ${badgeHtml}
            <div>${formatMarkdown(text)}</div>
            ${suggestionsHtml}
        </div>
    `;

    container.appendChild(row);
    scrollToBottom();

    if (spoken && ttsEnabled) {
        speakText(spoken);
    }

    return row;
}

function appendExecutionCard(steps = []) {
    const container = document.getElementById("messages-container");
    if (!container) return null;

    const card = document.createElement("div");
    card.className = "execution-card";

    let stepsHtml = steps.map((step, idx) => `
        <div class="step-item pending" id="step-item-${idx}">
            <div class="step-icon-wrap" id="step-icon-${idx}">${ICONS.pending}</div>
            <div class="step-details" style="display:flex;flex-direction:column;gap:2px;">
                <span class="step-title" style="font-weight:500;">${escapeHtml(step.title || 'Step ' + (idx + 1))}</span>
                ${step.description ? `<span class="step-desc" style="font-size:11.5px;color:var(--text-muted);">${escapeHtml(step.description)}</span>` : ''}
            </div>
        </div>
    `).join("");

    card.innerHTML = `
        <div class="execution-card-header" id="exec-status-header">
            <div class="header-status-left">
                ${ICONS.spinner}
                <span>Autonomous Execution Pipeline</span>
            </div>
            <span style="font-size:11px;font-weight:500;color:var(--text-muted);">${steps.length} Steps</span>
        </div>
        <div class="step-list">
            ${stepsHtml}
        </div>
    `;

    container.appendChild(card);
    scrollToBottom();
    return card;
}

function sendSuggestion(text) {
    const input = document.getElementById("chat-input");
    input.value = text;
    input.focus();
    handleSend();
}

async function handleSend() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text || isRunning) return;

    // Remove empty state if present
    const emptyState = document.getElementById("empty-state");
    if (emptyState) emptyState.remove();

    appendUserMessage(text);
    input.value = "";
    input.style.height = "auto";

    setExecuting(true);
    executionAborted = false;

    try {
        const planRes = await fetch("/agent/plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: conversationId,
                user_message: text,
                device_target: currentDevice,
                is_voice: voiceModeActive
            })
        });

        if (!planRes.ok) throw new Error("Plan generation failed");
        const plan = await planRes.json();
        currentTaskId = plan.task_id;

        // If asking missing information
        if (plan.status === "COLLECTING_INFORMATION" && plan.question_to_user) {
            appendAgentMessage(plan.question_to_user, plan.suggested_options, null, null, plan.spoken_response);
            setExecuting(false);
            return;
        }

        // If general query or completed
        if (plan.status === "COMPLETED") {
            appendAgentMessage(plan.message, [], null, null, plan.spoken_response);
            setExecuting(false);
            return;
        }

        // If plan has execution steps
        if (plan.steps && plan.steps.length > 0) {
            if (plan.spoken_response) {
                speakText(plan.spoken_response);
            }
            await runExecutionPipeline(plan);
        } else {
            appendAgentMessage(plan.message || "I'm ready to assist with your request.", [], null, null, plan.spoken_response);
            setExecuting(false);
        }

    } catch (err) {
        appendAgentMessage(err.message, [], "error", "Error");
        setExecuting(false);
    }
}

let currentExecCard = null;

async function runExecutionPipeline(plan) {
    const execCard = appendExecutionCard(plan.steps);
    currentExecCard = execCard;

    for (let i = 0; i < plan.steps.length; i++) {
        if (executionAborted) {
            for (let k = i; k < plan.steps.length; k++) {
                updateStepItem(execCard, k, "cancelled", "Cancelled by user");
            }
            markExecutionCancelled(execCard);
            appendAgentMessage("Task cancelled on the spot. Execution halted.", [], "warning", "Task Cancelled", "Task cancelled.");
            setExecuting(false);
            currentTaskId = null;
            return;
        }

        const step = plan.steps[i];
        updateStepItem(execCard, i, "running");

        // Fast responsive UI update
        await new Promise(r => setTimeout(r, 80));

        if (executionAborted) {
            for (let k = i; k < plan.steps.length; k++) {
                updateStepItem(execCard, k, "cancelled", "Cancelled by user");
            }
            markExecutionCancelled(execCard);
            appendAgentMessage("Task cancelled on the spot. Execution halted.", [], "warning", "Task Cancelled", "Task cancelled.");
            setExecuting(false);
            currentTaskId = null;
            return;
        }

        try {
            const execRes = await fetch("/agent/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task_id: currentTaskId })
            });

            const data = await execRes.json();

            // Check if task was cancelled on backend
            if (data.status === "CANCELLED" || executionAborted) {
                for (let k = i; k < plan.steps.length; k++) {
                    updateStepItem(execCard, k, "cancelled", "Cancelled by user");
                }
                markExecutionCancelled(execCard);
                appendAgentMessage(data.message || "Task cancelled on the spot.", [], "warning", "Task Cancelled", "Task cancelled.");
                setExecuting(false);
                currentTaskId = null;
                return;
            }

            // Check if confirmation is required
            if (data.requires_confirmation || data.status === "WAITING_FOR_CONFIRMATION") {
                if (data.spoken_response) {
                    speakText(data.spoken_response);
                }
                updateStepItem(execCard, i, "pending", "Waiting for confirmation...");
                showConfirmationCard(data.confirmation || plan.confirmation, async (confirmed) => {
                    if (confirmed) {
                        await fetch("/agent/confirm", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ task_id: currentTaskId, confirmed: true })
                        });
                        updateStepItem(execCard, i, "running");
                        const finalRes = await fetch("/agent/execute", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ task_id: currentTaskId, is_voice: voiceModeActive })
                        });
                        const finalData = await finalRes.json();
                        for (let j = i; j < plan.steps.length; j++) {
                            updateStepItem(execCard, j, "success");
                        }
                        if (finalData.desktop_result && finalData.desktop_result.opened_url) {
                            try {
                                window.open(finalData.desktop_result.opened_url, "_blank");
                            } catch (e) {
                                console.warn("Client window.open failed or blocked:", e);
                            }
                        }
                        markExecutionCompleted(execCard);
                        appendAgentMessage(finalData.message, [], "success", "Task Complete", finalData.spoken_response);
                        setExecuting(false);
                    } else {
                        executionAborted = true;
                        await fetch("/agent/confirm", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ task_id: currentTaskId, confirmed: false })
                        });
                        for (let k = i; k < plan.steps.length; k++) {
                            updateStepItem(execCard, k, "cancelled", "Action declined");
                        }
                        markExecutionCancelled(execCard);
                        appendAgentMessage("Action declined. Task cancelled on the spot.", [], "warning", "Task Cancelled", "Action declined. Task cancelled.");
                        setExecuting(false);
                        currentTaskId = null;
                    }
                });
                return;
            }

            updateStepItem(execCard, i, "success");

            if (data.desktop_result && data.desktop_result.opened_url) {
                try {
                    window.open(data.desktop_result.opened_url, "_blank");
                } catch (e) {
                    console.warn("Client window.open failed or blocked:", e);
                }
            }

            if (data.is_completed || i === plan.steps.length - 1) {
                markExecutionCompleted(execCard);
                appendAgentMessage(data.message, [], "success", "Task Complete", data.spoken_response);
                break;
            }

        } catch (err) {
            updateStepItem(execCard, i, "failed", err.message);
            appendAgentMessage(`Execution failed: ${err.message}`, [], "error", "Execution Failed");
            setExecuting(false);
            return;
        }
    }

    setExecuting(false);
}

function handleStop() {
    executionAborted = true;
    if (currentTaskId) {
        fetch("/agent/cancel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: currentTaskId, reason: "User pressed stop" })
        }).catch(() => {});
    }
    if (currentExecCard) {
        markExecutionCancelled(currentExecCard);
    }
    setExecuting(false);
}

function markExecutionCompleted(card) {
    if (!card) return;
    const header = card.querySelector("#exec-status-header");
    if (header) {
        header.innerHTML = `
          <span style="color:var(--risk-low);display:inline-flex;align-items:center;gap:6px;">
            ${ICONS.checkCircle}
            <strong style="font-weight:600;">Execution pipeline complete</strong>
          </span>
        `;
    }
}

function markExecutionCancelled(card) {
    if (!card) return;
    const header = card.querySelector("#exec-status-header");
    if (header) {
        header.innerHTML = `
          <span style="color:var(--risk-high);display:inline-flex;align-items:center;gap:6px;">
            ${ICONS.close}
            <strong style="font-weight:600;">Task Cancelled — Stopped on the spot</strong>
          </span>
        `;
    }
}

function updateStepItem(card, index, status, message = "") {
    const item = card.querySelector(`#step-item-${index}`);
    const iconWrap = card.querySelector(`#step-icon-${index}`);
    if (!item || !iconWrap) return;

    item.className = `step-item ${status}`;
    if (status === "success") {
        iconWrap.innerHTML = ICONS.check;
        iconWrap.style.color = "var(--risk-low)";
    } else if (status === "running") {
        iconWrap.innerHTML = ICONS.spinner;
        iconWrap.style.color = "var(--accent-blue)";
    } else if (status === "cancelled" || status === "failed") {
        iconWrap.innerHTML = ICONS.close;
        iconWrap.style.color = "var(--risk-high)";
    } else {
        iconWrap.innerHTML = ICONS.pending;
        iconWrap.style.color = "var(--text-muted)";
    }

    if (message) {
        const title = item.querySelector(".step-title");
        if (title) {
            title.textContent = title.textContent.split(" (")[0] + ` (${message})`;
        }
    }
    scrollToBottom();
}

function showConfirmationCard(conf, callback) {
    const container = document.getElementById("messages-container");
    const card = document.createElement("div");
    card.className = "confirmation-card";

    const title = conf?.title || "Confirm High-Risk Action";
    const service = conf?.service_type || conf?.provider || "Action";
    const pickup = conf?.pickup || "Current Location";
    const dest = conf?.destination || "Target Destination";
    const fare = conf?.fare || "N/A";
    const payment = conf?.payment_method || "Direct";
    const msg = conf?.message || "Please confirm to proceed.";

    card.innerHTML = `
      <div class="confirmation-card-header">
        ${ICONS.alert}
        <span>${escapeHtml(title)}</span>
      </div>
      <div style="font-size: 13.5px; color: var(--text-secondary);">${escapeHtml(msg)}</div>
      <div class="confirmation-grid">
        <div><strong>Service:</strong> ${escapeHtml(service)}</div>
        <div><strong>Fare / Risk:</strong> ${escapeHtml(fare)}</div>
        <div><strong>From:</strong> ${escapeHtml(pickup)}</div>
        <div><strong>To:</strong> ${escapeHtml(dest)}</div>
        <div><strong>Payment:</strong> ${escapeHtml(payment)}</div>
        <div><strong>Device:</strong> ${escapeHtml(currentDevice)}</div>
      </div>
      <div class="confirm-actions">
        <button class="btn-cancel" id="conf-cancel">Cancel</button>
        <button class="btn-confirm" id="conf-proceed">Confirm & Execute</button>
      </div>
    `;

    container.appendChild(card);
    scrollToBottom();

    card.querySelector("#conf-proceed").addEventListener("click", () => {
        card.style.opacity = "0.75";
        card.querySelector(".confirm-actions").innerHTML = `<span style="color:var(--risk-low);font-weight:600;display:inline-flex;align-items:center;gap:6px;">${ICONS.check} Confirmed. Executing action...</span>`;
        callback(true);
    });

    card.querySelector("#conf-cancel").addEventListener("click", () => {
        card.style.opacity = "0.75";
        card.querySelector(".confirm-actions").innerHTML = `<span style="color:var(--text-muted);display:inline-flex;align-items:center;gap:6px;">${ICONS.close} Cancelled</span>`;
        callback(false);
    });
}

function scrollToBottom() {
    const container = document.getElementById("messages-container");
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function formatMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Markdown Images: ![caption](url)
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.trim();
        const caption = alt.trim() || "Screen Image";
        return `
          <div class="chat-img-card">
            <img src="${cleanUrl}" alt="${caption}" class="chat-screenshot" onclick="openImageModal('${cleanUrl}')" title="Click to zoom full screen" />
            <div class="img-caption">${ICONS.zoom} <span>${caption}</span> <span style="margin-left:auto;font-size:11px;opacity:0.8;">Click to zoom</span></div>
          </div>
        `;
    });

    // Markdown Links: [label](url)
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="chat-link">$1</a>');

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');

    // Bold: **text**
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italics: *text*
    html = html.replace(/\*([^\*]+?)\*/g, "<em>$1</em>");

    // Newlines
    html = html.replace(/\n/g, "<br>");

    return html;
}

function openImageModal(url) {
    const modal = document.getElementById("image-modal");
    const img = document.getElementById("modal-img");
    if (modal && img) {
        img.src = url;
        modal.classList.add("open");
    }
}

function closeImageModal() {
    const modal = document.getElementById("image-modal");
    if (modal) {
        modal.classList.remove("open");
    }
}

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeImageModal();
        closeDiagnosticsModal();
    }
});

// ==========================================================================
// Voice & Microphone Engine (Wake Word & Calling AgentZ)
// ==========================================================================

function playActivationChime() {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        if (!audioContext || audioContext.state === "suspended") {
            audioContext = new AudioCtx();
        }
        const now = audioContext.currentTime;
        const osc1 = audioContext.createOscillator();
        const osc2 = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc1.type = "sine";
        osc2.type = "sine";
        osc1.frequency.setValueAtTime(587.33, now); // D5
        osc1.frequency.exponentialRampToValueAtTime(880.00, now + 0.12); // A5
        osc2.frequency.setValueAtTime(880.00, now + 0.12); // A5
        osc2.frequency.exponentialRampToValueAtTime(1174.66, now + 0.25); // D6
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(audioContext.destination);
        osc1.start(now);
        osc1.stop(now + 0.15);
        osc2.start(now + 0.12);
        osc2.stop(now + 0.35);
    } catch (e) {
        console.warn("Chime failed", e);
    }
}

function playDeactivationChime() {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        if (!audioContext || audioContext.state === "suspended") {
            audioContext = new AudioCtx();
        }
        const now = audioContext.currentTime;
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(659.25, now); // E5
        osc.frequency.exponentialRampToValueAtTime(440.00, now + 0.2); // A4
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        osc.connect(gain);
        gain.connect(audioContext.destination);
        osc.start(now);
        osc.stop(now + 0.25);
    } catch (e) {
        console.warn("Deactivation chime failed", e);
    }
}

function enableTTSVoice() {
    if (!ttsEnabled) {
        ttsEnabled = true;
        const ttsBtn = document.getElementById("tts-btn");
        if (ttsBtn) {
            ttsBtn.innerHTML = ICONS.speaker;
            ttsBtn.title = "Voice Output Active (Click to mute)";
            ttsBtn.style.color = "var(--accent-blue)";
        }
    }
}

function startVoiceMode(isWakeMode = false) {
    if (!recognition) {
        initVoiceEngine();
        if (!recognition) {
            alert("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
            return;
        }
    }
    voiceModeActive = true;
    enableTTSVoice();
    playActivationChime();

    const voiceBtn = document.getElementById("voice-btn");
    const voiceModeBtn = document.getElementById("voice-mode-btn");
    const voiceLabel = document.getElementById("voice-mode-label");
    const voiceStatusBar = document.getElementById("voice-status-bar");
    const soundwave = document.getElementById("soundwave-anim");
    const statusText = document.getElementById("voice-status-text");

    if (voiceBtn) {
        voiceBtn.classList.add("listening");
        voiceBtn.title = "Microphone Active (Listening... Click to stop)";
        voiceBtn.style.color = "var(--risk-low)";
    }
    if (voiceModeBtn) {
        voiceModeBtn.classList.add("active", "listening");
        if (voiceLabel) voiceLabel.innerHTML = "Voice: <strong>Listening</strong>";
    }
    if (voiceStatusBar) voiceStatusBar.style.display = "flex";
    if (soundwave) soundwave.classList.add("active");
    if (statusText) statusText.textContent = " Listening... Speak your command now";

    try {
        if (!isRecognitionRunning) {
            recognition.start();
        }
    } catch (e) {
        console.warn("Recognition already active", e);
    }
}

function stopVoiceMode(playChime = true) {
    voiceModeActive = false;
    isAwakened = false;

    const voiceBtn = document.getElementById("voice-btn");
    const voiceModeBtn = document.getElementById("voice-mode-btn");
    const voiceLabel = document.getElementById("voice-mode-label");
    const voiceStatusBar = document.getElementById("voice-status-bar");
    const soundwave = document.getElementById("soundwave-anim");

    if (voiceBtn) {
        voiceBtn.classList.remove("listening", "awakened");
        voiceBtn.title = "Voice Input (Click to speak)";
        voiceBtn.style.color = "var(--text-secondary)";
    }
    if (voiceModeBtn) {
        voiceModeBtn.classList.remove("active", "listening");
        if (voiceLabel) voiceLabel.innerHTML = "Voice: <strong>Call AgentZ</strong>";
    }
    if (voiceStatusBar) voiceStatusBar.style.display = "none";
    if (soundwave) soundwave.classList.remove("active");

    if (recognition) {
        try { recognition.stop(); } catch (e) {}
    }
    isRecognitionRunning = false;
    if (playChime) {
        playDeactivationChime();
    }
}

function triggerVoiceCall() {
    startVoiceMode(true);
}

function initVoiceEngine() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const voiceBtn = document.getElementById("voice-btn");
    const voiceModeBtn = document.getElementById("voice-mode-btn");

    if (!SpeechRecognition) {
        if (voiceBtn) voiceBtn.style.display = "none";
        if (voiceModeBtn) voiceModeBtn.style.display = "none";
        return;
    }

    if (recognition) return;

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    if (voiceBtn) {
        voiceBtn.addEventListener("click", () => {
            if (voiceModeActive) {
                stopVoiceMode(true);
            } else {
                startVoiceMode();
            }
        });
    }

    recognition.onstart = () => {
        isRecognitionRunning = true;
    };

    recognition.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const input = document.getElementById("chat-input");
        const statusText = document.getElementById("voice-status-text");

        if (finalTranscript && finalTranscript.trim()) {
            const commandText = finalTranscript.trim();
            input.value = commandText;
            if (statusText) {
                statusText.textContent = ` Command recognized: "${commandText}"`;
            }
            // Stop taking voice input immediately once command is captured
            stopVoiceMode(false);
            // Execute the recognized command
            handleSend();
        } else if (interimTranscript && interimTranscript.trim()) {
            input.value = interimTranscript.trim();
            if (statusText) {
                statusText.textContent = ` Heard: "${interimTranscript.trim()}"`;
            }
        }
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
            alert("Microphone access is needed for voice calling. Please allow microphone permissions in your browser address bar.");
        }
        stopVoiceMode(false);
    };

    recognition.onend = () => {
        isRecognitionRunning = false;
        // Do not auto-restart — microphone stays off until user clicks microphone button again
        if (!voiceModeActive) {
            const voiceBtn = document.getElementById("voice-btn");
            if (voiceBtn) {
                voiceBtn.classList.remove("listening", "awakened");
                voiceBtn.style.color = "var(--text-secondary)";
            }
        }
    };
}

function speakText(text) {
    if (!ttsEnabled || !("speechSynthesis" in window)) return;
    try {
        window.speechSynthesis.cancel();
        const cleanText = text.replace(/<[^>]*>/g, "")
                              .replace(/!\[.*?\]\(.*?\)/g, "")
                              .replace(/\[(.*?)\]\(.*?\)/g, "$1")
                              .replace(/[*_#`•]/g, "")
                              .replace(/\s+/g, " ")
                              .trim();
        if (!cleanText) return;
        const utter = new SpeechSynthesisUtterance(cleanText);
        utter.rate = 1.05;

        utter.onstart = () => {
            isSpeaking = true;
            if (recognition && isRecognitionRunning) {
                try { recognition.stop(); } catch(e) {}
            }
        };

        utter.onend = () => {
            isSpeaking = false;
            // Never auto-restart microphone after speaking
        };

        utter.onerror = () => {
            isSpeaking = false;
        };

        window.speechSynthesis.speak(utter);
    } catch (e) {
        console.warn("TTS error", e);
    }
}

function openDiagnosticsModal(data) {
    const modal = document.getElementById("diagnostics-modal");
    const body = document.getElementById("diag-details-content");
    if (!modal || !body) return;
    const s = data.stats || {};
    const batt = s.battery || {};
    const ram = s.ram || {};
    const devs = data.android_devices || [];
    body.innerHTML = `
        <div class="diag-item"><span class="label">Operating System</span><span class="val">${s.os || 'Windows 11'} (${s.machine || 'x86_64'})</span></div>
        <div class="diag-item"><span class="label">CPU Utilization</span><span class="val">${s.cpu_percent !== undefined ? s.cpu_percent : '--'}%</span></div>
        <div class="diag-item"><span class="label">RAM Total / Used</span><span class="val">${ram.total_gb || '--'} GB (${ram.percent_used || '--'}%)</span></div>
        <div class="diag-item"><span class="label">Battery Status</span><span class="val">${batt.percent || '--'}% (${batt.status || 'AC Power'})</span></div>
        <div class="diag-item"><span class="label">Disk Usage (C:)</span><span class="val">${s.disk?.percent_used || '--'}%</span></div>
        <div class="diag-item"><span class="label">Connected Android Devices</span><span class="val">${devs.length > 0 ? devs.map(d => d.id).join(', ') : 'None (Standby)'}</span></div>
    `;
    modal.classList.add("open");
}

function closeDiagnosticsModal() {
    const modal = document.getElementById("diagnostics-modal");
    if (modal) modal.classList.remove("open");
}

// --- Web Knowledge & Continuous Learning Functions ---
async function fetchWebKnowledgeStats() {
    try {
        const res = await fetch("/agent/websites");
        if (!res.ok) return;
        const data = await res.json();
        const badge = document.getElementById("learned-websites-badge");
        if (badge) {
            badge.innerText = `${data.total_websites_indexed} Websites (${data.dynamically_learned_count} Learned)`;
        }
    } catch (e) {
        console.warn("Failed to fetch website knowledge stats", e);
    }
}

async function openWebKnowledgeModal() {
    const modal = document.getElementById("web-knowledge-modal");
    const content = document.getElementById("web-knowledge-content");
    if (!modal || !content) return;
    modal.classList.add("open");
    content.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted);">Loading AgentZ Website Knowledge Base...</div>`;

    try {
        const res = await fetch("/agent/websites");
        const data = await res.json();
        const total = data.total_websites_indexed || 0;
        const dyn = data.dynamically_learned_count || 0;
        const preset = data.preset_catalog_count || 0;
        const recent = data.recent_learned || [];
        const top = data.top_visited || [];
        const cats = data.categories || {};

        let catChips = Object.entries(cats).map(([k, v]) => `
            <span style="background:var(--bg-tertiary); padding:4px 8px; border-radius:12px; font-size:11px; margin:2px 4px; display:inline-block; border:1px solid var(--border-color);">
                ${k}: <strong>${v}</strong>
            </span>
        `).join("");

        let recentHtml = recent.length ? recent.map(r => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 12px; border-bottom:1px solid var(--border-color); font-size:12px;">
                <div>
                    <strong style="color:var(--text-primary);">${r.name}</strong>
                    <div style="color:var(--text-muted); font-size:11px;">${r.url}</div>
                </div>
                <div style="text-align:right;">
                    <span style="background:#e8f0fe; color:#1a73e8; padding:2px 6px; border-radius:8px; font-size:10px; font-weight:600;">${r.source}</span>
                </div>
            </div>
        `).join("") : `<div style="color:var(--text-muted); font-style:italic; padding:8px;">No dynamic websites learned yet. Try asking 'open vit vtop' or teaching a custom site!</div>`;

        let topHtml = top.slice(0, 6).map(t => `
            <div style="display:flex; justify-content:space-between; padding:6px 10px; font-size:12px; border-bottom:1px solid var(--border-color);">
                <span style="color:var(--text-primary); font-weight:500;">${t.name}</span>
                <span style="color:var(--text-muted); font-size:11px;">Visited: <strong>${t.visit_count}x</strong></span>
            </div>
        `).join("");

        content.innerHTML = `
            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-bottom:16px;">
                <div style="background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
                    <div style="font-size:22px; font-weight:700; color:#1a73e8;">${total}</div>
                    <div style="font-size:11px; color:var(--text-muted);">Total Websites Known</div>
                </div>
                <div style="background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
                    <div style="font-size:22px; font-weight:700; color:#34a853;">${dyn}</div>
                    <div style="font-size:11px; color:var(--text-muted);">AI Dynamically Learned</div>
                </div>
                <div style="background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
                    <div style="font-size:22px; font-weight:700; color:#fbbc04;">${preset}</div>
                    <div style="font-size:11px; color:var(--text-muted);">Foundational Catalog</div>
                </div>
            </div>

            <!-- Teach Agent Website Form -->
            <div style="background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; padding:12px; margin-bottom:16px;">
                <div style="font-weight:600; font-size:13px; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
                    <span>🎓</span> Teach AgentZ a Custom Website / Portal
                </div>
                <div style="display:flex; gap:8px;">
                    <input id="teach-name" placeholder="Name / Shortcut (e.g. My College Portal)" style="flex:1; padding:8px 10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary); font-size:12px;" />
                    <input id="teach-url" placeholder="URL (e.g. https://portal.college.edu)" style="flex:1.5; padding:8px 10px; border-radius:6px; border:1px solid var(--border-color); background:var(--bg-primary); color:var(--text-primary); font-size:12px;" />
                    <button onclick="submitTeachWebsite()" style="background:#1a73e8; color:#fff; border:none; border-radius:6px; padding:8px 14px; font-weight:600; font-size:12px; cursor:pointer;">Teach</button>
                </div>
                <div id="teach-msg" style="font-size:11px; margin-top:6px; color:#34a853; display:none;"></div>
            </div>

            <!-- Categories -->
            <div style="margin-bottom:16px;">
                <div style="font-weight:600; font-size:12px; color:var(--text-muted); margin-bottom:6px;">INDEXED CATEGORIES</div>
                <div>${catChips}</div>
            </div>

            <!-- Recently Learned by AI -->
            <div style="margin-bottom:16px;">
                <div style="font-weight:600; font-size:12px; color:var(--text-muted); margin-bottom:6px;">RECENTLY LEARNED BY AI AGENT</div>
                <div style="background:var(--bg-primary); border:1px solid var(--border-color); border-radius:8px; max-height:160px; overflow-y:auto;">
                    ${recentHtml}
                </div>
            </div>

            <!-- Top Visited -->
            <div>
                <div style="font-weight:600; font-size:12px; color:var(--text-muted); margin-bottom:6px;">MOST FREQUENTLY ACCESSED SITES</div>
                <div style="background:var(--bg-primary); border:1px solid var(--border-color); border-radius:8px;">
                    ${topHtml}
                </div>
            </div>
        `;
    } catch (e) {
        content.innerHTML = `<div style="color:#d93025; padding:15px;">Failed to load website knowledge: ${e.message}</div>`;
    }
}

function closeWebKnowledgeModal() {
    const modal = document.getElementById("web-knowledge-modal");
    if (modal) modal.classList.remove("open");
}

async function submitTeachWebsite() {
    const nameInput = document.getElementById("teach-name");
    const urlInput = document.getElementById("teach-url");
    const msgEl = document.getElementById("teach-msg");
    if (!nameInput || !urlInput) return;
    const name = nameInput.value.trim();
    let url = urlInput.value.trim();
    if (!name || !url) {
        alert("Please enter both a website name and URL.");
        return;
    }
    if (!url.startsWith("http")) url = "https://" + url;

    try {
        const res = await fetch("/agent/learn-website", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, url })
        });
        const data = await res.json();
        if (data.status === "success") {
            if (msgEl) {
                msgEl.innerText = `✓ Successfully learned and saved '${name}'! You can now say 'open ${name}'.`;
                msgEl.style.display = "block";
            }
            nameInput.value = "";
            urlInput.value = "";
            fetchWebKnowledgeStats();
            setTimeout(() => { openWebKnowledgeModal(); }, 1200);
        }
    } catch (e) {
        alert("Error saving website: " + e.message);
    }
}
