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
 * AJAX handler for AI Companion plugin
 *
 * @package    local_aicompanion
 * @copyright  2025 NatWest Hack4aCause
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');
require_once($CFG->libdir.'/adminlib.php');
require_once($CFG->dirroot.'/local/aicompanion/lib.php');

// Set content type to JSON
header('Content-Type: application/json');

// Check if user is logged in
require_login();

// Check capabilities
$context = context_system::instance();
require_capability('local/aicompanion:view', $context);

// Get action from request
$action = optional_param('action', '', PARAM_TEXT);

// Initialize response
$response = array(
    'success' => false,
    'message' => '',
    'data' => null
);

try {
    switch ($action) {
        case 'chat':
            $response = handleChatRequest();
            break;
            
        case 'get_settings':
            $response = handleGetSettingsRequest();
            break;
            
        case 'save_settings':
            $response = handleSaveSettingsRequest();
            break;
            
        case 'get_progress':
            $response = handleGetProgressRequest();
            break;
            
        case 'get_analytics':
            $response = handleGetAnalyticsRequest();
            break;
            
        default:
            $response['message'] = 'Invalid action';
            break;
    }
} catch (Exception $e) {
    $response['message'] = 'An error occurred: ' . $e->getMessage();
    error_log('AI Companion Error: ' . $e->getMessage());
}

// Output JSON response
echo json_encode($response);
exit;

/**
 * Handle chat requests
 */
function handleChatRequest() {
    global $USER;
    
    $message = required_param('message', PARAM_TEXT);
    $user_id = required_param('user_id', PARAM_INT);
    $chat_history = optional_param('chat_history', '[]', PARAM_TEXT);
    
    // Validate user
    if ($user_id != $USER->id) {
        return array(
            'success' => false,
            'message' => 'Invalid user',
            'response' => ''
        );
    }
    
    // Get AI response
    $ai_response = getAIResponse($message, $chat_history);
    
    // Log the interaction
    logChatInteraction($user_id, $message, $ai_response);
    
    return array(
        'success' => true,
        'message' => 'Chat processed successfully',
        'response' => $ai_response
    );
}

/**
 * Handle get settings requests
 */
function handleGetSettingsRequest() {
    global $USER, $DB;
    
    $user_id = required_param('user_id', PARAM_INT);
    
    // Validate user
    if ($user_id != $USER->id) {
        return array(
            'success' => false,
            'message' => 'Invalid user',
            'settings' => null
        );
    }
    
    // Get user settings from database
    $settings = $DB->get_record('local_aicompanion_settings', array('userid' => $user_id));
    
    if (!$settings) {
        // Return default settings
        $settings = (object) array(
            'ai_personality' => 'friendly',
            'learning_style' => 'visual',
            'difficulty_level' => 'intermediate',
            'notifications' => 1
        );
    }
    
    return array(
        'success' => true,
        'message' => 'Settings retrieved successfully',
        'settings' => $settings
    );
}

/**
 * Handle save settings requests
 */
function handleSaveSettingsRequest() {
    global $USER, $DB;
    
    $user_id = required_param('user_id', PARAM_INT);
    $ai_personality = required_param('ai_personality', PARAM_TEXT);
    $learning_style = required_param('learning_style', PARAM_TEXT);
    $difficulty_level = required_param('difficulty_level', PARAM_TEXT);
    $notifications = required_param('notifications', PARAM_INT);
    
    // Validate user
    if ($user_id != $USER->id) {
        return array(
            'success' => false,
            'message' => 'Invalid user'
        );
    }
    
    // Prepare settings data
    $settings_data = array(
        'userid' => $user_id,
        'ai_personality' => $ai_personality,
        'learning_style' => $learning_style,
        'difficulty_level' => $difficulty_level,
        'notifications' => $notifications,
        'timemodified' => time()
    );
    
    // Check if settings exist
    $existing = $DB->get_record('local_aicompanion_settings', array('userid' => $user_id));
    
    if ($existing) {
        $settings_data['id'] = $existing->id;
        $result = $DB->update_record('local_aicompanion_settings', $settings_data);
    } else {
        $result = $DB->insert_record('local_aicompanion_settings', $settings_data);
    }
    
    if ($result) {
        return array(
            'success' => true,
            'message' => 'Settings saved successfully'
        );
    } else {
        return array(
            'success' => false,
            'message' => 'Failed to save settings'
        );
    }
}

/**
 * Handle get progress requests
 */
function handleGetProgressRequest() {
    global $USER;
    
    $user_id = required_param('user_id', PARAM_INT);
    
    // Validate user
    if ($user_id != $USER->id) {
        return array(
            'success' => false,
            'message' => 'Invalid user',
            'progress' => null
        );
    }
    
    // Get progress data (this would typically come from Snowflake)
    $progress = getProgressData($user_id);
    
    return array(
        'success' => true,
        'message' => 'Progress data retrieved successfully',
        'progress' => $progress
    );
}

/**
 * Handle get analytics requests
 */
