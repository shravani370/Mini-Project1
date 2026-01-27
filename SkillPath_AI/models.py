"""
SkillPath AI - Database Models
Personalized Career Development Platform
"""

import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'Shravani@2006'),
                database=os.getenv('DB_NAME', 'skillpath_ai'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            if self.connection.is_connected():
                print("✅ Connected to SkillPath AI MySQL database")
        except Error as e:
            print(f"⚠️ MySQL not available, using fallback data: {e}")
            self.connection = None

    def create_tables(self):
        """Create tables from schema"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        
        # Create tables (simplified version)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('learner', 'admin', 'mentor', 'industry_expert') DEFAULT 'learner',
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
        """)
        
        self.connection.commit()
        cursor.close()
        return True

    # ============ USER OPERATIONS ============
    
    def create_user(self, email, password_hash, role, first_name, last_name, phone=None):
        """Create new user"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (email, password_hash, role, first_name, last_name, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, password_hash, role, first_name, last_name, phone))
            self.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Error as e:
            print(f"❌ Error creating user: {e}")
            return None

    def get_user_by_email(self, email):
        """Get user by email"""
        # Return demo user if database is unavailable
        if not self.connection:
            if email == "learner1@edu.com":
                return {"id": 1, "email": "learner1@edu.com", "password_hash": "password", 
                       "role": "learner", "first_name": "Demo", "last_name": "Learner", "is_active": True}
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"⚠️ Database query error, using fallback: {e}")
            # Return demo user for testing
            if email == "learner1@edu.com":
                return {"id": 1, "email": "learner1@edu.com", "password_hash": "password", 
                       "role": "learner", "first_name": "Demo", "last_name": "Learner", "is_active": True}
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        # Return demo user if database is unavailable
        if not self.connection:
            if user_id == 1:
                return {"id": 1, "email": "learner1@edu.com", "password_hash": "password", 
                       "role": "learner", "first_name": "Demo", "last_name": "Learner", "is_active": True}
            return None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"⚠️ Database query error, using fallback: {e}")
            # Return demo user for testing
            if user_id == 1:
                return {"id": 1, "email": "learner1@edu.com", "password_hash": "password", 
                       "role": "learner", "first_name": "Demo", "last_name": "Learner", "is_active": True}
            return None

    # ============ LEARNER PROFILE ============
    
    def create_learner_profile(self, user_id, year, department, current_skills, target_skills, career_goal, experience_level='beginner'):
        """Create learner profile"""
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO learner_profiles (user_id, year, department, current_skills, target_skills, career_goal, experience_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, year, department, current_skills, target_skills, career_goal, experience_level))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating profile: {e}")
            return False

    def get_learner_by_user_id(self, user_id):
        """Get learner profile"""
        if not self.connection:
            return None
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM learner_profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()
        cursor.close()
        return profile

    # ============ SKILLS ============
    
    def get_all_skills(self):
        """Get all skills from database"""
        if not self.connection:
            return self.get_fallback_skills()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM skills ORDER BY category, name")
        skills = cursor.fetchall()
        cursor.close()
        return skills

    def get_skills_by_category(self, category):
        """Get skills by category"""
        if not self.connection:
            return []
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM skills WHERE category = %s", (category,))
        skills = cursor.fetchall()
        cursor.close()
        return skills

    def get_fallback_skills(self):
        """Fallback skills when database unavailable"""
        return [
            {"id": 1, "name": "Python Programming", "category": "programming", "difficulty": "beginner", "demand_score": 95},
            {"id": 2, "name": "Machine Learning", "category": "data_science", "difficulty": "intermediate", "demand_score": 90},
            {"id": 3, "name": "AWS Cloud", "category": "cloud", "difficulty": "intermediate", "demand_score": 88},
            {"id": 4, "name": "React.js", "category": "web", "difficulty": "intermediate", "demand_score": 85},
            {"id": 5, "name": "SQL & Databases", "category": "programming", "difficulty": "beginner", "demand_score": 92},
            {"id": 6, "name": "Docker & Containers", "category": "devops", "difficulty": "intermediate", "demand_score": 82},
        ]

    # ============ LEARNING PATHS ============
    
    def get_learning_paths(self, user_id):
        """Get learning paths for user"""
        if not self.connection:
            return []
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM learning_paths WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        paths = cursor.fetchall()
        cursor.close()
        return paths

    def create_learning_path(self, user_id, path_name, target_role, description, duration_weeks, difficulty):
        """Create new learning path"""
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO learning_paths (user_id, path_name, target_role, description, estimated_duration_weeks, difficulty_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, path_name, target_role, description, duration_weeks, difficulty))
            self.connection.commit()
            path_id = cursor.lastrowid
            cursor.close()
            return path_id
        except Error as e:
            print(f"❌ Error creating path: {e}")
            return None

    # ============ RESOURCES ============
    
    def get_resources(self, skill_id=None, limit=20):
        """Get learning resources"""
        if not self.connection:
            return self.get_fallback_resources()
        
        cursor = self.connection.cursor(dictionary=True)
        if skill_id:
            cursor.execute("SELECT * FROM resources WHERE skill_id = %s LIMIT %s", (skill_id, limit))
        else:
            cursor.execute("SELECT * FROM resources LIMIT %s", (limit,))
        
        resources = cursor.fetchall()
        cursor.close()
        return resources

    def get_fallback_resources(self):
        """Fallback resources"""
        return [
            {"id": 1, "title": "Python for Everybody", "type": "course", "duration_hours": 35, "difficulty": "beginner", "is_free": True, "rating": 4.8},
            {"id": 2, "title": "Machine Learning by Andrew Ng", "type": "course", "duration_hours": 50, "difficulty": "intermediate", "is_free": True, "rating": 4.9},
            {"id": 3, "title": "AWS Certified Solutions Architect", "type": "certification", "duration_hours": 40, "difficulty": "intermediate", "is_free": False, "rating": 4.6},
            {"id": 4, "title": "React - The Complete Guide", "type": "course", "duration_hours": 40, "difficulty": "intermediate", "is_free": False, "rating": 4.7},
            {"id": 5, "title": "SQL for Data Science", "type": "course", "duration_hours": 25, "difficulty": "beginner", "is_free": True, "rating": 4.5},
            {"id": 6, "title": "Docker Mastery", "type": "course", "duration_hours": 20, "difficulty": "intermediate", "is_free": False, "rating": 4.6},
        ]

    # ============ GOALS ============
    
    def get_goals(self, user_id):
        """Get user goals"""
        if not self.connection:
            return []
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM goals WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        goals = cursor.fetchall()
        cursor.close()
        return goals

    def create_goal(self, user_id, title, description, goal_type, target_date, priority='medium'):
        """Create new goal"""
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO goals (user_id, title, description, goal_type, target_date, priority)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, title, description, goal_type, target_date, priority))
            self.connection.commit()
            goal_id = cursor.lastrowid
            cursor.close()
            return goal_id
        except Error as e:
            print(f"❌ Error creating goal: {e}")
            return None

    # ============ INDUSTRY TRENDS ============
    
    def get_industry_trends(self, skill_id=None):
        """Get industry trends data"""
        if not self.connection:
            return self.get_fallback_trends()
        
        cursor = self.connection.cursor(dictionary=True)
        if skill_id:
            cursor.execute("SELECT * FROM industry_trends WHERE skill_id = %s", (skill_id,))
        else:
            cursor.execute("SELECT * FROM industry_trends ORDER BY demand_growth DESC LIMIT 10")
        
        trends = cursor.fetchall()
        cursor.close()
        return trends

    def get_fallback_trends(self):
        """Fallback trends"""
        return [
            {"skill_name": "Machine Learning", "demand_growth": 25.0, "avg_salary_min": 800000, "avg_salary_max": 2000000, "trend_direction": "rising"},
            {"skill_name": "AWS Cloud", "demand_growth": 18.0, "avg_salary_min": 600000, "avg_salary_max": 1500000, "trend_direction": "rising"},
            {"skill_name": "Python Programming", "demand_growth": 15.5, "avg_salary_min": 500000, "avg_salary_max": 1200000, "trend_direction": "rising"},
            {"skill_name": "React.js", "demand_growth": 12.0, "avg_salary_min": 500000, "avg_salary_max": 1000000, "trend_direction": "stable"},
            {"skill_name": "Docker & Containers", "demand_growth": 10.0, "avg_salary_min": 550000, "avg_salary_max": 1100000, "trend_direction": "stable"},
        ]

    # ============ USER SKILLS ============
    
    def get_user_skills(self, user_id):
        """Get user's skill proficiency"""
        if not self.connection:
            return []
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT us.*, s.name as skill_name, s.category, s.demand_score
            FROM user_skills us
            JOIN skills s ON us.skill_id = s.id
            WHERE us.user_id = %s
        """, (user_id,))
        skills = cursor.fetchall()
        cursor.close()
        return skills

    # ============ PROGRESS ============
    
    def get_user_progress(self, user_id):
        """Get user's learning progress"""
        if not self.connection:
            return {"total_hours": 45, "completed_resources": 8, "active_streak": 5}
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_progress WHERE user_id = %s", (user_id,))
        progress = cursor.fetchall()
        cursor.close()
        
        total_hours = sum(p['time_spent_minutes'] or 0 for p in progress) / 60
        completed = len([p for p in progress if p['status'] == 'completed'])
        
        return {
            "total_hours": round(total_hours, 1),
            "completed_resources": completed,
            "in_progress_resources": len([p for p in progress if p['status'] == 'in_progress'])
        }

    # ============ ADMIN STATS ============
    
    def get_admin_stats(self):
        """Get admin dashboard statistics"""
        if not self.connection:
            return {"total_learners": 250, "active_paths": 180, "resources_count": 150}
        
        stats = {}
        cursor = self.connection.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'learner'")
        stats['total_learners'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM learning_paths WHERE status = 'active'")
        stats['active_paths'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM resources")
        stats['resources_count'] = cursor.fetchone()['total']
        
        cursor.close()
        return stats

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")


# Global database instance
db = Database()
