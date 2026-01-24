-- =================================================================
-- AI-Driven Training and Placement System - MySQL Database Schema
-- =================================================================
-- Run this script in MySQL Workbench or via command line:
-- mysql -u root -p < schema.sql
-- =================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS ai_training_platform;
USE ai_training_platform;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- =================================================================
-- DROP EXISTING TABLES (in reverse order of dependencies)
-- =================================================================
DROP TABLE IF EXISTS verification_codes;
DROP TABLE IF EXISTS training_recommendations;
DROP TABLE IF EXISTS placements;
DROP TABLE IF EXISTS interview_sessions;
DROP TABLE IF EXISTS recruiter_profiles;
DROP TABLE IF EXISTS admin_profiles;
DROP TABLE IF EXISTS student_profiles;
DROP TABLE IF EXISTS users;

-- =================================================================
-- MAIN USERS TABLE - Central authentication and user management
-- =================================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Authentication fields
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- Stores hashed password (never plain text)
    role ENUM('student', 'admin', 'recruiter') NOT NULL DEFAULT 'student',
    
    -- Common fields for all users
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    
    -- Status and verification
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    -- Indexes for performance
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- STUDENT PROFILES TABLE - Additional student-specific data
-- =================================================================
CREATE TABLE student_profiles (
    user_id INT PRIMARY KEY,
    enrollment_number VARCHAR(50) UNIQUE,
    year INT NOT NULL,
    department VARCHAR(100),
    cgpa DECIMAL(3,2),
    skills TEXT,  -- Comma-separated skills
    interests VARCHAR(255),
    resume_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    total_score INT DEFAULT 0,
    interview_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_year (year),
    INDEX idx_cgpa (cgpa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- RECRUITER PROFILES TABLE - Additional recruiter-specific data
-- =================================================================
CREATE TABLE recruiter_profiles (
    user_id INT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    company_website VARCHAR(200),
    company_size ENUM('startup', 'small', 'medium', 'large', 'enterprise'),
    industry VARCHAR(100),
    job_positions VARCHAR(255),
    required_skills TEXT,
    company_description TEXT,
    company_logo_url VARCHAR(500),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_company_name (company_name),
    INDEX idx_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- ADMIN PROFILES TABLE - Additional admin-specific data
-- =================================================================
CREATE TABLE admin_profiles (
    user_id INT PRIMARY KEY,
    admin_level ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin',
    permissions TEXT,
    department VARCHAR(100),
    employee_id VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- INTERVIEW SESSIONS TABLE - AI Interview tracking
-- =================================================================
CREATE TABLE interview_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    interview_type ENUM('technical', 'behavioral', 'mixed', 'mock') NOT NULL DEFAULT 'mixed',
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    
    -- AI Generated Questions
    questions JSON,
    answers JSON,
    
    -- Evaluation
    score INT DEFAULT 0,
    max_score INT DEFAULT 100,
    feedback TEXT,
    strengths TEXT,
    areas_for_improvement TEXT,
    
    -- Status
    status ENUM('in_progress', 'completed', 'cancelled') DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_completed_at (completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- PLACEMENTS TABLE - Job placement tracking
-- =================================================================
CREATE TABLE placements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    recruiter_id INT,
    company_name VARCHAR(200) NOT NULL,
    job_role VARCHAR(200) NOT NULL,
    salary DECIMAL(12,2),
    location VARCHAR(200),
    employment_type ENUM('full_time', 'part_time', 'internship', 'contract') DEFAULT 'full_time',
    
    -- Timeline
    application_date DATE,
    interview_date DATE,
    offer_date DATE,
    joining_date DATE,
    
    -- Status
    status ENUM('applied', 'screening', 'interviewing', 'offered', 'accepted', 'rejected', 'withdrawn') DEFAULT 'applied',
    
    -- Notes
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_status (status),
    INDEX idx_company_name (company_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- TRAINING RECOMMENDATIONS TABLE - AI-generated training paths
-- =================================================================
CREATE TABLE training_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_area VARCHAR(100) NOT NULL,
    recommendation_type ENUM('course', 'project', 'certification', 'practice', 'resource') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_url VARCHAR(500),
    estimated_duration_hours INT,
    priority ENUM('high', 'medium', 'low') DEFAULT 'medium',
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_skill_area (skill_area),
    INDEX idx_priority (priority),
    INDEX idx_is_completed (is_completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- VERIFICATION CODES TABLE - OTP/Email verification
-- =================================================================
CREATE TABLE verification_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code VARCHAR(10) NOT NULL,
    code_type ENUM('email', 'phone', 'password_reset') NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_code (code),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =================================================================
-- SAMPLE DATA - For testing purposes
-- =================================================================

-- Insert sample admin (password: admin123)
INSERT INTO users (email, password_hash, role, first_name, last_name, phone, is_verified) 
VALUES ('admin@tpo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYn9qXwCqKKa', 'admin', 'System', 'Admin', '9876543210', TRUE);

-- Insert sample student (password: student123)
INSERT INTO users (email, password_hash, role, first_name, last_name, phone, is_verified) 
VALUES ('student@edu.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'John', 'Doe', '1234567890', TRUE);

INSERT INTO student_profiles (user_id, enrollment_number, year, department, cgpa, skills, interests) 
VALUES (2, 'ENR2024001', 3, 'Computer Science', 8.75, 'Python, Machine Learning, SQL', 'AI, Web Development');

-- Insert sample recruiter (password: recruiter123)
INSERT INTO users (email, password_hash, role, first_name, last_name, phone, is_verified) 
VALUES ('recruiter@company.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'recruiter', 'Jane', 'Smith', '5555555555', TRUE);

INSERT INTO recruiter_profiles (user_id, company_name, company_website, company_size, industry, required_skills) 
VALUES (3, 'Tech Corp', 'https://techcorp.com', 'large', 'Technology', 'Python, Java, Machine Learning');

-- =================================================================
-- VERIFICATION QUERIES
-- =================================================================

-- Check tables created
SELECT 'Tables created:' as status;
SHOW TABLES;

-- Check sample data
SELECT 'Sample data inserted:' as status;
SELECT id, email, role, first_name, last_name FROM users;

