#!/usr/bin/env python3
"""
AI Learning Companion Microservice
Enhanced AI functionality using Python and advanced libraries
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'moodle_app')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'public')

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

class AILearningCompanion:
    """Main AI Learning Companion class"""
    
    def __init__(self):
        self.snowflake_conn = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.learning_patterns = {}
        
    def connect_snowflake(self):
        """Connect to Snowflake database"""
        try:
            self.snowflake_conn = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                account=SNOWFLAKE_ACCOUNT,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
            logger.info("Connected to Snowflake successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return False
    
    def get_ai_response(self, message: str, user_id: int, chat_history: List[Dict]) -> str:
        """Generate AI response using OpenAI"""
        try:
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(user_id)
                }
            ]
            
            # Add recent chat history
            for msg in chat_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": "user" if msg['sender'] == 'user' else "assistant",
                    "content": msg['message']
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    def _get_system_prompt(self, user_id: int) -> str:
        """Get personalized system prompt based on user data"""
        user_data = self.get_user_profile(user_id)
        
        base_prompt = """You are an AI Learning Companion designed to help students with their learning journey. 
        You are friendly, encouraging, and knowledgeable about educational topics. 
        Provide helpful, accurate, and personalized responses to help students learn effectively."""
        
        if user_data:
            learning_style = user_data.get('learning_style', 'visual')
            difficulty_level = user_data.get('difficulty_level', 'intermediate')
            
            if learning_style == 'visual':
                base_prompt += " This student learns best through visual aids, diagrams, and visual representations."
            elif learning_style == 'auditory':
                base_prompt += " This student learns best through listening, discussions, and verbal explanations."
            elif learning_style == 'kinesthetic':
                base_prompt += " This student learns best through hands-on activities and practical exercises."
            elif learning_style == 'reading':
                base_prompt += " This student learns best through reading, writing, and text-based materials."
            
            base_prompt += f" Adjust your explanations to a {difficulty_level} level."
        
        return base_prompt
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile from Snowflake"""
        if not self.snowflake_conn:
            return None
        
        try:
            cursor = self.snowflake_conn.cursor()
            query = """
                SELECT ai_personality, learning_style, difficulty_level, notifications
                FROM local_aicompanion_settings
                WHERE userid = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'ai_personality': result[0],
                    'learning_style': result[1],
                    'difficulty_level': result[2],
                    'notifications': result[3]
                }
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
        
        return None
    
    def analyze_learning_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's learning patterns using Snowflake data"""
        if not self.snowflake_conn:
            return self._get_mock_analytics()
        
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Get learning analytics
            query = """
                SELECT 
                    COUNT(DISTINCT course_id) as completed_courses,
                    SUM(study_time) as total_study_time,
                    AVG(quiz_score) as average_quiz_score,
                    COUNT(DISTINCT DATE(study_date)) as study_days,
                    AVG(engagement_score) as avg_engagement
                FROM learning_analytics 
                WHERE user_id = %s 
                AND study_date >= DATEADD(day, -30, CURRENT_DATE())
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'completed_courses': result[0] or 0,
                    'total_study_time': result[1] or 0,
                    'average_quiz_score': result[2] or 0,
                    'study_days': result[3] or 0,
                    'avg_engagement': result[4] or 0
                }
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
        
        return self._get_mock_analytics()
    
    def _get_mock_analytics(self) -> Dict[str, Any]:
        """Return mock analytics data for demonstration"""
        return {
            'completed_courses': 3,
            'total_study_time': 25.5,
            'average_quiz_score': 78.5,
            'study_days': 18,
            'avg_engagement': 0.75
        }
    
    def generate_learning_recommendations(self, user_id: int) -> List[str]:
        """Generate personalized learning recommendations"""
        analytics = self.analyze_learning_patterns(user_id)
        user_profile = self.get_user_profile(user_id)
        
        recommendations = []
        
        # Based on quiz scores
        if analytics['average_quiz_score'] < 70:
            recommendations.append("Focus on reviewing difficult concepts and taking practice quizzes")
        
        # Based on study consistency
        if analytics['study_days'] < 15:
            recommendations.append("Try to study more consistently - even 15 minutes daily helps")
        
        # Based on engagement
        if analytics['avg_engagement'] < 0.6:
            recommendations.append("Try interactive learning methods like group discussions or hands-on projects")
        
        # Based on learning style
        if user_profile:
            learning_style = user_profile.get('learning_style', 'visual')
            if learning_style == 'visual':
                recommendations.append("Create mind maps and visual summaries of key concepts")
            elif learning_style == 'auditory':
                recommendations.append("Listen to educational podcasts and participate in study groups")
            elif learning_style == 'kinesthetic':
                recommendations.append("Engage in hands-on projects and practical exercises")
            elif learning_style == 'reading':
                recommendations.append("Read comprehensive guides and create detailed written notes")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def track_learning_goal(self, user_id: int, goal_data: Dict) -> bool:
        """Track a learning goal"""
        if not self.snowflake_conn:
            return False
        
        try:
            cursor = self.snowflake_conn.cursor()
            query = """
                INSERT INTO local_aicompanion_goals 
                (userid, title, description, progress, target_date, status, timecreated, timemodified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            current_time = int(datetime.now().timestamp())
            cursor.execute(query, (
                user_id,
                goal_data['title'],
                goal_data['description'],
                goal_data.get('progress', 0),
                goal_data.get('target_date'),
                goal_data.get('status', 'active'),
                current_time,
                current_time
            ))
            
            self.snowflake_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error tracking learning goal: {e}")
            return False
    
    def log_interaction(self, user_id: int, action: str, data: Dict = None):
        """Log user interaction for analytics"""
        if not self.snowflake_conn:
            return
        
        try:
            cursor = self.snowflake_conn.cursor()
            query = """
                INSERT INTO local_aicompanion_interaction_log 
                (userid, action, data, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                user_id,
                action,
                json.dumps(data) if data else None,
                int(datetime.now().timestamp())
            ))
            
            self.snowflake_conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")

# Initialize AI companion
ai_companion = AILearningCompanion()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'snowflake_connected': ai_companion.snowflake_conn is not None
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id')
        chat_history = data.get('chat_history', [])
        
        if not message or not user_id:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Generate AI response
        response = ai_companion.get_ai_response(message, user_id, chat_history)
        
        # Log interaction
        ai_companion.log_interaction(user_id, 'chat', {
            'message': message,
            'response_length': len(response)
        })
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analytics/<int:user_id>', methods=['GET'])
def get_analytics(user_id):
    """Get user analytics"""
    try:
        analytics = ai_companion.analyze_learning_patterns(user_id)
        recommendations = ai_companion.generate_learning_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in analytics endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/goals', methods=['POST'])
def create_goal():
    """Create a learning goal"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        goal_data = data.get('goal')
        
        if not user_id or not goal_data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        success = ai_companion.track_learning_goal(user_id, goal_data)
        
        return jsonify({
            'success': success,
            'message': 'Goal created successfully' if success else 'Failed to create goal',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in create_goal endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized learning recommendations"""
    try:
        recommendations = ai_companion.generate_learning_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in recommendations endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Connect to Snowflake
    ai_companion.connect_snowflake()
    
    # Start the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