function handleGetAnalyticsRequest() {
    global $USER;
    
    $user_id = required_param('user_id', PARAM_INT);
    
    // Validate user
    if ($user_id != $USER->id) {
        return array(
            'success' => false,
            'message' => 'Invalid user',
            'analytics' => null
        );
    }
    
    // Get analytics data (this would typically come from Snowflake)
    $analytics = getAnalyticsData($user_id);
    
    return array(
        'success' => true,
        'message' => 'Analytics data retrieved successfully',
        'analytics' => $analytics
    );
}

/**
 * Get AI response for a message
 */
function getAIResponse($message, $chat_history) {
    // Prefer external AI service if configured, else fallback to OpenAI direct call
    $service_base = trim(get_config('local_aicompanion', 'service_base_url'));
    if (!empty($service_base)) {
        $endpoint = rtrim($service_base, '/') . '/chat';
        $payload = array(
            'message' => $message,
            'user_id' => (int) optional_param('user_id', 0, PARAM_INT),
            'chat_history' => json_decode($chat_history, true)
        );
        $response = callExternalAIService($endpoint, $payload);
        if (!empty($response)) {
            return $response;
        }
        // If external fails, continue to OpenAI fallback
    }

    // OpenAI fallback
    $api_key = get_config('local_aicompanion', 'openai_api_key');
    $model = get_config('local_aicompanion', 'ai_model');
    if (empty($api_key)) {
        return "I'm sorry, but the AI service is not properly configured. Please contact your administrator.";
    }
    
    // Parse chat history
    $history = json_decode($chat_history, true);
    if (!is_array($history)) {
        $history = array();
    }
    
    // Prepare messages for OpenAI
    $messages = array();
    
    // Add system message
    $messages[] = array(
        'role' => 'system',
        'content' => "You are an AI Learning Companion designed to help students with their learning journey. You are friendly, encouraging, and knowledgeable about educational topics. Provide helpful, accurate, and personalized responses to help students learn effectively."
    );
    
    // Add chat history (last 10 messages to stay within token limits)
    $recent_history = array_slice($history, -10);
    foreach ($recent_history as $msg) {
        $messages[] = array(
            'role' => $msg['sender'] === 'user' ? 'user' : 'assistant',
            'content' => $msg['message']
        );
    }
    
    // Add current message
    $messages[] = array(
        'role' => 'user',
        'content' => $message
    );
    
    // Call OpenAI API
    $response = callOpenAI($api_key, $model, $messages);
    
    return $response;
}

/**
 * Call external AI Flask service
 */
function callExternalAIService($endpoint, $payload) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $endpoint);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 20);
    $result = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($http_code === 200) {
        $decoded = json_decode($result, true);
        if (isset($decoded['response'])) {
            return $decoded['response'];
        }
    }
    return null;
}

/**
 * Call OpenAI API
 */
function callOpenAI($api_key, $model, $messages) {
    $url = 'https://api.openai.com/v1/chat/completions';
    
    $data = array(
        'model' => $model,
        'messages' => $messages,
        'max_tokens' => 500,
        'temperature' => 0.7
    );
    
    $headers = array(
        'Content-Type: application/json',
        'Authorization: Bearer ' . $api_key
    );
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http_code !== 200) {
        error_log('OpenAI API Error: HTTP ' . $http_code . ' - ' . $response);
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later.";
    }
    
    $result = json_decode($response, true);
    
    if (isset($result['choices'][0]['message']['content'])) {
        return $result['choices'][0]['message']['content'];
    } else {
        error_log('OpenAI API Error: ' . $response);
        return "I'm sorry, I couldn't generate a proper response. Please try rephrasing your question.";
    }
}

/**
 * Log chat interaction
 */
function logChatInteraction($user_id, $user_message, $ai_response) {
    global $DB;
    
    $log_data = array(
        'userid' => $user_id,
        'user_message' => $user_message,
        'ai_response' => $ai_response,
        'timestamp' => time()
    );
    
    $DB->insert_record('local_aicompanion_chat_log', $log_data);
}

/**
 * Get progress data for user
 */
function getProgressData($user_id) {
    // This would typically query Snowflake for real data
    // For now, return mock data
    return array(
        'goals' => array(
            array(
                'title' => 'Complete Python Course',
                'progress' => 75,
                'description' => 'Learn Python programming fundamentals'
            ),
            array(
                'title' => 'Read 5 Books This Month',
                'progress' => 40,
                'description' => 'Expand knowledge through reading'
            )
        ),
        'achievements' => array(
            array(
                'title' => 'First Course Completed',
                'description' => 'Completed your first online course',
                'date' => '2025-01-15'
            ),
            array(
                'title' => 'Week Streak',
                'description' => 'Studied for 7 consecutive days',
                'date' => '2025-01-20'
            )
        ),
        'stats' => array(
            'learning_time' => '12.5',
            'completed_courses' => '3',
            'current_streak' => '5'
        )
    );
}

/**
 * Get analytics data for user
 */
function getAnalyticsData($user_id) {
    // This would typically query Snowflake for real data
    // For now, return mock data
    return array(
        'strengths' => array(
            'Strong in problem-solving',
            'Excellent time management',
            'Good at visual learning'
        ),
        'improvements' => array(
            'Focus on practical applications',
            'Try different learning methods',
            'Increase study consistency'
        ),
        'recommendations' => array(
            'Try hands-on coding exercises',
            'Join study groups for collaboration',
            'Set daily learning goals'
        )
    );
}
