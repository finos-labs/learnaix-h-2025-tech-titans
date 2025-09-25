# 🚀 AI Learning Companion - Installation Guide

## Prerequisites

### System Requirements
- **Moodle**: Version 3.11 or higher
- **PHP**: Version 7.4 or higher
- **MySQL**: Version 5.7 or higher
- **Python**: Version 3.9 or higher (for microservice)
- **Memory**: Minimum 2GB RAM
- **Storage**: At least 1GB free space

### Required Accounts
- **OpenAI Account**: For AI functionality
- **Snowflake Account**: For advanced analytics (optional)
- **Moodle Admin Access**: To install and configure the plugin

## Installation Methods

### Method 1: Quick Installation (Recommended)

#### Step 1: Download Plugin
```bash
# Clone or download the plugin files
git clone [repository-url]
# Or download the ZIP file and extract it
```

#### Step 2: Install in Moodle
1. Copy the `aicompanion` folder to `moodle/local/`
2. Navigate to **Site Administration → Notifications**
3. Click **"Upgrade Moodle database now"**
4. Wait for the installation to complete

#### Step 3: Configure Settings
1. Go to **Site Administration → Plugins → Local plugins → AI Learning Companion**
2. Enter your OpenAI API key
3. Configure other settings as needed
4. Click **"Save changes"**

### Method 2: Advanced Installation with Python Microservice

#### Step 1: Install Moodle Plugin
Follow Method 1 steps 1-3.

#### Step 2: Set Up Python Microservice
```bash
# Navigate to the python directory
cd moodle/local/aicompanion/python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SNOWFLAKE_ACCOUNT="your-account.snowflakecomputing.com"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_DATABASE="moodle_app"
export SNOWFLAKE_SCHEMA="public"

# Run the service
python ai_service.py
```

#### Step 3: Docker Installation (Alternative)
```bash
# Build the Docker image
docker build -t ai-companion-service .

# Run the container
docker run -d \
  --name ai-companion \
  -p 5000:5000 \
  -e OPENAI_API_KEY="your-api-key" \
  -e SNOWFLAKE_ACCOUNT="your-account" \
  -e SNOWFLAKE_USER="your-username" \
  -e SNOWFLAKE_PASSWORD="your-password" \
  ai-companion-service
```

## Configuration

### 1. OpenAI Configuration

#### Get API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key (it won't be shown again)

#### Configure in Moodle
1. Go to **Site Administration → Plugins → Local plugins → AI Learning Companion**
2. Paste your API key in the **OpenAI API Key** field
3. Select your preferred AI model:
   - **GPT-3.5 Turbo**: Faster, more cost-effective
   - **GPT-4**: More advanced, higher cost
   - **GPT-4 Turbo**: Latest model with improved performance

### 2. Snowflake Configuration (Optional)

