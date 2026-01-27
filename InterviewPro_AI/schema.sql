-- =================================================================
-- InterviewPro AI - Technical Interview Training Platform
-- MySQL Database Schema
-- =================================================================

-- Create database
CREATE DATABASE IF NOT EXISTS interviewpro_ai;
USE interviewpro_ai;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- =================================================================
-- DROP EXISTING TABLES
-- =================================================================
DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS evaluations;
DROP TABLE IF EXISTS interview_sessions;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS question_categories;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

-- =================================================================
-- USERS TABLE - Central authentication
-- =================================================================
CREATE TABLE users (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- STUDENTS TABLE - Student profiles
-- =================================================================
CREATE TABLE students (
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
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_target_role (target_role),
    INDEX idx_experience (experience_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- QUESTION CATEGORIES TABLE - Topic categories
-- =================================================================
CREATE TABLE question_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    difficulty ENUM('easy', 'medium', 'hard', 'all') DEFAULT 'all',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- QUESTIONS TABLE - Question bank
-- =================================================================
CREATE TABLE questions (
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
    
    FOREIGN KEY (category_id) REFERENCES question_categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id),
    INDEX idx_type (question_type),
    INDEX idx_difficulty (difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- INTERVIEW SESSIONS TABLE - Session tracking
-- =================================================================
CREATE TABLE interview_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    session_type ENUM('technical', 'behavioral', 'mixed', 'coding') NOT NULL DEFAULT 'mixed',
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    target_role VARCHAR(100),
    
    -- Session data stored as JSON
    questions_asked JSON,
    answers_given JSON,
    question_times JSON,
    
    -- Scoring
    total_score INT DEFAULT 0,
    max_score INT DEFAULT 100,
    percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Status
    status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_status (status),
    INDEX idx_completed_at (completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- EVALUATIONS TABLE - AI evaluations
-- =================================================================
CREATE TABLE evaluations (
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
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- ACHIEVEMENTS TABLE - Gamification badges
-- =================================================================
CREATE TABLE achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    category ENUM('interview', 'score', 'streak', 'milestone') NOT NULL,
    requirement_type VARCHAR(50),
    requirement_value INT,
    points INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- USER ACHIEVEMENTS TABLE - User badges
-- =================================================================
CREATE TABLE user_achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    achievement_id INT NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE KEY unique_achievement (user_id, achievement_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- INSERT SAMPLE DATA
-- =================================================================

-- Insert sample admin
INSERT INTO users (email, password_hash, role, first_name, last_name, phone, is_verified) 
VALUES ('admin@interviewpro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYn9qXwCqKKa', 'admin', 'System', 'Admin', '9876543210', TRUE);

-- Insert sample students
INSERT INTO users (email, password_hash, role, first_name, last_name, phone, is_verified) 
VALUES 
('student1@edu.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'John', 'Doe', '1234567890', TRUE),
('student2@edu.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Jane', 'Smith', '0987654321', TRUE);

INSERT INTO students (user_id, year, department, cgpa, target_role, experience_level, total_interviews, avg_score) VALUES
(2, 3, 'Computer Science', 8.5, 'SDE', 'intermediate', 5, 72.5),
(3, 2, 'Information Technology', 8.8, 'Data Scientist', 'beginner', 2, 65.0);

-- Insert question categories
INSERT INTO question_categories (name, description, icon, difficulty) VALUES
('Data Structures', 'Questions about arrays, linked lists, trees, graphs, etc.', '📊', 'all'),
('Algorithms', 'Sorting, searching, dynamic programming, greedy algorithms', '🧮', 'all'),
('Object-Oriented Programming', 'Classes, inheritance, polymorphism, design patterns', '🏗️', 'all'),
('Database', 'SQL, normalization, indexing, transactions', '🗄️', 'all'),
('System Design', 'Scalability, distributed systems, architecture', '🔧', 'all'),
('Behavioral', 'HR questions, situational answers, soft skills', '💬', 'all'),
('Web Technologies', 'HTML, CSS, JavaScript, frameworks', '🌐', 'all'),
('Machine Learning', 'ML concepts, models, evaluation', '🤖', 'all');

-- Insert sample questions
INSERT INTO questions (category_id, question_type, difficulty, question_text, ideal_answer, keywords, points, estimated_time) VALUES
(1, 'technical', 'easy', 'What is the difference between an array and a linked list?', 'Arrays have fixed size and random access, while linked lists are dynamic and use pointers. Arrays provide O(1) access, linked lists provide O(1) insertion/deletion at head.', 'array,linked list,pointer,dynamic,access', 10, 5),
(1, 'technical', 'medium', 'Explain the different types of binary trees.', 'Full binary tree: every node has 0 or 2 children. Complete binary tree: all levels filled except last. Perfect binary tree: all internal nodes have 2 children and all leaves are at same level.', 'full,complete,perfect,binary tree,levels', 15, 8),
(2, 'technical', 'easy', 'What is the time complexity of binary search?', 'O(log n) - the search space halves with each comparison.', 'log n,halves,comparison', 10, 3),
(2, 'coding', 'medium', 'Write a function to find the nth Fibonacci number using dynamic programming.', 'Use bottom-up approach with O(n) time and O(1) space. Store only last two values.', 'fibonacci,dynamic programming,O(n),optimization', 20, 15),
(3, 'technical', 'easy', 'What are the four pillars of OOP?', 'Encapsulation, Inheritance, Polymorphism, and Abstraction.', 'encapsulation,inheritance,polymorphism,abstraction', 10, 5),
(3, 'technical', 'medium', 'Explain the difference between method overloading and method overriding.', 'Overloading: same class, same method name, different parameters. Overriding: subclass provides specific implementation of method already defined in parent class.', 'overloading,overriding,inheritance,polymorphism', 15, 8),
(4, 'technical', 'easy', 'What is a primary key?', 'A column or set of columns that uniquely identifies each row in a table. It cannot be NULL and must be unique.', 'unique,null,identifier', 10, 3),
(4, 'technical', 'medium', 'Explain the difference between INNER JOIN and LEFT JOIN.', 'INNER JOIN returns only matching rows from both tables. LEFT JOIN returns all rows from left table and matching rows from right table.', 'inner join,left join,matching,rows', 15, 8),
(5, 'system_design', 'hard', 'Design a URL shortening service like bit.ly.', 'Consider: API design, database schema (hash vs auto-increment), collision handling, scaling with sharding, caching with Redis, analytics tracking.', 'api,database,hash,sharding,caching,analytics', 30, 20),
(6, 'behavioral', 'easy', 'Tell me about yourself.', 'Brief introduction covering education, interests, and career goals. Relate to the position applied for.', 'introduction,education,goals,relevant', 10, 3),
(6, 'behavioral', 'medium', 'Describe a challenging project you worked on and how you overcame obstacles.', 'Use STAR method: Situation, Task, Action, Result. Focus on problem-solving and learning.', 'star method,challenge,problem-solving,result', 15, 8),
(7, 'technical', 'easy', 'What is the difference between GET and POST methods?', 'GET requests data (parameters in URL), POST sends data (parameters in body). GET is idempotent, POST is not. GET is for reading, POST for creating.', 'get,post,idempotent,url,body', 10, 5),
(8, 'technical', 'medium', 'Explain the bias-variance tradeoff.', 'High bias causes underfitting (misses patterns), high variance causes overfitting (captures noise). Goal is to find optimal complexity that minimizes total error.', 'bias,variance,underfitting,overfitting,error', 15, 10);

-- Insert achievements
INSERT INTO achievements (name, description, icon, category, requirement_type, requirement_value, points) VALUES
('First Interview', 'Completed your first mock interview', '🎯', 'milestone', 'interviews_completed', 1, 10),
('Warm Up', 'Completed 5 mock interviews', '🔥', 'streak', 'interviews_completed', 5, 25),
('Interview Pro', 'Completed 20 mock interviews', '⭐', 'milestone', 'interviews_completed', 20, 50),
('High Scorer', 'Scored above 80% in an interview', '🏆', 'score', 'single_score', 80, 30),
('Perfectionist', 'Scored 100% in an interview', '💯', 'score', 'single_score', 100, 100),
('Consistent', 'Maintained average above 70%', '📈', 'score', 'avg_score', 70, 40),
('Coding Champion', 'Completed 10 coding challenges', '💻', 'milestone', 'coding_challenges', 10, 35),
('System Design Expert', 'Completed 5 system design interviews', '🔧', 'milestone', 'system_design', 5, 45);

-- =================================================================
-- VERIFICATION QUERIES
-- =================================================================
SELECT 'Tables created:' as status;
SHOW TABLES;

SELECT 'Question categories inserted:' as status;
SELECT id, name, difficulty FROM question_categories;

SELECT 'Sample questions inserted:' as status;
SELECT id, question_type, difficulty, LEFT(question_text, 50) as preview FROM questions LIMIT 5;

SELECT 'Achievements created:' as status;
SELECT id, name, points FROM achievements;

SELECT 'Database setup complete!' as status;
