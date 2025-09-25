# 🤖 AI Learning Companion Plugin

## Overview

The AI Learning Companion is an innovative Moodle plugin designed to enhance the learning experience through personalized AI assistance. Built for the NatWest Hack4aCause hackathon, this plugin integrates with Snowflake and OpenAI to provide intelligent learning support, progress tracking, and analytics.

## 🚀 Features

### 🗣️ Intelligent Chat Assistant
- **Natural Language Processing**: Powered by OpenAI GPT models
- **Context-Aware Responses**: Maintains conversation context for better assistance
- **Personalized Interactions**: Adapts to user's learning style and preferences
- **Suggested Questions**: Pre-built prompts to help users get started

### 📊 Learning Progress Tracking
- **Goal Setting**: Set and track personal learning objectives
- **Achievement System**: Earn badges and recognition for milestones
- **Learning Statistics**: Visual representation of study time and progress
- **Course Completion Tracking**: Monitor progress across multiple courses

### 📈 Advanced Analytics
- **Learning Strengths**: Identify areas where the user excels
- **Improvement Areas**: Highlight opportunities for growth
- **Personalized Recommendations**: AI-generated suggestions based on learning patterns
- **Performance Insights**: Detailed analysis of learning effectiveness

### ⚙️ Customizable Settings
- **AI Personality**: Choose from friendly, professional, casual, or motivational
- **Learning Style**: Visual, auditory, kinesthetic, or reading/writing preferences
- **Difficulty Level**: Beginner, intermediate, advanced, or expert
- **Notification Preferences**: Control when and how you receive updates

## 🛠️ Technical Architecture

### Backend Technologies
- **PHP**: Core plugin development
- **Moodle**: Learning management system integration
- **Snowflake**: Data storage and analytics
- **OpenAI API**: AI-powered responses
- **MySQL**: Local data storage

### Frontend Technologies
- **HTML5/CSS3**: Modern, responsive interface
- **JavaScript (ES6+)**: Interactive functionality
- **AJAX**: Seamless server communication
- **Bootstrap-inspired**: Clean, professional design

### Database Schema
- `local_aicompanion_settings`: User preferences and configuration
- `local_aicompanion_chat_log`: Chat interaction history
- `local_aicompanion_goals`: Learning goals and objectives
- `local_aicompanion_interaction_log`: Analytics and usage data

## 📋 Installation

### Prerequisites
- Moodle 3.11 or higher
- PHP 7.4 or higher
- MySQL 5.7 or higher
- OpenAI API key
- Snowflake account (optional, for advanced analytics)

### Step 1: Download and Install
1. Download the plugin files
2. Extract to `moodle/local/aicompanion/`
3. Navigate to Site Administration → Notifications
4. Click "Upgrade Moodle database now"

### Step 2: Configure Settings
1. Go to Site Administration → Plugins → Local plugins → AI Learning Companion
2. Enter your OpenAI API key
3. Configure Snowflake connection (optional)
4. Enable desired features
5. Save settings

### Step 3: Set Permissions
1. Go to Site Administration → Users → Permissions → Define roles
2. Assign appropriate capabilities to user roles:
   - `local/aicompanion:view` - View the AI companion
   - `local/aicompanion:chat` - Use chat features
   - `local/aicompanion:analytics` - View analytics (teachers/managers)
   - `local/aicompanion:manage` - Manage plugin settings (managers only)

## 🔧 Configuration

### OpenAI Integration
```php
// In plugin settings
OpenAI API Key: your-api-key-here
AI Model: gpt-3.5-turbo (or gpt-4)
```

### Snowflake Integration (Optional)
```php
// In plugin settings
Snowflake Account: your-account.snowflakecomputing.com
Username: your-username
Password: your-password
Database: moodle_app
Schema: public
```

### Feature Toggles
- Enable Chat Feature: Yes/No
- Enable Progress Tracking: Yes/No
- Enable Analytics: Yes/No
- Maximum Chat History: 50 messages
- Response Delay: 2 seconds

## 📱 Usage

### For Students
1. **Access the Plugin**: Navigate to the AI Learning Companion from your dashboard
2. **Start Chatting**: Ask questions about your learning, get explanations, or request help
3. **Set Goals**: Create personal learning objectives and track your progress
4. **View Analytics**: See your learning patterns and get personalized recommendations
5. **Customize Settings**: Adjust the AI personality and learning preferences

### For Teachers
1. **Monitor Progress**: View student learning analytics and progress
2. **Provide Support**: Use insights to offer targeted assistance
3. **Track Engagement**: Monitor student interaction with the AI companion
4. **Generate Reports**: Export learning analytics for further analysis

### For Administrators
1. **Configure Settings**: Set up API keys and connection details
2. **Manage Permissions**: Control who can access different features
3. **Monitor Usage**: Track plugin usage and performance
4. **Update Configuration**: Modify settings as needed

## 🔒 Security & Privacy

### Data Protection
- All user data is stored securely in the Moodle database
- Chat logs are encrypted and can be purged as needed
- No personal data is shared with third parties without consent

### API Security
- OpenAI API keys are stored securely in Moodle configuration
- All API calls are made server-side to protect credentials
- Rate limiting prevents API abuse

### User Privacy
- Users can clear their chat history at any time
- Analytics data is anonymized where possible
- Settings are user-specific and private

## 🚀 Future Enhancements

### Planned Features
- **Multi-language Support**: Chat in multiple languages
- **Voice Integration**: Voice-to-text and text-to-speech capabilities
- **Advanced Analytics**: Machine learning-powered insights
- **Mobile App**: Dedicated mobile application
- **Integration APIs**: Connect with other learning tools

### AI Improvements
- **Custom Models**: Train models on specific course content
- **Emotion Recognition**: Detect and respond to user emotions
- **Predictive Analytics**: Anticipate learning needs
- **Adaptive Learning**: Automatically adjust difficulty and content

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow Moodle coding guidelines
- Use proper PHPDoc comments
- Write unit tests for new features
- Ensure accessibility compliance

## 📞 Support

### Documentation
- [Moodle Plugin Development Guide](https://docs.moodle.org/dev/Plugin_types)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Snowflake Documentation](https://docs.snowflake.com/)

### Troubleshooting
- Check Moodle error logs for issues
- Verify API key configuration
- Ensure proper permissions are set
- Test with different user roles

### Contact
- **GitHub Issues**: Report bugs and request features
- **Email**: [Your contact email]
- **Documentation**: [Link to detailed docs]

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NatWest Hack4aCause**: For organizing this amazing hackathon
- **Moodle Community**: For the excellent learning management system
- **OpenAI**: For providing powerful AI capabilities
- **Snowflake**: For robust data analytics platform
- **FINOS**: For supporting open-source financial technology

## 🏆 Hackathon Submission

### Team Information
- **Team Name**: [Your Team Name]
- **Project Title**: AI Learning Companion
- **Theme**: AI Companion for Learning and Development
- **Contact**: [Your Email]

### Key Innovations
1. **Personalized AI Tutoring**: Adaptive learning assistance based on individual needs
2. **Integrated Analytics**: Seamless data flow between Moodle and Snowflake
3. **Multi-modal Interface**: Chat, progress tracking, and analytics in one place
4. **Scalable Architecture**: Designed to handle large numbers of users

### Impact
- **Enhanced Learning**: Students get personalized, 24/7 learning support
- **Improved Engagement**: Interactive AI companion keeps learners motivated
- **Data-Driven Insights**: Teachers and administrators get valuable analytics
- **Accessibility**: Makes learning more accessible to diverse learners

---

**Built with ❤️ for the NatWest Hack4aCause Hackathon 2025**
