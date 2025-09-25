<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * AI Learning Companion Plugin
 *
 * @package    local_aicompanion
 * @copyright  2025 NatWest Hack4aCause
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');
require_once($CFG->libdir.'/adminlib.php');
require_once($CFG->dirroot.'/local/aicompanion/lib.php');

// Check if user is logged in
require_login();

// Check capabilities
$context = context_system::instance();
require_capability('local/aicompanion:view', $context);

// Set up the page
$PAGE->set_url('/local/aicompanion/index.php');
$PAGE->set_context($context);
$PAGE->set_title(get_string('nav_title', 'local_aicompanion'));
$PAGE->set_heading(get_string('nav_title', 'local_aicompanion'));
$PAGE->set_pagelayout('standard');

// Add CSS and JavaScript
$PAGE->requires->css('/local/aicompanion/styles.css');
$PAGE->requires->js('/local/aicompanion/script.js');

// Get user information
$user = $USER;
$userid = $user->id;

// Get plugin configuration
$config = get_config('local_aicompanion');

// Check if features are enabled
$chat_enabled = get_config('local_aicompanion', 'enable_chat');
$progress_enabled = get_config('local_aicompanion', 'enable_progress');
$analytics_enabled = get_config('local_aicompanion', 'enable_analytics');

// Start output
echo $OUTPUT->header();

// Display welcome message
echo html_writer::div(
    html_writer::tag('h2', get_string('welcome_message', 'local_aicompanion'), array('class' => 'welcome-title')),
    'welcome-container'
);

// Create tab navigation
$tabs = array();
if ($chat_enabled) {
    $tabs[] = new tabobject('chat', '#chat', get_string('chat_tab', 'local_aicompanion'));
}
if ($progress_enabled) {
    $tabs[] = new tabobject('progress', '#progress', get_string('progress_tab', 'local_aicompanion'));
}
if ($analytics_enabled) {
    $tabs[] = new tabobject('analytics', '#analytics', get_string('analytics_tab', 'local_aicompanion'));
}
$tabs[] = new tabobject('settings', '#settings', get_string('settings_tab', 'local_aicompanion'));

echo $OUTPUT->tabtree($tabs, 'chat');