#### Set Up Snowflake Account
1. Sign up for [Snowflake](https://www.snowflake.com/)
2. Create a new database for Moodle data
3. Note your account identifier, username, and password

#### Configure in Moodle
1. Go to **Site Administration → Plugins → Local plugins → AI Learning Companion**
2. Enter your Snowflake details:
   - **Account**: `your-account.snowflakecomputing.com`
   - **Username**: Your Snowflake username
   - **Password**: Your Snowflake password
   - **Database**: `moodle_app` (or your preferred name)
   - **Schema**: `public` (or your preferred schema)

#### Create Snowflake Tables
```sql
-- Run these commands in Snowflake SQL editor

-- Learning analytics table
CREATE TABLE learning_analytics (
    user_id INT,
    course_id INT,
    study_time FLOAT,
    quiz_score FLOAT,
    engagement_score FLOAT,
    study_date DATE
);

-- Course progress table
CREATE TABLE course_progress (
    user_id INT,
    course_id INT,
    course_name VARCHAR(255),
    progress_percentage INT,
    last_accessed TIMESTAMP,
    completion_status VARCHAR(50)
);

-- User settings table
CREATE TABLE local_aicompanion_settings (
    userid INT,
    ai_personality VARCHAR(50),
    learning_style VARCHAR(50),
    difficulty_level VARCHAR(50),
    notifications INT
);
```

### 3. Feature Configuration

#### Enable/Disable Features
1. Go to **Site Administration → Plugins → Local plugins → AI Learning Companion**
2. Toggle the following features:
   - **Enable Chat Feature**: Allow users to chat with AI
   - **Enable Progress Tracking**: Track learning progress
   - **Enable Analytics**: Provide learning analytics

#### Advanced Settings
- **Maximum Chat History**: Number of messages to store per user (default: 50)
- **Response Delay**: Delay before showing AI response in seconds (default: 2)

## User Permissions

### Set Up Capabilities
1. Go to **Site Administration → Users → Permissions → Define roles**
2. Edit the appropriate role (e.g., Student, Teacher)
3. Find **AI Learning Companion** capabilities:
   - **local/aicompanion:view**: View the AI companion
   - **local/aicompanion:chat**: Use chat features
   - **local/aicompanion:analytics**: View analytics (teachers only)
   - **local/aicompanion:manage**: Manage settings (managers only)

### Recommended Permission Setup
- **Students**: `view`, `chat`
- **Teachers**: `view`, `chat`, `analytics`
- **Managers**: All capabilities

## Testing the Installation

### 1. Basic Functionality Test
1. Log in as a student
2. Navigate to the AI Learning Companion
3. Try sending a message in the chat
4. Check if you receive an AI response

### 2. Settings Test
1. Go to the Settings tab
2. Change your AI personality
3. Save settings
4. Verify changes are saved

### 3. Progress Tracking Test
1. Go to the Progress tab
2. Check if learning goals are displayed
3. Verify statistics are shown

### 4. Analytics Test (Teachers/Managers)
1. Log in as a teacher or manager
2. Go to the Analytics tab
3. Check if learning insights are displayed

## Troubleshooting

### Common Issues

#### 1. Plugin Not Appearing
**Problem**: Plugin doesn't show up in Moodle
**Solution**: 
- Check file permissions
- Ensure all files are in the correct directory
- Run database upgrade again

#### 2. OpenAI API Errors
**Problem**: Chat not working, API errors
**Solution**:
- Verify API key is correct
- Check API key has sufficient credits
- Ensure internet connection is working

#### 3. Snowflake Connection Issues
**Problem**: Analytics not loading
**Solution**:
- Verify Snowflake credentials
- Check network connectivity
- Ensure tables are created correctly

#### 4. Permission Denied Errors
**Problem**: Users can't access features
**Solution**:
- Check user capabilities
- Verify role assignments
- Review permission settings

### Debug Mode
Enable debug mode for detailed error messages:
1. Go to **Site Administration → Development → Debugging**
2. Enable **Debug messages**
3. Set **Debug level** to **DEVELOPER**
4. Check error logs in `moodledata/error.log`

### Log Files
- **Moodle Logs**: `moodledata/error.log`
- **Plugin Logs**: Check Moodle admin interface
- **Python Service Logs**: Console output or log files

## Performance Optimization

### 1. Caching
- Enable Moodle caching
- Use Redis or Memcached for better performance

### 2. Database Optimization
- Regular database maintenance
- Index optimization for large datasets

### 3. API Rate Limiting
- Monitor OpenAI API usage
- Implement rate limiting if needed

### 4. Memory Management
- Increase PHP memory limit if needed
- Monitor server resources

## Security Considerations

### 1. API Key Security
- Store API keys securely
- Use environment variables in production
- Regularly rotate API keys

### 2. Data Privacy
- Review data collection practices
- Implement data retention policies
- Ensure GDPR compliance

### 3. Access Control
- Regular permission audits
- Monitor user access patterns
- Implement session timeouts

## Support and Maintenance

### Regular Maintenance
- Update plugin regularly
- Monitor error logs
- Backup data regularly
- Test functionality after updates

### Getting Help
- Check the README.md file
- Review error logs
- Contact support team
- Check GitHub issues

### Updates
- Subscribe to plugin updates
- Test updates in staging environment
- Follow update procedures carefully

## Uninstallation

### Remove Plugin
1. Go to **Site Administration → Plugins → Plugins overview**
2. Find **AI Learning Companion**
3. Click **Uninstall**
4. Confirm uninstallation

### Clean Up Data
1. Remove plugin files from `moodle/local/aicompanion/`
2. Clean up database tables (optional)
3. Remove Python service (if installed)

---

**Need Help?** Check the troubleshooting section or contact support!
