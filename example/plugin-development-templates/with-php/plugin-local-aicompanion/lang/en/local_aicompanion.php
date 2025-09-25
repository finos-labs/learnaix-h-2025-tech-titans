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
 * Language strings for AI Companion plugin
 *
 * @package    local_aicompanion
 * @copyright  2025 NatWest Hack4aCause
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$string['pluginname'] = 'AI Learning Companion';
$string['aicompanion'] = 'AI Companion';
$string['privacy:metadata'] = 'The AI Companion plugin does not store any personal data.';

// Navigation and UI
$string['nav_title'] = 'AI Learning Companion';
$string['welcome_message'] = 'Welcome to your AI Learning Companion! I\'m here to help you with your learning journey.';
$string['chat_placeholder'] = 'Ask me anything about your learning...';
$string['send_button'] = 'Send';
$string['clear_chat'] = 'Clear Chat';
$string['loading'] = 'Thinking...';

// Features
$string['chat_tab'] = 'Chat Assistant';
$string['progress_tab'] = 'Learning Progress';
$string['analytics_tab'] = 'Analytics';
$string['settings_tab'] = 'Settings';

// Chat features
$string['chat_title'] = 'AI Learning Assistant';
$string['chat_subtitle'] = 'Ask questions, get explanations, and receive personalized learning guidance';
$string['suggested_questions'] = 'Suggested Questions:';
$string['suggested_q1'] = 'What should I study next?';
$string['suggested_q2'] = 'Explain this concept in simple terms';
$string['suggested_q3'] = 'How can I improve my learning?';
$string['suggested_q4'] = 'What are my learning goals?';

// Progress tracking
$string['progress_title'] = 'Learning Progress';
$string['progress_subtitle'] = 'Track your learning journey and achievements';
$string['current_goals'] = 'Current Learning Goals';
$string['achievements'] = 'Achievements';
$string['learning_time'] = 'Learning Time This Week';
$string['completed_courses'] = 'Completed Courses';
$string['in_progress'] = 'In Progress';
$string['not_started'] = 'Not Started';

// Analytics
$string['analytics_title'] = 'Learning Analytics';
$string['analytics_subtitle'] = 'Insights into your learning patterns and performance';
$string['strengths'] = 'Learning Strengths';
$string['improvements'] = 'Areas for Improvement';
$string['learning_patterns'] = 'Learning Patterns';
$string['recommendations'] = 'Personalized Recommendations';

// Settings
$string['settings_title'] = 'AI Companion Settings';
$string['settings_subtitle'] = 'Customize your AI learning experience';
$string['ai_personality'] = 'AI Personality';
$string['learning_style'] = 'Learning Style';
$string['difficulty_level'] = 'Difficulty Level';
$string['notifications'] = 'Notifications';
$string['save_settings'] = 'Save Settings';

// Error messages
$string['error_api_key'] = 'API key not configured. Please contact your administrator.';
$string['error_connection'] = 'Unable to connect to AI service. Please try again later.';
$string['error_permission'] = 'You do not have permission to access this feature.';
$string['error_general'] = 'An error occurred. Please try again.';

// Success messages
$string['success_settings_saved'] = 'Settings saved successfully!';
$string['success_goal_set'] = 'Learning goal set successfully!';

// AI Responses
$string['ai_greeting'] = 'Hello! I\'m your AI Learning Companion. How can I help you learn today?';
$string['ai_thinking'] = 'Let me think about that...';
$string['ai_processing'] = 'Processing your request...';

// Settings
$string['ai_config'] = 'AI Service Configuration';
$string['ai_config_desc'] = 'Configure the AI service settings for the learning companion';
$string['openai_api_key'] = 'OpenAI API Key';
$string['openai_api_key_desc'] = 'Enter your OpenAI API key for AI functionality';
$string['ai_model'] = 'AI Model';
$string['ai_model_desc'] = 'Select the AI model to use for responses';
$string['service_base_url'] = 'AI Service Base URL';
$string['service_base_url_desc'] = 'Optional: External AI service base URL (e.g., http://localhost:5000). If set, plugin will call this service.';
$string['snowflake_config'] = 'Snowflake Configuration';
$string['snowflake_config_desc'] = 'Configure Snowflake database connection settings';
$string['snowflake_account'] = 'Snowflake Account';
$string['snowflake_account_desc'] = 'Your Snowflake account identifier';
$string['snowflake_username'] = 'Snowflake Username';
$string['snowflake_username_desc'] = 'Username for Snowflake connection';
$string['snowflake_password'] = 'Snowflake Password';
$string['snowflake_password_desc'] = 'Password for Snowflake connection';
$string['snowflake_database'] = 'Snowflake Database';
$string['snowflake_database_desc'] = 'Database name in Snowflake';
$string['snowflake_schema'] = 'Snowflake Schema';
$string['snowflake_schema_desc'] = 'Schema name in Snowflake';
$string['feature_config'] = 'Feature Configuration';
$string['feature_config_desc'] = 'Enable or disable specific features';
$string['enable_chat'] = 'Enable Chat Feature';
$string['enable_chat_desc'] = 'Allow users to chat with the AI companion';
$string['enable_progress'] = 'Enable Progress Tracking';
$string['enable_progress_desc'] = 'Track and display learning progress';
$string['enable_analytics'] = 'Enable Analytics';
$string['enable_analytics_desc'] = 'Provide learning analytics and insights';
$string['max_chat_history'] = 'Maximum Chat History';
$string['max_chat_history_desc'] = 'Maximum number of chat messages to store per user';
$string['response_delay'] = 'Response Delay (seconds)';
$string['response_delay_desc'] = 'Delay before showing AI response (for better UX)';