// Chat Tab
if ($chat_enabled) {
    echo html_writer::start_div('tab-content', array('id' => 'chat'));
    echo html_writer::tag('h3', get_string('chat_title', 'local_aicompanion'));
    echo html_writer::tag('p', get_string('chat_subtitle', 'local_aicompanion'), array('class' => 'subtitle'));
    
    // Chat container
    echo html_writer::start_div('chat-container');
    
    // Chat messages area
    echo html_writer::start_div('chat-messages', array('id' => 'chat-messages'));
    
    // Initial AI greeting
    echo html_writer::start_div('message ai-message');
    echo html_writer::start_div('message-content');
    echo html_writer::tag('div', get_string('ai_greeting', 'local_aicompanion'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    echo html_writer::end_div(); // chat-messages
    
    // Suggested questions
    echo html_writer::start_div('suggested-questions');
    echo html_writer::tag('h4', get_string('suggested_questions', 'local_aicompanion'));
    echo html_writer::start_div('suggestions-grid');
    
    $suggestions = array(
        get_string('suggested_q1', 'local_aicompanion'),
        get_string('suggested_q2', 'local_aicompanion'),
        get_string('suggested_q3', 'local_aicompanion'),
        get_string('suggested_q4', 'local_aicompanion')
    );
    
    foreach ($suggestions as $suggestion) {
        echo html_writer::tag('button', $suggestion, array(
            'class' => 'suggestion-btn',
            'onclick' => 'sendSuggestion(this.textContent)'
        ));
    }
    
    echo html_writer::end_div(); // suggestions-grid
    echo html_writer::end_div(); // suggested-questions
    
    // Chat input area
    echo html_writer::start_div('chat-input-container');
    echo html_writer::tag('input', '', array(
        'type' => 'text',
        'id' => 'chat-input',
        'placeholder' => get_string('chat_placeholder', 'local_aicompanion'),
        'class' => 'chat-input'
    ));
    echo html_writer::tag('button', get_string('send_button', 'local_aicompanion'), array(
        'id' => 'send-button',
        'class' => 'send-button',
        'onclick' => 'sendMessage()'
    ));
    echo html_writer::tag('button', get_string('clear_chat', 'local_aicompanion'), array(
        'id' => 'clear-button',
        'class' => 'clear-button',
        'onclick' => 'clearChat()'
    ));
    echo html_writer::end_div(); // chat-input-container
    
    echo html_writer::end_div(); // chat-container
    echo html_writer::end_div(); // chat tab
}

// Progress Tab
if ($progress_enabled) {
    echo html_writer::start_div('tab-content', array('id' => 'progress'));
    echo html_writer::tag('h3', get_string('progress_title', 'local_aicompanion'));
    echo html_writer::tag('p', get_string('progress_subtitle', 'local_aicompanion'), array('class' => 'subtitle'));
    
    // Progress dashboard
    echo html_writer::start_div('progress-dashboard');
    
    // Learning goals
    echo html_writer::start_div('progress-section');
    echo html_writer::tag('h4', get_string('current_goals', 'local_aicompanion'));
    echo html_writer::start_div('goals-container', array('id' => 'goals-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    // Achievements
    echo html_writer::start_div('progress-section');
    echo html_writer::tag('h4', get_string('achievements', 'local_aicompanion'));
    echo html_writer::start_div('achievements-container', array('id' => 'achievements-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    // Learning statistics
    echo html_writer::start_div('progress-section');
    echo html_writer::tag('h4', get_string('learning_time', 'local_aicompanion'));
    echo html_writer::start_div('stats-container', array('id' => 'stats-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    echo html_writer::end_div(); // progress-dashboard
    echo html_writer::end_div(); // progress tab
}

// Analytics Tab
if ($analytics_enabled) {
    echo html_writer::start_div('tab-content', array('id' => 'analytics'));
    echo html_writer::tag('h3', get_string('analytics_title', 'local_aicompanion'));
    echo html_writer::tag('p', get_string('analytics_subtitle', 'local_aicompanion'), array('class' => 'subtitle'));
    
    // Analytics dashboard
    echo html_writer::start_div('analytics-dashboard');
    
    // Learning strengths
    echo html_writer::start_div('analytics-section');
    echo html_writer::tag('h4', get_string('strengths', 'local_aicompanion'));
    echo html_writer::start_div('strengths-container', array('id' => 'strengths-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    // Areas for improvement
    echo html_writer::start_div('analytics-section');
    echo html_writer::tag('h4', get_string('improvements', 'local_aicompanion'));
    echo html_writer::start_div('improvements-container', array('id' => 'improvements-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    // Recommendations
    echo html_writer::start_div('analytics-section');
    echo html_writer::tag('h4', get_string('recommendations', 'local_aicompanion'));
    echo html_writer::start_div('recommendations-container', array('id' => 'recommendations-container'));
    echo html_writer::end_div();
    echo html_writer::end_div();
    
    echo html_writer::end_div(); // analytics-dashboard
    echo html_writer::end_div(); // analytics tab
}

// Settings Tab
echo html_writer::start_div('tab-content', array('id' => 'settings'));
echo html_writer::tag('h3', get_string('settings_title', 'local_aicompanion'));
echo html_writer::tag('p', get_string('settings_subtitle', 'local_aicompanion'), array('class' => 'subtitle'));

// Settings form
echo html_writer::start_form('', 'post', array('id' => 'settings-form'));
echo html_writer::start_div('settings-container');

// AI Personality
echo html_writer::start_div('setting-group');
echo html_writer::tag('label', get_string('ai_personality', 'local_aicompanion'), array('for' => 'ai_personality'));
$personality_options = array(
    'friendly' => 'Friendly & Encouraging',
    'professional' => 'Professional & Direct',
    'casual' => 'Casual & Relaxed',
    'motivational' => 'Motivational & Inspiring'
);
echo html_writer::select($personality_options, 'ai_personality', 'friendly', false, array('id' => 'ai_personality'));
echo html_writer::end_div();

// Learning Style
echo html_writer::start_div('setting-group');
echo html_writer::tag('label', get_string('learning_style', 'local_aicompanion'), array('for' => 'learning_style'));
$style_options = array(
    'visual' => 'Visual Learner',
    'auditory' => 'Auditory Learner',
    'kinesthetic' => 'Kinesthetic Learner',
    'reading' => 'Reading/Writing Learner'
);
echo html_writer::select($style_options, 'learning_style', 'visual', false, array('id' => 'learning_style'));
echo html_writer::end_div();

// Difficulty Level
echo html_writer::start_div('setting-group');
echo html_writer::tag('label', get_string('difficulty_level', 'local_aicompanion'), array('for' => 'difficulty_level'));
$difficulty_options = array(
    'beginner' => 'Beginner',
    'intermediate' => 'Intermediate',
    'advanced' => 'Advanced',
    'expert' => 'Expert'
);
echo html_writer::select($difficulty_options, 'difficulty_level', 'intermediate', false, array('id' => 'difficulty_level'));
echo html_writer::end_div();

// Notifications
echo html_writer::start_div('setting-group');
echo html_writer::tag('label', get_string('notifications', 'local_aicompanion'), array('for' => 'notifications'));
echo html_writer::tag('input', '', array(
    'type' => 'checkbox',
    'id' => 'notifications',
    'name' => 'notifications',
    'value' => '1',
    'checked' => 'checked'
));
echo html_writer::end_div();

// Save button
echo html_writer::tag('button', get_string('save_settings', 'local_aicompanion'), array(
    'type' => 'submit',
    'class' => 'save-settings-btn'
));

echo html_writer::end_div(); // settings-container
echo html_writer::end_form();

echo html_writer::end_div(); // settings tab

// Add JavaScript for functionality
echo html_writer::script('
    // Initialize the AI Companion
    document.addEventListener("DOMContentLoaded", function() {
        initializeAICompanion();
    });
    
    // Global variables
    let chatHistory = [];
    let currentUser = ' . $userid . ';
    
    // Initialize the application
    function initializeAICompanion() {
        loadUserSettings();
        loadProgressData();
        loadAnalyticsData();
        setupEventListeners();
    }
    
    // Setup event listeners
    function setupEventListeners() {
        const chatInput = document.getElementById("chat-input");
        const sendButton = document.getElementById("send-button");
        
        if (chatInput) {
            chatInput.addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });
        }
        
        if (sendButton) {
            sendButton.addEventListener("click", sendMessage);
        }
        
        // Settings form
        const settingsForm = document.getElementById("settings-form");
        if (settingsForm) {
            settingsForm.addEventListener("submit", saveSettings);
        }
    }
    
    // Send message function
    function sendMessage() {
        const input = document.getElementById("chat-input");
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat(message, "user");
        input.value = "";
        
        // Show loading indicator
        showLoadingIndicator();
        
        // Send to AI service
        sendToAI(message);
    }
    
    // Send suggestion
    function sendSuggestion(suggestion) {
        document.getElementById("chat-input").value = suggestion;
        sendMessage();
    }
    
    // Add message to chat display
    function addMessageToChat(message, sender) {
        const chatMessages = document.getElementById("chat-messages");
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        contentDiv.textContent = message;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        chatHistory.push({message: message, sender: sender, timestamp: new Date()});
    }
    
    // Show loading indicator
    function showLoadingIndicator() {
        const chatMessages = document.getElementById("chat-messages");
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message ai-message loading";
        loadingDiv.id = "loading-message";
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        contentDiv.innerHTML = "<em>" + "' . get_string('ai_thinking', 'local_aicompanion') . '" + "</em>";
        
        loadingDiv.appendChild(contentDiv);
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Remove loading indicator
    function removeLoadingIndicator() {
        const loadingMessage = document.getElementById("loading-message");
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    // Send message to AI service
    function sendToAI(message) {
        // This would typically make an AJAX call to a PHP script that handles AI communication
        // For now, we\'ll simulate a response
        setTimeout(() => {
            removeLoadingIndicator();
            const response = generateAIResponse(message);
            addMessageToChat(response, "ai");
        }, 2000);
    }
    
    // Generate AI response (placeholder - would be replaced with actual AI integration)
    function generateAIResponse(message) {
        const responses = [
            "That\'s a great question! Let me help you understand that concept.",
            "I can see you\'re working on improving your learning. Here\'s what I suggest...",
            "Based on your learning style, I recommend focusing on...",
            "That\'s an interesting topic! Let me break it down for you.",
            "I understand you want to learn more about this. Here\'s a detailed explanation..."
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    // Clear chat
    function clearChat() {
        const chatMessages = document.getElementById("chat-messages");
        chatMessages.innerHTML = \'<div class="message ai-message"><div class="message-content">' . get_string('ai_greeting', 'local_aicompanion') . '</div></div>\';
        chatHistory = [];
    }
    
    // Load user settings
    function loadUserSettings() {
        // This would load settings from the database
        console.log("Loading user settings...");
    }
    
    // Save settings
    function saveSettings(e) {
        e.preventDefault();
        // This would save settings to the database
        alert("' . get_string('success_settings_saved', 'local_aicompanion') . '");
    }
    
    // Load progress data
    function loadProgressData() {
        // This would load progress data from Snowflake
        console.log("Loading progress data...");
    }
    
    // Load analytics data
    function loadAnalyticsData() {
        // This would load analytics data from Snowflake
        console.log("Loading analytics data...");
    }
');

echo $OUTPUT->footer();
