// Starvios Assistant — Frontend Logic
// Creado y Desarrollado por: CORNEJOXx (c) 2026
console.log(
  "%c⭐ Starvios Assistant v1.0 ⭐\n%cCreado y Desarrollado por CORNEJOXx\nTodos los derechos reservados © 2026",
  "color: #ff5d9e; font-size: 16px; font-weight: bold;",
  "color: #00f0ff; font-size: 13px; font-weight: 600;"
);

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const connectionBadge = document.getElementById("connectionBadge");
  const connectionText = document.getElementById("connectionText");
  const liveBadge = document.getElementById("liveBadge");
  const liveText = document.getElementById("liveText");
  const speakingIndicator = document.getElementById("speakingIndicator");
  const speakingText = document.getElementById("speakingText");
  
  const channelTokenInput = document.getElementById("channelTokenInput");
  const saveTokenBtn = document.getElementById("saveTokenBtn");
  const saveTokenFeedback = document.getElementById("saveTokenFeedback");
  const tokenStatusBadge = document.getElementById("tokenStatusBadge");

  const obsUrlInput = document.getElementById("obsUrlInput");
  const copyObsBtn = document.getElementById("copyObsBtn");
  const copyFeedback = document.getElementById("copyFeedback");

  const ttsToggle = document.getElementById("ttsToggle");
  const voiceSelect = document.getElementById("voiceSelect");
  const rateSlider = document.getElementById("rateSlider");
  const rateValue = document.getElementById("rateValue");
  const volumeSlider = document.getElementById("volumeSlider");
  const volumeValue = document.getElementById("volumeValue");
  const readUsernameToggle = document.getElementById("readUsernameToggle");
  const filterCommandsToggle = document.getElementById("filterCommandsToggle");
  const testVoiceBtn = document.getElementById("testVoiceBtn");

  const messagesList = document.getElementById("messagesList");
  const emptyState = document.getElementById("emptyState");
  const messageCountBadge = document.getElementById("messageCountBadge");
  const clearChatBtn = document.getElementById("clearChatBtn");

  let messages = [];

  // Save Token
  if (saveTokenBtn && channelTokenInput) {
    const handleSaveToken = async () => {
      const val = channelTokenInput.value.trim();
      await saveSetting("token", val);
      if (saveTokenFeedback) {
        saveTokenFeedback.classList.add("show");
        saveTokenBtn.classList.add("btn-success");
        setTimeout(() => {
          saveTokenFeedback.classList.remove("show");
          saveTokenBtn.classList.remove("btn-success");
        }, 2500);
      }
    };
    saveTokenBtn.addEventListener("click", handleSaveToken);
    channelTokenInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleSaveToken();
    });
  }

  // Copy Official OBS URL
  copyObsBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(obsUrlInput.value);
      copyFeedback.classList.add("show");
      copyObsBtn.classList.add("btn-success");
      setTimeout(() => {
        copyFeedback.classList.remove("show");
        copyObsBtn.classList.remove("btn-success");
      }, 2500);
    } catch (err) {
      obsUrlInput.select();
      document.execCommand("copy");
      copyFeedback.classList.add("show");
      setTimeout(() => copyFeedback.classList.remove("show"), 2500);
    }
  });

  // Copy Local OBS URL
  const copyLocalObsBtn = document.getElementById("copyLocalObsBtn");
  const localObsUrlInput = document.getElementById("localObsUrlInput");
  const copyLocalFeedback = document.getElementById("copyLocalFeedback");

  if (copyLocalObsBtn) {
    copyLocalObsBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(localObsUrlInput.value);
        copyLocalFeedback.classList.add("show");
        copyLocalObsBtn.classList.add("btn-success");
        setTimeout(() => {
          copyLocalFeedback.classList.remove("show");
          copyLocalObsBtn.classList.remove("btn-success");
        }, 2500);
      } catch (err) {
        localObsUrlInput.select();
        document.execCommand("copy");
        copyLocalFeedback.classList.add("show");
        setTimeout(() => copyLocalFeedback.classList.remove("show"), 2500);
      }
    });
  }

  // Slider formatting helpers
  function updateRateLabel(val) {
    const num = parseInt(val);
    let label = `${num}`;
    if (num > 0) label = `+${num} (Rápido)`;
    else if (num === 0) label = `0 (Normal)`;
    else label = `${num} (Lento)`;
    rateValue.textContent = label;
  }

  function updateVolumeLabel(val) {
    volumeValue.textContent = `${val}%`;
  }

  // Update Settings via API
  async function saveSetting(key, val) {
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [key]: val })
      });
    } catch (err) {
      console.error("Error guardando ajuste:", err);
    }
  }

  // Event Listeners for Controls
  ttsToggle.addEventListener("change", (e) => saveSetting("tts_enabled", e.target.checked));
  voiceSelect.addEventListener("change", (e) => saveSetting("voice_name", e.target.value));
  
  rateSlider.addEventListener("input", (e) => updateRateLabel(e.target.value));
  rateSlider.addEventListener("change", (e) => saveSetting("rate", parseInt(e.target.value)));

  volumeSlider.addEventListener("input", (e) => updateVolumeLabel(e.target.value));
  volumeSlider.addEventListener("change", (e) => saveSetting("volume", parseInt(e.target.value)));

  readUsernameToggle.addEventListener("change", (e) => saveSetting("read_username", e.target.checked));
  filterCommandsToggle.addEventListener("change", (e) => saveSetting("filter_commands", e.target.checked));

  // Test Voice Button
  testVoiceBtn.addEventListener("click", async () => {
    testVoiceBtn.disabled = true;
    try {
      await fetch("/api/test-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "Hola streamer, el lector de chat para Starvios está activo y funcionando en tus audífonos." })
      });
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => { testVoiceBtn.disabled = false; }, 1200);
    }
  });

  // Clear Chat History
  clearChatBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/clear", { method: "POST" });
      messages = [];
      renderMessages();
    } catch (err) {
      console.error(err);
    }
  });

  // Render a Single Message Item
  function createMessageElement(msg) {
    const isDonation = msg.coins > 0;
    const card = document.createElement("div");
    card.className = `msg-card ${isDonation ? "donation" : ""}`;
    card.id = `msg-${msg.id}`;

    const color = msg.color || "#5CFF67";
    const name = escapeHtml(msg.name || "Espectador");
    const body = escapeHtml(msg.body || "");
    const time = msg.time || new Date().toLocaleTimeString();

    let donationBadge = "";
    if (isDonation) {
      donationBadge = `
        <span class="starvies-tag">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          +${msg.coins} Starvies
        </span>
      `;
    }

    card.innerHTML = `
      <div class="msg-content">
        <div class="msg-header">
          <span class="msg-author" style="color: ${color}">${name}</span>
          ${donationBadge}
          <span class="msg-time">${time}</span>
        </div>
        <div class="msg-text">${body}</div>
      </div>
      <div class="msg-actions">
        <button class="repeat-btn" title="Escuchar de nuevo este mensaje">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
          </svg>
        </button>
      </div>
    `;

    const repeatBtn = card.querySelector(".repeat-btn");
    repeatBtn.addEventListener("click", () => {
      const speech = isDonation ? `${name} donó ${msg.coins} Starvies: ${msg.body}` : `${name} dice: ${msg.body}`;
      fetch("/api/test-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: speech })
      });
    });

    return card;
  }

  function renderMessages() {
    messageCountBadge.textContent = `${messages.length} mensaje${messages.length === 1 ? "" : "s"}`;
    if (messages.length === 0) {
      messagesList.innerHTML = "";
      messagesList.appendChild(emptyState);
      return;
    }

    if (emptyState.parentNode === messagesList) {
      messagesList.removeChild(emptyState);
    }

    messagesList.innerHTML = "";
    messages.slice().reverse().forEach(msg => {
      messagesList.appendChild(createMessageElement(msg));
    });
  }

  function addMessage(msg) {
    messages.push(msg);
    if (messages.length > 100) messages.shift();
    renderMessages();
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Populate Voices in Dropdown
  function populateVoices(voices, selectedVoice) {
    if (!voices || voices.length === 0) return;
    voiceSelect.innerHTML = "";
    voices.forEach(v => {
      const opt = document.createElement("option");
      opt.value = v.id;
      opt.textContent = v.name;
      if (selectedVoice && v.id === selectedVoice) {
        opt.selected = true;
      }
      voiceSelect.appendChild(opt);
    });
  }

  // Apply Config from Backend
  function applyConfig(cfg) {
    if (!cfg) return;
    if (cfg.token && cfg.token.trim()) {
      if (channelTokenInput) channelTokenInput.value = cfg.token.trim();
      if (tokenStatusBadge) {
        tokenStatusBadge.textContent = "Conectado";
        tokenStatusBadge.style.background = "rgba(92, 255, 103, 0.2)";
        tokenStatusBadge.style.color = "#5CFF67";
      }
      obsUrlInput.value = `https://starvios.com/overlay/chat/${cfg.token.trim()}`;
    } else {
      if (channelTokenInput && !channelTokenInput.value) channelTokenInput.value = "";
      if (tokenStatusBadge) {
        tokenStatusBadge.textContent = "Sin configurar";
        tokenStatusBadge.style.background = "rgba(255, 93, 158, 0.2)";
        tokenStatusBadge.style.color = "#ff5d9e";
      }
      obsUrlInput.value = "https://starvios.com/overlay/chat/TU_TOKEN";
    }
    ttsToggle.checked = !!cfg.tts_enabled;
    readUsernameToggle.checked = !!cfg.read_username;
    filterCommandsToggle.checked = !!cfg.filter_commands;
    
    rateSlider.value = cfg.rate !== undefined ? cfg.rate : 1;
    updateRateLabel(rateSlider.value);

    volumeSlider.value = cfg.volume !== undefined ? cfg.volume : 100;
    updateVolumeLabel(volumeSlider.value);
  }

  // Handle Speech Indicators
  function setSpeaking(isSpeaking, text = "") {
    if (isSpeaking) {
      speakingIndicator.classList.remove("hidden");
      speakingText.textContent = text ? (text.length > 30 ? text.slice(0, 30) + "..." : text) : "Leyendo mensaje...";
    } else {
      speakingIndicator.classList.add("hidden");
    }
  }

  // Connect SSE for Real-Time Streaming
  function connectSSE() {
    const eventSource = new EventSource("/api/events");

    eventSource.addEventListener("init", (e) => {
      try {
        const data = JSON.parse(e.data);
        applyConfig(data.config);
        
        connectionBadge.className = "status-badge connected";
        connectionText.textContent = "Conectado a Starvios";

        if (data.state.is_live) {
          liveBadge.className = "status-badge stream-status live";
          liveText.textContent = "EN VIVO";
        } else {
          liveBadge.className = "status-badge stream-status offline";
          liveText.textContent = "Canal Offline";
        }

        if (data.state.voices) {
          populateVoices(data.state.voices, data.config.voice_name);
        }

        setSpeaking(data.state.is_speaking, data.state.current_speech);

        messages = data.state.messages || [];
        renderMessages();
      } catch (err) {
        console.error("Error al procesar init:", err);
      }
    });

    eventSource.addEventListener("init_messages", (e) => {
      try {
        const msgs = JSON.parse(e.data);
        if (Array.isArray(msgs)) {
          messages = msgs;
          renderMessages();
        }
      } catch (err) {
        console.error("Error en init_messages:", err);
      }
    });

    eventSource.addEventListener("status_update", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.connected) {
          connectionBadge.className = "status-badge connected";
          connectionText.textContent = "Conectado a Starvios";
        } else {
          connectionBadge.className = "status-badge connecting";
          connectionText.textContent = "Reconectando...";
        }

        if (data.is_live) {
          liveBadge.className = "status-badge stream-status live";
          liveText.textContent = "EN VIVO";
        } else {
          liveBadge.className = "status-badge stream-status offline";
          liveText.textContent = "Canal Offline";
        }
      } catch (err) {
        console.error("Error en status_update:", err);
      }
    });

    eventSource.addEventListener("new_message", (e) => {
      try {
        const msg = JSON.parse(e.data);
        addMessage(msg);
      } catch (err) {
        console.error("Error al recibir mensaje:", err);
      }
    });

    eventSource.addEventListener("speech_start", (e) => {
      try {
        const data = JSON.parse(e.data);
        setSpeaking(true, data.text);
      } catch (err) {
        setSpeaking(true);
      }
    });

    eventSource.addEventListener("speech_end", () => {
      setSpeaking(false);
    });

    eventSource.addEventListener("config_updated", (e) => {
      try {
        const cfg = JSON.parse(e.data);
        applyConfig(cfg);
      } catch (err) {
        console.error(err);
      }
    });

    eventSource.addEventListener("cleared", () => {
      messages = [];
      renderMessages();
    });

    eventSource.onerror = () => {
      connectionBadge.className = "status-badge connecting";
      connectionText.textContent = "Reconectando...";
    };
  }

  // Polling sync fallback (checks /api/status every 3s)
  setInterval(async () => {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        if (data.state) {
          if (data.state.connected) {
            connectionBadge.className = "status-badge connected";
            connectionText.textContent = "Conectado a Starvios";
          }
          if (data.state.is_live !== undefined) {
            liveBadge.className = `status-badge stream-status ${data.state.is_live ? "live" : "offline"}`;
            liveText.textContent = data.state.is_live ? "EN VIVO" : "Canal Offline";
          }
          if (Array.isArray(data.state.messages) && data.state.messages.length > 0) {
            if (messages.length === 0 || data.state.messages[data.state.messages.length - 1]?.id !== messages[messages.length - 1]?.id) {
              messages = data.state.messages;
              renderMessages();
            }
          }
        }
      }
    } catch (err) {
      // Offline / server rebooting
    }
  }, 3000);

  connectSSE();
});
