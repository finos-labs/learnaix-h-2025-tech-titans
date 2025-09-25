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
 * Settings for AI Companion plugin
 *
 * @package    local_aicompanion
 * @copyright  2025 NatWest Hack4aCause
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage('local_aicompanion', get_string('pluginname', 'local_aicompanion'));
    
    if ($ADMIN->fulltree) {
        
        // AI Service Configuration
        $settings->add(new admin_setting_heading('local_aicompanion/ai_config', 
            get_string('ai_config', 'local_aicompanion'), 
            get_string('ai_config_desc', 'local_aicompanion')));
        
        // OpenAI API Key
        $settings->add(new admin_setting_configtext('local_aicompanion/openai_api_key',
            get_string('openai_api_key', 'local_aicompanion'),
            get_string('openai_api_key_desc', 'local_aicompanion'),
            '', PARAM_TEXT));
        
        // AI Model Selection
        $options = array(
            'gpt-3.5-turbo' => 'GPT-3.5 Turbo',
            'gpt-4' => 'GPT-4',
            'gpt-4-turbo' => 'GPT-4 Turbo'
        );
        $settings->add(new admin_setting_configselect('local_aicompanion/ai_model',
            get_string('ai_model', 'local_aicompanion'),
            get_string('ai_model_desc', 'local_aicompanion'),
            'gpt-3.5-turbo', $options));

        // External AI Service URL (optional)
        $settings->add(new admin_setting_configtext('local_aicompanion/service_base_url',
            get_string('service_base_url', 'local_aicompanion'),
            get_string('service_base_url_desc', 'local_aicompanion'),
            '', PARAM_URL));
        
        // Snowflake Configuration
        $settings->add(new admin_setting_heading('local_aicompanion/snowflake_config', 
            get_string('snowflake_config', 'local_aicompanion'), 
            get_string('snowflake_config_desc', 'local_aicompanion')));
        
        // Snowflake Account
        $settings->add(new admin_setting_configtext('local_aicompanion/snowflake_account',
            get_string('snowflake_account', 'local_aicompanion'),
            get_string('snowflake_account_desc', 'local_aicompanion'),
            '', PARAM_TEXT));
        
        // Snowflake Username
        $settings->add(new admin_setting_configtext('local_aicompanion/snowflake_username',
            get_string('snowflake_username', 'local_aicompanion'),
            get_string('snowflake_username_desc', 'local_aicompanion'),
            '', PARAM_TEXT));
        
        // Snowflake Password
        $settings->add(new admin_setting_configpasswordunmask('local_aicompanion/snowflake_password',
            get_string('snowflake_password', 'local_aicompanion'),
            get_string('snowflake_password_desc', 'local_aicompanion'),
            ''));
        
        // Snowflake Database
        $settings->add(new admin_setting_configtext('local_aicompanion/snowflake_database',
            get_string('snowflake_database', 'local_aicompanion'),
            get_string('snowflake_database_desc', 'local_aicompanion'),
            'moodle_app', PARAM_TEXT));
        
        // Snowflake Schema
        $settings->add(new admin_setting_configtext('local_aicompanion/snowflake_schema',
            get_string('snowflake_schema', 'local_aicompanion'),
            get_string('snowflake_schema_desc', 'local_aicompanion'),
            'public', PARAM_TEXT));
        
        // Feature Settings
        $settings->add(new admin_setting_heading('local_aicompanion/feature_config', 
            get_string('feature_config', 'local_aicompanion'), 
            get_string('feature_config_desc', 'local_aicompanion')));
        
        // Enable Chat Feature
        $settings->add(new admin_setting_configcheckbox('local_aicompanion/enable_chat',
            get_string('enable_chat', 'local_aicompanion'),
            get_string('enable_chat_desc', 'local_aicompanion'),
            1));
        
        // Enable Progress Tracking
        $settings->add(new admin_setting_configcheckbox('local_aicompanion/enable_progress',
            get_string('enable_progress', 'local_aicompanion'),
            get_string('enable_progress_desc', 'local_aicompanion'),
            1));
        
        // Enable Analytics
        $settings->add(new admin_setting_configcheckbox('local_aicompanion/enable_analytics',
            get_string('enable_analytics', 'local_aicompanion'),
            get_string('enable_analytics_desc', 'local_aicompanion'),
            1));
        
        // Max Chat History
        $settings->add(new admin_setting_configtext('local_aicompanion/max_chat_history',
            get_string('max_chat_history', 'local_aicompanion'),
            get_string('max_chat_history_desc', 'local_aicompanion'),
            '50', PARAM_INT));
        
        // AI Response Delay (for better UX)
        $settings->add(new admin_setting_configtext('local_aicompanion/response_delay',
            get_string('response_delay', 'local_aicompanion'),
            get_string('response_delay_desc', 'local_aicompanion'),
            '2', PARAM_INT));
    }
    
    $ADMIN->add('localplugins', $settings);
}
