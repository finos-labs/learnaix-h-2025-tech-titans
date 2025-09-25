/**
 * AI Learning Companion Plugin JavaScript
 * Enhanced functionality for the AI companion interface
 */

// Global variables
let chatHistory = [];
let currentUser = null;
let isTyping = false;

// Initialize the AI Companion when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    initializeAICompanion();
});

/**
 * Initialize the AI Companion application
 */
function initializeAICompanion() {
    console.log("Initializing AI Learning Companion...");
    
    // Get current user ID from the page
    const userElement = document.querySelector('[data-user-id]');
    if (userElement) {
        currentUser = userElement.dataset.userId;
    }
    
    // Initialize all components
    setupEventListeners();
    loadUserSettings();
    loadProgressData();
    loadAnalyticsData();
    initializeTabs();
    
    console.log("AI Learning Companion initialized successfully!");
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Chat input events
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");
    const clearButton = document.getElementById("clear-button");
    
    if (chatInput) {
        chatInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        chatInput.addEventListener("input", function() {
            // Auto-resize input
            this.style.height = "auto";
            this.style.height = this.scrollHeight + "px";
        });
    }
    
    if (sendButton) {
        sendButton.addEventListener("click", sendMessage);
    }
    
    if (clearButton) {
        clearButton.addEventListener("click", clearChat);
    }
    
    // Settings form
    const settingsForm = document.getElementById("settings-form");
    if (settingsForm) {
        settingsForm.addEventListener("submit", saveSettings);
    }
    
    // Tab switching
    const tabLinks = document.querySelectorAll('.tabtree a');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            switchTab(this.getAttribute('href').substring(1));
        });
    });
}

/**
 * Initialize tab functionality
 */
function initializeTabs() {
    // Show first tab by default
    const firstTab = document.querySelector('.tab-content');
    if (firstTab) {
        firstTab.classList.add('active');
    }
}

/**
 * Switch between tabs
 */
