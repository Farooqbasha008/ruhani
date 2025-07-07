-- RUHANI Database Schema for Snowflake
-- Run these commands in your Snowflake database

-- Create database and schema
CREATE DATABASE IF NOT EXISTS RUHANI_DB;
USE DATABASE RUHANI_DB;
CREATE SCHEMA IF NOT EXISTS RUHANI_SCHEMA;
USE SCHEMA RUHANI_SCHEMA;

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    github VARCHAR(255),
    linkedin VARCHAR(255),
    cultural_background VARCHAR(100),
    preferred_language VARCHAR(10) DEFAULT 'en',
    public_info TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Employee sessions table
CREATE TABLE IF NOT EXISTS employee_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    session_type VARCHAR(20) NOT NULL, -- 'voice_check_in', 'therapy', 'crisis'
    start_time TIMESTAMP_NTZ NOT NULL,
    end_time TIMESTAMP_NTZ,
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    transcript TEXT,
    ai_response TEXT,
    mood_score FLOAT,
    sentiment_analysis VARIANT,
    notes TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Sentiment logs table
CREATE TABLE IF NOT EXISTS sentiment_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    source VARCHAR(20) NOT NULL, -- 'email', 'slack', 'chat', 'voice_session'
    sentiment VARCHAR(20) NOT NULL,
    score FLOAT NOT NULL,
    text_content TEXT,
    timestamp TIMESTAMP_NTZ NOT NULL,
    context VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Wellness checks table
CREATE TABLE IF NOT EXISTS wellness_checks (
    check_id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    mood_rating VARCHAR(1) NOT NULL, -- '1', '2', '3', '4', '5'
    stress_level INTEGER NOT NULL, -- 1-10
    sleep_quality INTEGER NOT NULL, -- 1-10
    work_satisfaction INTEGER NOT NULL, -- 1-10
    social_support INTEGER NOT NULL, -- 1-10
    overall_score FLOAT NOT NULL,
    risk_level VARCHAR(10) NOT NULL, -- 'low', 'medium', 'high'
    notes TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- HR users table (for dashboard access)
CREATE TABLE IF NOT EXISTS hr_users (
    hr_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'admin', 'manager', 'analyst'
    permissions VARIANT, -- JSON object with permissions
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Activity logs table (for Coral Protocol integration)
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36),
    session_id VARCHAR(36),
    activity_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP_NTZ NOT NULL,
    data VARIANT, -- JSON object with activity data
    coral_reference VARCHAR(255), -- Reference to Coral Protocol
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (session_id) REFERENCES employee_sessions(session_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_employee_sessions_employee_id ON employee_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_sessions_start_time ON employee_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_employee_sessions_status ON employee_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sentiment_logs_employee_id ON sentiment_logs(employee_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_logs_timestamp ON sentiment_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_wellness_checks_employee_id ON wellness_checks(employee_id);
CREATE INDEX IF NOT EXISTS idx_wellness_checks_created_at ON wellness_checks(created_at);

-- Create views for common queries
CREATE OR REPLACE VIEW employee_wellness_summary AS
SELECT 
    e.employee_id,
    e.name,
    e.department,
    e.role,
    AVG(es.mood_score) as average_mood,
    COUNT(es.session_id) as total_sessions,
    MAX(es.start_time) as last_session,
    AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage,
    CASE 
        WHEN AVG(es.mood_score) >= 4.0 AND AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) < 0.2 THEN 'excellent'
        WHEN AVG(es.mood_score) >= 3.0 AND AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) < 0.4 THEN 'stable'
        WHEN AVG(es.mood_score) >= 2.5 THEN 'improving'
        WHEN AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) > 0.6 THEN 'at_risk'
        ELSE 'declining'
    END as wellness_status
FROM employees e
LEFT JOIN employee_sessions es ON e.employee_id = es.employee_id AND es.status = 'completed'
GROUP BY e.employee_id, e.name, e.department, e.role;

-- Create view for department insights
CREATE OR REPLACE VIEW department_insights AS
SELECT 
    e.department,
    COUNT(DISTINCT e.employee_id) as employee_count,
    AVG(es.mood_score) as average_mood,
    COUNT(es.session_id) as session_count,
    AVG(CASE WHEN es.mood_score <= 2.0 THEN 1 ELSE 0 END) as low_mood_percentage
FROM employees e
LEFT JOIN employee_sessions es ON e.employee_id = es.employee_id 
    AND es.status = 'completed' 
    AND es.start_time >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY e.department;

-- Insert sample HR user
INSERT INTO hr_users (hr_id, name, email, role, permissions) VALUES (
    'hr-admin-001',
    'HR Administrator',
    'hr@company.com',
    'admin',
    '{"can_view_all": true, "can_export": true, "can_manage_users": true}'
);

-- Grant necessary permissions
GRANT USAGE ON DATABASE RUHANI_DB TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA RUHANI_SCHEMA TO ROLE PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA RUHANI_SCHEMA TO ROLE PUBLIC;
GRANT SELECT ON ALL VIEWS IN SCHEMA RUHANI_SCHEMA TO ROLE PUBLIC; 