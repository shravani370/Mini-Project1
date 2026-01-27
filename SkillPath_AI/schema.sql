-- =================================================================
-- SkillPath AI - Personalized Career Development Platform
-- MySQL Database Schema
-- =================================================================

CREATE DATABASE IF NOT EXISTS skillpath_ai;
USE skillpath_ai;

SET FOREIGN_KEY_CHECKS = 1;

-- Drop existing tables
DROP TABLE IF EXISTS user_goals;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS user_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS learning_paths;
DROP TABLE IF EXISTS user_progress;
DROP TABLE IF EXISTS industry_trends;
DROP TABLE IF EXISTS learner_profiles;
DROP TABLE IF EXISTS users;

-- =================================================================
-- USERS TABLE
-- =================================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('learner', 'admin', 'mentor', 'industry_expert') NOT NULL DEFAULT 'learner',
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
-- LEARNER PROFILES TABLE
-- =================================================================
CREATE TABLE learner_profiles (
    user_id INT PRIMARY KEY,
    year INT,
    department VARCHAR(100),
    current_skills TEXT,
    target_skills TEXT,
    career_goal VARCHAR(200),
    experience_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    learning_style ENUM('visual', 'reading', 'practical', 'mixed') DEFAULT 'mixed',
    weekly_hours DECIMAL(4,2) DEFAULT 10.0,
    streak_days INT DEFAULT 0,
    total_learning_hours DECIMAL(6,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- SKILLS DATABASE TABLE
-- =================================================================
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category ENUM('programming', 'data_science', 'cloud', 'web', 'mobile', 'devops', 'soft_skills', 'other') NOT NULL,
    description TEXT,
    difficulty ENUM('beginner', 'intermediate', 'advanced') NOT NULL,
    estimated_hours INT DEFAULT 40,
    prerequisites TEXT,
    resource_count INT DEFAULT 0,
    demand_score INT DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- USER SKILLS TABLE - Track skill proficiency
-- =================================================================
CREATE TABLE user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('novice', 'beginner', 'intermediate', 'advanced', 'expert') NOT NULL,
    self_assessment INT DEFAULT 1,
    verified_by_mentor BOOLEAN DEFAULT FALSE,
    last_practiced TIMESTAMP NULL,
    hours_invested DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY unique_skill (user_id, skill_id),
    INDEX idx_user (user_id),
    INDEX idx_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- LEARNING PATHS TABLE
-- =================================================================
CREATE TABLE learning_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    path_name VARCHAR(200) NOT NULL,
    target_role VARCHAR(200),
    description TEXT,
    estimated_duration_weeks INT,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    status ENUM('active', 'completed', 'paused', 'archived') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- RESOURCES TABLE - Learning materials
-- =================================================================
CREATE TABLE resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT,
    category_id INT,
    title VARCHAR(255) NOT NULL,
    type ENUM('course', 'tutorial', 'book', 'video', 'article', 'project', 'certification') NOT NULL,
    description TEXT,
    url VARCHAR(500),
    duration_hours DECIMAL(5,2),
    difficulty ENUM('beginner', 'intermediate', 'advanced'),
    is_free BOOLEAN DEFAULT TRUE,
    rating DECIMAL(2,1) DEFAULT 0,
    provider VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    INDEX idx_skill (skill_id),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- USER PROGRESS TABLE
-- =================================================================
CREATE TABLE user_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    learning_path_id INT,
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    time_spent_minutes INT DEFAULT 0,
    notes TEXT,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE SET NULL,
    UNIQUE KEY unique_progress (user_id, resource_id),
    INDEX idx_user (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- GOALS TABLE
-- =================================================================
CREATE TABLE goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    goal_type ENUM('daily', 'weekly', 'monthly', 'quarterly', 'yearly') NOT NULL,
    target_date DATE,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- USER GOALS PROGRESS TABLE
-- =================================================================
CREATE TABLE user_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT NOT NULL,
    user_id INT NOT NULL,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- INDUSTRY TRENDS TABLE
-- =================================================================
CREATE TABLE industry_trends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT,
    job_role VARCHAR(200),
    company_type ENUM('startup', 'product', 'service', 'faang', 'msme') NOT NULL,
    demand_growth DECIMAL(5,2),
    avg_salary_min DECIMAL(10,2),
    avg_salary_max DECIMAL(10,2),
    top_companies TEXT,
    trend_direction ENUM('rising', 'stable', 'declining') NOT NULL,
    data_source VARCHAR(100),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    INDEX idx_skill (skill_id),
    INDEX idx_trend (trend_direction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- INSERT SAMPLE DATA
-- =================================================================

-- Sample users
INSERT INTO users (email, password_hash, role, first_name, last_name, is_verified) VALUES
('admin@skillpath.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYn9qXwCqKKa', 'admin', 'System', 'Admin', TRUE),
('learner1@edu.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'learner', 'Amit', 'Sharma', TRUE),
('learner2@edu.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'learner', 'Priya', 'Gupta', TRUE);

-- Learner profiles
INSERT INTO learner_profiles (user_id, year, department, current_skills, target_skills, career_goal, experience_level, weekly_hours) VALUES
(2, 3, 'Computer Science', 'Python, HTML, CSS', 'Machine Learning, AWS', 'ML Engineer', 'intermediate', 15),
(3, 2, 'Information Technology', 'JavaScript, React', 'Node.js, Docker', 'Full Stack Developer', 'beginner', 10);

-- Skills database
INSERT INTO skills (name, category, description, difficulty, estimated_hours, demand_score) VALUES
('Python Programming', 'programming', 'Core Python programming language', 'beginner', 40, 95),
('Machine Learning', 'data_science', 'ML algorithms and applications', 'intermediate', 80, 90),
('AWS Cloud', 'cloud', 'Amazon Web Services', 'intermediate', 60, 88),
('React.js', 'web', 'Frontend JavaScript library', 'intermediate', 50, 85),
('SQL & Databases', 'programming', 'Database design and SQL queries', 'beginner', 35, 92),
('Docker & Containers', 'devops', 'Containerization technology', 'intermediate', 30, 82),
('Data Structures', 'programming', 'Core DSA concepts', 'beginner', 60, 88),
('System Design', 'programming', 'Scalable system architecture', 'advanced', 40, 75),
('Java Programming', 'programming', 'Core Java and advanced concepts', 'intermediate', 50, 80),
('Node.js', 'web', 'Backend JavaScript runtime', 'intermediate', 40, 78);

-- User skills
INSERT INTO user_skills (user_id, skill_id, proficiency_level, self_assessment, hours_invested) VALUES
(2, 1, 'intermediate', 7, 25),
(2, 5, 'beginner', 5, 15),
(3, 4, 'beginner', 4, 20);

-- Resources
INSERT INTO resources (skill_id, title, type, description, duration_hours, difficulty, is_free, provider, rating) VALUES
(1, 'Python for Everybody', 'course', 'Full Python course on Coursera', 35, 'beginner', TRUE, 'Coursera', 4.8),
(1, 'Automate the Boring Stuff', 'book', 'Practical Python programming', 20, 'beginner', TRUE, 'Free', 4.7),
(2, 'Machine Learning by Andrew Ng', 'course', 'Foundational ML course', 50, 'intermediate', TRUE, 'Coursera', 4.9),
(3, 'AWS Certified Solutions Architect', 'certification', 'AWS certification preparation', 40, 'intermediate', FALSE, 'AWS', 4.6),
(4, 'React - The Complete Guide', 'course', 'Complete React.js learning', 40, 'intermediate', FALSE, 'Udemy', 4.7),
(5, 'SQL for Data Science', 'course', 'SQL for data analysis', 25, 'beginner', TRUE, 'Coursera', 4.5);

-- Learning paths
INSERT INTO learning_paths (user_id, path_name, target_role, description, estimated_duration_weeks, difficulty_level, progress_percentage) VALUES
(2, 'ML Engineer Path', 'Machine Learning Engineer', 'Complete path to become an ML Engineer', 24, 'intermediate', 35),
(3, 'Full Stack Developer', 'Full Stack Developer', 'Web development from scratch', 16, 'beginner', 60);

-- Goals
INSERT INTO goals (user_id, title, description, goal_type, target_date, status, priority) VALUES
(2, 'Complete Python Course', 'Finish Python for Everybody course', 'weekly', '2024-02-15', 'in_progress', 'high'),
(2, 'Learn Pandas', 'Master Pandas library for data manipulation', 'monthly', '2024-03-01', 'pending', 'medium'),
(3, 'Build React App', 'Create a portfolio website using React', 'monthly', '2024-02-28', 'in_progress', 'high');

-- Industry trends
INSERT INTO industry_trends (skill_id, job_role, company_type, demand_growth, avg_salary_min, avg_salary_max, top_companies, trend_direction) VALUES
(1, 'Python Developer', 'startup', 15.5, 500000, 1200000, 'Google, Facebook, Amazon', 'rising'),
(2, 'ML Engineer', 'product', 25.0, 800000, 2000000, 'Google, Microsoft, Apple', 'rising'),
(3, 'Cloud Engineer', 'service', 18.0, 600000, 1500000, 'TCS, Infosys, Wipro', 'rising'),
(4, 'Frontend Developer', 'startup', 12.0, 500000, 1000000, 'Paytm, Flipkart, Ola', 'stable');

SELECT '✅ SkillPath AI Database schema created!' as status;