function switchTab(tabId) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Update active tab styling
    const tabLinks = document.querySelectorAll('.tabtree a');
    tabLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`.tabtree a[href="#${tabId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

/**
 * Send a message to the AI
 */
function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    
    if (!message || isTyping) return;
    
    // Add user message to chat
    addMessageToChat(message, "user");
    input.value = "";
    input.style.height = "auto";
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to AI service
    sendToAI(message);
}

/**
 * Send a suggestion as a message
 */
function sendSuggestion(suggestion) {
    const input = document.getElementById("chat-input");
    input.value = suggestion;
    sendMessage();
}

/**
 * Add message to chat display
 */
function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    
    // Format message content
    if (sender === "ai") {
        contentDiv.innerHTML = formatAIResponse(message);
    } else {
        contentDiv.textContent = message;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
    
    // Store in history
    chatHistory.push({
        message: message,
        sender: sender,
        timestamp: new Date()
    });
    
    // Limit chat history
    const maxHistory = 50; // This should come from settings
    if (chatHistory.length > maxHistory) {
        chatHistory = chatHistory.slice(-maxHistory);
    }
}

/**
 * Format AI response with markdown-like formatting
 */
function formatAIResponse(message) {
    // Convert line breaks to HTML
    let formatted = message.replace(/\n/g, '<br>');
    
    // Convert **bold** to <strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert bullet points
    formatted = formatted.replace(/^•\s(.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return formatted;
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const chatMessages = document.getElementById("chat-messages");
    const typingDiv = document.createElement("div");
    typingDiv.className = "message ai-message typing";
    typingDiv.id = "typing-indicator";
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.innerHTML = '<em>AI is typing...</em>';
    
    typingDiv.appendChild(contentDiv);
    chatMessages.appendChild(typingDiv);
    
    // Smooth scroll to bottom
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
    
    isTyping = true;
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isTyping = false;
}

/**
 * Send message to AI service via AJAX
 */
function sendToAI(message) {
    // Create form data
    const formData = new FormData();
    formData.append('action', 'chat');
    formData.append('message', message);
    formData.append('user_id', currentUser);
    formData.append('chat_history', JSON.stringify(chatHistory));
    
    // Make AJAX request
    fetch('ajax.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator();
        
        if (data.success) {
            addMessageToChat(data.response, "ai");
        } else {
            addMessageToChat("Sorry, I encountered an error. Please try again.", "ai");
            console.error('AI Error:', data.error);
        }
    })
    .catch(error => {
        removeTypingIndicator();
        addMessageToChat("Sorry, I'm having trouble connecting. Please try again later.", "ai");
        console.error('Network Error:', error);
    });
}

/**
 * Clear chat history
 */
function clearChat() {
    if (confirm("Are you sure you want to clear the chat history?")) {
        const chatMessages = document.getElementById("chat-messages");
        chatMessages.innerHTML = `
            <div class="message ai-message">
                <div class="message-content">Hello! I'm your AI Learning Companion. How can I help you learn today?</div>
            </div>
        `;
        chatHistory = [];
    }
}

/**
 * Load user settings from server
 */
function loadUserSettings() {
    fetch('ajax.php?action=get_settings&user_id=' + currentUser)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Populate settings form
            const settings = data.settings;
            if (settings.ai_personality) {
                document.getElementById('ai_personality').value = settings.ai_personality;
            }
            if (settings.learning_style) {
                document.getElementById('learning_style').value = settings.learning_style;
            }
            if (settings.difficulty_level) {
                document.getElementById('difficulty_level').value = settings.difficulty_level;
            }
            if (settings.notifications) {
                document.getElementById('notifications').checked = settings.notifications;
            }
        }
    })
    .catch(error => {
        console.error('Error loading settings:', error);
    });
}

/**
 * Save user settings
 */
function saveSettings(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('action', 'save_settings');
    formData.append('user_id', currentUser);
    formData.append('ai_personality', document.getElementById('ai_personality').value);
    formData.append('learning_style', document.getElementById('learning_style').value);
    formData.append('difficulty_level', document.getElementById('difficulty_level').value);
    formData.append('notifications', document.getElementById('notifications').checked ? '1' : '0');
    
    fetch('ajax.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Settings saved successfully!', 'success');
        } else {
            showNotification('Error saving settings. Please try again.', 'error');
        }
    })
    .catch(error => {
        showNotification('Error saving settings. Please try again.', 'error');
        console.error('Error:', error);
    });
}

/**
 * Load progress data
 */
function loadProgressData() {
    fetch('ajax.php?action=get_progress&user_id=' + currentUser)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayProgressData(data.progress);
        }
    })
    .catch(error => {
        console.error('Error loading progress:', error);
    });
}

/**
 * Display progress data
 */
function displayProgressData(progress) {
    // Display goals
    const goalsContainer = document.getElementById('goals-container');
    if (goalsContainer && progress.goals) {
        goalsContainer.innerHTML = progress.goals.map(goal => `
            <div class="goal-item">
                <h5>${goal.title}</h5>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${goal.progress}%"></div>
                </div>
                <span class="progress-text">${goal.progress}% Complete</span>
            </div>
        `).join('');
    }
    
    // Display achievements
    const achievementsContainer = document.getElementById('achievements-container');
    if (achievementsContainer && progress.achievements) {
        achievementsContainer.innerHTML = progress.achievements.map(achievement => `
            <div class="achievement-item">
                <div class="achievement-icon">🏆</div>
                <div class="achievement-text">
                    <h5>${achievement.title}</h5>
                    <p>${achievement.description}</p>
                </div>
            </div>
        `).join('');
    }
    
    // Display statistics
    const statsContainer = document.getElementById('stats-container');
    if (statsContainer && progress.stats) {
        statsContainer.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${progress.stats.learning_time}</div>
                <div class="stat-label">Hours This Week</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${progress.stats.completed_courses}</div>
                <div class="stat-label">Courses Completed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${progress.stats.current_streak}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        `;
    }
}

/**
 * Load analytics data
 */
function loadAnalyticsData() {
    fetch('ajax.php?action=get_analytics&user_id=' + currentUser)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAnalyticsData(data.analytics);
        }
    })
    .catch(error => {
        console.error('Error loading analytics:', error);
    });
}

/**
 * Display analytics data
 */
function displayAnalyticsData(analytics) {
    // Display strengths
    const strengthsContainer = document.getElementById('strengths-container');
    if (strengthsContainer && analytics.strengths) {
        strengthsContainer.innerHTML = analytics.strengths.map(strength => `
            <div class="strength-item">
                <div class="strength-icon">💪</div>
                <div class="strength-text">${strength}</div>
            </div>
        `).join('');
    }
    
    // Display improvements
    const improvementsContainer = document.getElementById('improvements-container');
    if (improvementsContainer && analytics.improvements) {
        improvementsContainer.innerHTML = analytics.improvements.map(improvement => `
            <div class="improvement-item">
                <div class="improvement-icon">📈</div>
                <div class="improvement-text">${improvement}</div>
            </div>
        `).join('');
    }
    
    // Display recommendations
    const recommendationsContainer = document.getElementById('recommendations-container');
    if (recommendationsContainer && analytics.recommendations) {
        recommendationsContainer.innerHTML = analytics.recommendations.map(recommendation => `
            <div class="recommendation-item">
                <div class="recommendation-icon">💡</div>
                <div class="recommendation-text">${recommendation}</div>
            </div>
        `).join('');
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#dc3545';
    } else {
        notification.style.backgroundColor = '#007bff';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
