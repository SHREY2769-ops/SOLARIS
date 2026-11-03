/* SOLARIS - Frontend Logic */
document.addEventListener('DOMContentLoaded', () => {
  const orb = document.getElementById('orb');
  const app = document.getElementById('app');
  const userInput = document.getElementById('user-input');
  const conversation = document.getElementById('conversation');
  const voiceControls = document.getElementById('voice-controls');
  const tabs = document.querySelectorAll('.tab');
  const themeToggle = document.getElementById('theme-toggle');
  
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };
  let isListening = false;
  let currentTheme = 'cyan';
  
  // Orb drag functionality
  orb.addEventListener('mousedown', (e) => {
    if (e.target.className.includes('logo') || e.target.className.includes('status')) return;
    isDragging = true;
    dragOffset = {
      x: e.clientX - orb.getBoundingClientRect().left,
      y: e.clientY - orb.getBoundingClientRect().top
    };
    orb.style.cursor = 'grabbing';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const x = e.clientX - dragOffset.x;
    const y = e.clientY - dragOffset.y;
    orb.style.left = `${x}px`;
    orb.style.top = `${y}px`;
  });
  
  document.addEventListener('mouseup', () => {
    isDragging = false;
    orb.style.cursor = 'grab';
  });
  
  // Click to open app
  orb.addEventListener('click', (e) => {
    if (e.target.className.includes('logo')) {
      toggleApp();
    }
  });
  
  function toggleApp() {
    app.classList.toggle('active');
    if (app.classList.contains('active')) {
      orb.classList.add('dragging');
    } else {
      orb.classList.remove('dragging');
    }
  }
  
  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      // Switch views based on tab
      const view = tab.dataset.view;
      switchView(view);
    });
  });
  
  function switchView(view) {
    // Hide all content sections
    document.querySelectorAll('.view').forEach(s => s.style.display = 'none');
    // Show selected view
    const viewEl = document.getElementById(`${view}-view`);
    if (viewEl) {
      viewEl.style.display = 'block';
    }
  }
  
  // Voice input
  userInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const text = userInput.value.trim();
      if (text) {
        addMessage(text, 'user');
        userInput.value = '';
        processUserInput(text);
      }
    }
  });
  
  function addMessage(text, sender) {
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    msg.textContent = text;
    conversation.appendChild(msg);
    conversation.scrollTop = conversation.scrollHeight;
  }
  
  function processUserInput(text) {
    // Simple command handling
    if (text.toLowerCase().includes('hello') || text.toLowerCase().includes('hi')) {
      addMessage('Hello! I am SOLARIS, your personal AI assistant.', 'assistant');
    } else if (text.toLowerCase().includes('how are you')) {
      addMessage('I am functioning optimally. How can I assist you today?', 'assistant');
    } else if (text.toLowerCase().includes('time')) {
      const now = new Date();
      addMessage(`The current time is ${now.toLocaleTimeString()}`, 'assistant');
    } else {
      addMessage(`I received your message: "${text}". This feature is under development.', 'assistant');
    }
  }
  
  // Theme switching
  themeToggle.addEventListener('change', (e) => {
    currentTheme = e.target.value;
    document.documentElement.style.setProperty('--accent', getThemeColor(currentTheme));
    // Update orb
    updateOrbTheme(currentTheme);
  });
  
  function getThemeColor(theme) {
    const colors = {
      cyan: '#00d4aa',
      azure: '#4d8dff',
      violet: '#9b7bff',
      magenta: '#ff5fd2',
      crimson: '#ff4d5e',
      orange: '#ff8a3d',
      amber: '#ffc84a',
      lime: '#b6f04a',
      green: '#3dffa0',
      teal: '#2fe0d0',
      rose: '#ff8fb3',
      silver: '#dfe8f2'
    };
    return colors[theme] || '#00d4aa';
  }
  
  function updateOrbTheme(theme) {
    const color = getThemeColor(theme);
    orb.style.background = `linear-gradient(135deg, ${color} 0%, ${darkenColor(color)} 100%)`;
    orb.style.boxShadow = `0 0 30px rgba(${rgbToCss(color)}, 0.4), 0 0 60px rgba(${rgbToCss(color)}, 0.2)`;
  }
  
  function darkenColor(hex) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = (num >> 16) + 20;
    const g = ((num >> 8) & 0x0000FF) - 20;
    const b = (num & 0x000000FF) + 20;
    return `#${((r < 0 ? 0 : r > 255 ? 255 : r) << 16 | (g < 0 ? 0 : g > 255 ? 255 : g) << 8 | (b < 0 ? 0 : b > 255 ? 255 : b)).toString(16).padStart(6, '0')}`;
  }
  
  function rgbToCss(color) {
    return `${color}, ${color}, ${color}`;
  }
  
  // Initialize
  updateOrbTheme(currentTheme);
});