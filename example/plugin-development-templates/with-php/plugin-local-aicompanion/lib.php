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
 * Library functions for AI Companion plugin
 *
 * @package    local_aicompanion
 * @copyright  2025 NatWest Hack4aCause
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Get Snowflake connection
 */
function get_snowflake_connection() {
    global $CFG;
    
    $account = get_config('local_aicompanion', 'snowflake_account');
    $username = get_config('local_aicompanion', 'snowflake_username');
    $password = get_config('local_aicompanion', 'snowflake_password');
    $database = get_config('local_aicompanion', 'snowflake_database');
    $schema = get_config('local_aicompanion', 'snowflake_schema');
    
    if (empty($account) || empty($username) || empty($password)) {
        return false;
    }
    
    try {
        $dsn = "snowflake:account={$account};database={$database};schema={$schema}";
        $pdo = new PDO($dsn, $username, $password);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch (PDOException $e) {
        error_log('Snowflake connection error: ' . $e->getMessage());
        return false;
    }
}

/**
 * Create database tables for the plugin
 */
function local_aicompanion_install() {
    global $DB;
    
    $dbman = $DB->get_manager();
    
    // Define table for user settings
    $table = new xmldb_table('local_aicompanion_settings');
    $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
    $table->add_field('userid', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_field('ai_personality', XMLDB_TYPE_CHAR, '50', null, null, null, 'friendly');
    $table->add_field('learning_style', XMLDB_TYPE_CHAR, '50', null, null, null, 'visual');
    $table->add_field('difficulty_level', XMLDB_TYPE_CHAR, '50', null, null, null, 'intermediate');
    $table->add_field('notifications', XMLDB_TYPE_INTEGER, '1', null, null, null, '1');
    $table->add_field('timecreated', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_field('timemodified', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_key('primary', XMLDB_KEY_PRIMARY, array('id'));
    $table->add_key('userid', XMLDB_KEY_UNIQUE, array('userid'));
    $table->add_index('userid_idx', XMLDB_INDEX_NOTUNIQUE, array('userid'));
    
    if (!$dbman->table_exists($table)) {
        $dbman->create_table($table);
    }
    
    // Define table for chat logs
    $table = new xmldb_table('local_aicompanion_chat_log');
    $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
    $table->add_field('userid', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_field('user_message', XMLDB_TYPE_TEXT, null, null, null, null, null);
    $table->add_field('ai_response', XMLDB_TYPE_TEXT, null, null, null, null, null);
    $table->add_field('timestamp', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_key('primary', XMLDB_KEY_PRIMARY, array('id'));
    $table->add_index('userid_idx', XMLDB_INDEX_NOTUNIQUE, array('userid'));
    $table->add_index('timestamp_idx', XMLDB_INDEX_NOTUNIQUE, array('timestamp'));
    
    if (!$dbman->table_exists($table)) {
        $dbman->create_table($table);
    }
    
    // Define table for learning goals
    $table = new xmldb_table('local_aicompanion_goals');
    $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
    $table->add_field('userid', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_field('title', XMLDB_TYPE_CHAR, '255', null, XMLDB_NOTNULL, null, null);
    $table->add_field('description', XMLDB_TYPE_TEXT, null, null, null, null, null);
    $table->add_field('progress', XMLDB_TYPE_INTEGER, '3', null, null, null, '0');
    $table->add_field('target_date', XMLDB_TYPE_INTEGER, '10', null, null, null, null);
    $table->add_field('status', XMLDB_TYPE_CHAR, '20', null, null, null, 'active');
    $table->add_field('timecreated', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_field('timemodified', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
    $table->add_key('primary', XMLDB_KEY_PRIMARY, array('id'));
    $table->add_index('userid_idx', XMLDB_INDEX_NOTUNIQUE, array('userid'));
    $table->add_index('status_idx', XMLDB_INDEX_NOTUNIQUE, array('status'));
    
    if (!$dbman->table_exists($table)) {
        $dbman->create_table($table);
    }
    
    return true;
}

/**
 * Uninstall the plugin
 */
function local_aicompanion_uninstall() {
    global $DB;
    
    $dbman = $DB->get_manager();
    
    // Drop tables
    $tables = array(
        'local_aicompanion_settings',
        'local_aicompanion_chat_log',
        'local_aicompanion_goals'
    );
    
    foreach ($tables as $table_name) {
        $table = new xmldb_table($table_name);
        if ($dbman->table_exists($table)) {
            $dbman->drop_table($table);
        }
    }
    
    return true;
}

/**
 * Get user learning analytics from Snowflake
 */
function get_user_analytics($userid) {
    $pdo = get_snowflake_connection();
    if (!$pdo) {
        return false;
    }
    
    try {
        // Query user learning data from Snowflake
        $sql = "SELECT 
                    COUNT(DISTINCT course_id) as completed_courses,
                    SUM(study_time) as total_study_time,
                    AVG(quiz_score) as average_quiz_score,
                    COUNT(DISTINCT DATE(study_date)) as study_days
                FROM learning_analytics 
                WHERE user_id = :userid 
                AND study_date >= DATEADD(day, -30, CURRENT_DATE())";
        
        $stmt = $pdo->prepare($sql);
        $stmt->bindParam(':userid', $userid, PDO::PARAM_INT);
        $stmt->execute();
        
        return $stmt->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        error_log('Snowflake analytics query error: ' . $e->getMessage());
        return false;
    }
}

/**
 * Get user learning progress from Snowflake
 */
function get_user_progress($userid) {
    $pdo = get_snowflake_connection();
    if (!$pdo) {
        return false;
    }
    
    try {
        // Query user progress data from Snowflake
        $sql = "SELECT 
                    course_id,
                    course_name,
                    progress_percentage,
                    last_accessed,
                    completion_status
                FROM course_progress 
                WHERE user_id = :userid 
                ORDER BY last_accessed DESC";
        
        $stmt = $pdo->prepare($sql);
        $stmt->bindParam(':userid', $userid, PDO::PARAM_INT);
        $stmt->execute();
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        error_log('Snowflake progress query error: ' . $e->getMessage());
        return false;
    }
}

/**
 * Generate AI-powered learning recommendations
 */
function generate_learning_recommendations($userid, $learning_style = 'visual') {
    $analytics = get_user_analytics($userid);
    $progress = get_user_progress($userid);
    
    if (!$analytics || !$progress) {
        return array(
            'error' => 'Unable to generate recommendations at this time.'
        );
    }
    
    $recommendations = array();
    
    // Based on learning style
    switch ($learning_style) {
        case 'visual':
            $recommendations[] = 'Try using mind maps and diagrams to organize your learning';
            $recommendations[] = 'Watch video tutorials and create visual summaries';
            break;
        case 'auditory':
            $recommendations[] = 'Listen to educational podcasts and audio books';
            $recommendations[] = 'Join study groups for discussions and verbal explanations';
            break;
        case 'kinesthetic':
            $recommendations[] = 'Engage in hands-on projects and practical exercises';
            $recommendations[] = 'Take frequent breaks and move around while studying';
            break;
        case 'reading':
            $recommendations[] = 'Read comprehensive guides and take detailed notes';
            $recommendations[] = 'Create written summaries and flashcards';
            break;
    }
    
    // Based on performance
    if ($analytics['average_quiz_score'] < 70) {
        $recommendations[] = 'Focus on reviewing difficult concepts and taking practice quizzes';
    }
    
    if ($analytics['study_days'] < 15) {
        $recommendations[] = 'Try to study more consistently - even 15 minutes daily helps';
    }
    
    // Based on progress
    $incomplete_courses = array_filter($progress, function($course) {
        return $course['completion_status'] !== 'completed';
    });
    
    if (count($incomplete_courses) > 3) {
        $recommendations[] = 'Consider focusing on fewer courses at a time for better progress';
    }
    
    return $recommendations;
}

/**
 * Log user interaction for analytics
 */
function log_user_interaction($userid, $action, $data = null) {
    global $DB;
    
    $log_entry = new stdClass();
    $log_entry->userid = $userid;
    $log_entry->action = $action;
    $log_entry->data = $data ? json_encode($data) : null;
    $log_entry->timestamp = time();
    
    return $DB->insert_record('local_aicompanion_interaction_log', $log_entry);
}

/**
 * Get AI personality based on user settings
 */
function get_ai_personality($userid) {
    global $DB;
    
    $settings = $DB->get_record('local_aicompanion_settings', array('userid' => $userid));
    
    if (!$settings) {
        return 'friendly';
    }
    
    return $settings->ai_personality;
}

/**
 * Format AI response based on personality
 */
function format_ai_response($response, $personality = 'friendly') {
    switch ($personality) {
        case 'professional':
            return $response; // Keep as is
        case 'casual':
            return str_replace(['Hello', 'Thank you', 'Please'], ['Hey', 'Thanks', 'Could you'], $response);
        case 'motivational':
            $response = "💪 " . $response;
            if (strpos($response, '!') === false) {
                $response .= " You've got this!";
            }
            return $response;
        case 'friendly':
        default:
            $response = "😊 " . $response;
            return $response;
    }
}

/**
 * Check if AI service is available
 */
function is_ai_service_available() {
    $api_key = get_config('local_aicompanion', 'openai_api_key');
    return !empty($api_key);
}

/**
 * Get plugin configuration summary
 */
function get_plugin_config_summary() {
    $config = array(
        'ai_enabled' => is_ai_service_available(),
        'snowflake_connected' => get_snowflake_connection() !== false,
        'features' => array(
            'chat' => get_config('local_aicompanion', 'enable_chat'),
            'progress' => get_config('local_aicompanion', 'enable_progress'),
            'analytics' => get_config('local_aicompanion', 'enable_analytics')
        )
    );
    
    return $config;
}
