"""
InterviewPro AI - Database Models
MySQL Database Interface for Interview Preparation Platform
"""

import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime


class Database:
    """Database connection and operations for InterviewPro AI"""
    
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
                database=os.getenv('DB_NAME', 'interviewpro_ai'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            if self.connection.is_connected():
                print("✅ Connected to InterviewPro AI MySQL database")
        except Error as e:
            print(f"⚠️ MySQL not available, using fallback data: {e}")
            self.connection = None

    def create_tables(self):
        """Create all tables from schema"""
        if not self.connection:
            return False

        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin', 'mentor') NOT NULL DEFAULT 'student',
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                user_id INT PRIMARY KEY,
                year INT NOT NULL,
                department VARCHAR(100),
                cgpa DECIMAL(3,2),
                target_role VARCHAR(100),
                experience_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
                total_interviews INT DEFAULT 0,
                avg_score DECIMAL(5,2) DEFAULT 0,
                total_score INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Question categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                icon VARCHAR(50),
                difficulty ENUM('easy', 'medium', 'hard', 'all') DEFAULT 'all',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_id INT NOT NULL,
                question_type ENUM('technical', 'behavioral', 'coding', 'system_design') NOT NULL,
                difficulty ENUM('easy', 'medium', 'hard') NOT NULL,
                question_text TEXT NOT NULL,
                ideal_answer TEXT,
                keywords TEXT,
                points INT DEFAULT 10,
                estimated_time INT DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES question_categories(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Interview sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                session_type ENUM('technical', 'behavioral', 'mixed', 'coding') NOT NULL DEFAULT 'mixed',
                difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
                target_role VARCHAR(100),
                questions_asked JSON,
                answers_given JSON,
                question_times JSON,
                total_score INT DEFAULT 0,
                max_score INT DEFAULT 100,
                percentage DECIMAL(5,2) DEFAULT 0,
                status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                question_id INT NOT NULL,
                answer_text TEXT,
                score DECIMAL(5,2) DEFAULT 0,
                max_score DECIMAL(5,2) DEFAULT 10,
                feedback TEXT,
                strengths TEXT,
                improvements TEXT,
                keywords_found TEXT,
                keywords_missing TEXT,
                evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                icon VARCHAR(50),
                category ENUM('interview', 'score', 'streak', 'milestone') NOT NULL,
                requirement_type VARCHAR(50),
                requirement_value INT,
                points INT DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # User achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                achievement_id INT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
                UNIQUE KEY unique_achievement (user_id, achievement_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        self.connection.commit()
        cursor.close()
        print("✅ All database tables created successfully")
        return True

    # ============ USER OPERATIONS ============
    
    def create_user(self, email, password_hash, role, first_name, last_name, phone=None):
        """Create a new user"""
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
            if email == "student1@edu.com":
                return {"id": 1, "email": "student1@edu.com", "password_hash": "password", 
                       "role": "student", "first_name": "Demo", "last_name": "Student", "is_active": True}
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
            if email == "student1@edu.com":
                return {"id": 1, "email": "student1@edu.com", "password_hash": "password", 
                       "role": "student", "first_name": "Demo", "last_name": "Student", "is_active": True}
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        # Return demo user if database is unavailable
        if not self.connection:
            if user_id == 1:
                return {"id": 1, "email": "student1@edu.com", "password_hash": "password", 
                       "role": "student", "first_name": "Demo", "last_name": "Student", "is_active": True}
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
                return {"id": 1, "email": "student1@edu.com", "password_hash": "password", 
                       "role": "student", "first_name": "Demo", "last_name": "Student", "is_active": True}
            return None

    # ============ STUDENT OPERATIONS ============
    
    def create_student(self, user_id, year, department, cgpa, target_role, experience_level='beginner'):
        """Create student profile"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO students (user_id, year, department, cgpa, target_role, experience_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, year, department, cgpa, target_role, experience_level))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error creating student: {e}")
            return False

    def get_student_by_user_id(self, user_id):
        """Get student profile by user ID"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        cursor.close()
        return student

    def update_student_stats(self, user_id, score):
        """Update student interview statistics"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE students 
                SET total_interviews = total_interviews + 1,
                    total_score = total_score + %s,
                    avg_score = (total_score + %s) / (total_interviews + 1)
                WHERE user_id = %s
            """, (score, score, user_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error updating student stats: {e}")
            return False

    def get_all_students(self):
        """Get all students"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students ORDER BY total_interviews DESC")
        students = cursor.fetchall()
        cursor.close()
        return students

    # ============ QUESTION OPERATIONS ============
    
    def get_question_categories(self):
        """Get all question categories"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM question_categories ORDER BY name")
        categories = cursor.fetchall()
        cursor.close()
        return categories

    def get_questions_by_category(self, category_id, limit=10, difficulty=None):
        """Get questions by category"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        if difficulty:
            cursor.execute("""
                SELECT * FROM questions 
                WHERE category_id = %s AND difficulty = %s AND is_active = TRUE
                ORDER BY RAND() LIMIT %s
            """, (category_id, difficulty, limit))
        else:
            cursor.execute("""
                SELECT * FROM questions 
                WHERE category_id = %s AND is_active = TRUE
                ORDER BY RAND() LIMIT %s
            """, (category_id, limit))
        
        questions = cursor.fetchall()
        cursor.close()
        return questions

    def get_random_questions(self, count=10, question_type=None, difficulty=None):
        """Get random questions for interview"""
        if not self.connection:
            return self.get_fallback_questions(count)
        
        cursor = self.connection.cursor(dictionary=True)
        
        query = "SELECT * FROM questions WHERE is_active = TRUE"
        params = []
        
        if question_type and question_type != 'mixed':
            query += " AND question_type = %s"
            params.append(question_type)
        
        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)
        
        query += " ORDER BY RAND() LIMIT %s"
        params.append(count)
        
        cursor.execute(query, tuple(params))
        questions = cursor.fetchall()
        cursor.close()
        
        if len(questions) < count:
            # Get more questions if not enough
            fallback = self.get_fallback_questions(count - len(questions))
            questions.extend(fallback)
        
        return questions

    def get_fallback_questions(self, count=10):
        """Fallback questions when database is not available"""
        return [
            {"id": 0, "question_type": "technical", "difficulty": "easy", 
             "question_text": "Tell me about yourself and your technical background.",
             "points": 10, "estimated_time": 3},
            {"id": 0, "question_type": "technical", "difficulty": "easy",
             "question_text": "What are your strengths and weaknesses as a developer?",
             "points": 10, "estimated_time": 5},
            {"id": 0, "question_type": "behavioral", "difficulty": "easy",
             "question_text": "Describe a challenging project you worked on.",
             "points": 15, "estimated_time": 8},
            {"id": 0, "question_type": "technical", "difficulty": "medium",
             "question_text": "Explain the concept of object-oriented programming.",
             "points": 15, "estimated_time": 8},
            {"id": 0, "question_type": "technical", "difficulty": "easy",
             "question_text": "What programming languages are you proficient in?",
             "points": 10, "estimated_time": 5},
        ][:count]

    def add_question(self, category_id, question_type, difficulty, question_text, 
                    ideal_answer=None, keywords=None, points=10, estimated_time=5):
        """Add new question to database"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO questions (category_id, question_type, difficulty, question_text, 
                                     ideal_answer, keywords, points, estimated_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (category_id, question_type, difficulty, question_text, ideal_answer, keywords, points, estimated_time))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error adding question: {e}")
            return False

    # ============ INTERVIEW SESSION OPERATIONS ============
    
    def create_interview_session(self, student_id, session_type, difficulty, target_role, questions):
        """Create new interview session"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO interview_sessions (student_id, session_type, difficulty, target_role, questions_asked)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, session_type, difficulty, target_role, str(questions)))
            self.connection.commit()
            session_id = cursor.lastrowid
            cursor.close()
            return session_id
        except Error as e:
            print(f"❌ Error creating session: {e}")
            return None

    def get_interview_session(self, session_id):
        """Get interview session by ID"""
        if not self.connection:
            return None
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM interview_sessions WHERE id = %s", (session_id,))
        session = cursor.fetchone()
        cursor.close()
        return session

    def update_interview_session(self, session_id, answers=None, score=None, completed=False):
        """Update interview session"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            if answers:
                cursor.execute("""
                    UPDATE interview_sessions SET answers_given = %s WHERE id = %s
                """, (str(answers), session_id))
            
            if score is not None:
                cursor.execute("""
                    UPDATE interview_sessions SET total_score = %s WHERE id = %s
                """, (score, session_id))
            
            if completed:
                cursor.execute("""
                    UPDATE interview_sessions 
                    SET status = 'completed', completed_at = NOW(),
                        percentage = (total_score / max_score) * 100
                    WHERE id = %s
                """, (session_id,))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error updating session: {e}")
            return False

    def get_student_sessions(self, student_id, limit=10):
        """Get interview sessions for a student"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM interview_sessions 
            WHERE student_id = %s 
            ORDER BY started_at DESC 
            LIMIT %s
        """, (student_id, limit))
        sessions = cursor.fetchall()
        cursor.close()
        return sessions

    # ============ EVALUATION OPERATIONS ============
    
    def save_evaluation(self, session_id, question_id, answer_text, score, feedback, 
                       strengths, improvements, keywords_found, keywords_missing):
        """Save AI evaluation"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO evaluations (session_id, question_id, answer_text, score, feedback,
                                       strengths, improvements, keywords_found, keywords_missing)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, question_id, answer_text, score, feedback, strengths, improvements, 
                  keywords_found, keywords_missing))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error saving evaluation: {e}")
            return False

    def get_session_evaluations(self, session_id):
        """Get all evaluations for a session"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.*, q.question_text, q.question_type, q.difficulty
            FROM evaluations e
            JOIN questions q ON e.question_id = q.id
            WHERE e.session_id = %s
            ORDER BY e.evaluated_at
        """, (session_id,))
        evaluations = cursor.fetchall()
        cursor.close()
        return evaluations

    # ============ ACHIEVEMENT OPERATIONS ============
    
    def get_all_achievements(self):
        """Get all achievements"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM achievements ORDER BY points")
        achievements = cursor.fetchall()
        cursor.close()
        return achievements

    def get_user_achievements(self, user_id):
        """Get achievements earned by user"""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, ua.earned_at 
            FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = %s
            ORDER BY ua.earned_at DESC
        """, (user_id,))
        achievements = cursor.fetchall()
        cursor.close()
        return achievements

    def award_achievement(self, user_id, achievement_id):
        """Award achievement to user"""
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT IGNORE INTO user_achievements (user_id, achievement_id)
                VALUES (%s, %s)
            """, (user_id, achievement_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error awarding achievement: {e}")
            return False

    def check_and_award_achievements(self, user_id):
        """Check conditions and award relevant achievements"""
        student = self.get_student_by_user_id(user_id)
        if not student:
            return []
        
        awarded = []
        achievements = self.get_all_achievements()
        
        for achievement in achievements:
            requirement_type = achievement['requirement_type']
            requirement_value = achievement['requirement_value']
            
            should_award = False
            
            if requirement_type == 'interviews_completed':
                should_award = student['total_interviews'] >= requirement_value
            elif requirement_type == 'single_score':
                should_award = student['total_score'] >= requirement_value
            elif requirement_type == 'avg_score':
                should_award = student['avg_score'] >= requirement_value
            
            if should_award:
                if self.award_achievement(user_id, achievement['id']):
                    awarded.append(achievement)
        
        return awarded

    # ============ ADMIN OPERATIONS ============
    
    def get_admin_stats(self):
        """Get admin dashboard statistics"""
        if not self.connection:
            return self.get_fallback_stats()
        
        stats = {}
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Total users
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'student'")
        stats['total_students'] = cursor.fetchone()['total']
        
        # Total interviews
        cursor.execute("SELECT COUNT(*) as total FROM interview_sessions WHERE status = 'completed'")
        stats['total_interviews'] = cursor.fetchone()['total']
        
        # Average score
        cursor.execute("SELECT AVG(percentage) as avg FROM interview_sessions WHERE status = 'completed'")
        stats['avg_score'] = cursor.fetchone()['avg'] or 0
        
        # Recent sessions
        cursor.execute("""
            SELECT COUNT(*) as total, DATE(started_at) as date 
            FROM interview_sessions 
            WHERE status = 'completed'
            GROUP BY DATE(started_at)
            ORDER BY date DESC LIMIT 7
        """)
        stats['weekly_activity'] = cursor.fetchall()
        
        cursor.close()
        return stats

    def get_fallback_stats(self):
        """Fallback statistics when database is not available"""
        return {
            'total_students': 150,
            'total_interviews': 500,
            'avg_score': 72.5,
            'weekly_activity': []
        }

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")


# Global database instance
db = Database()
