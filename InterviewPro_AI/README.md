# 🎯 InterviewPro AI

## Intelligent Technical Interview Training Platform

![InterviewPro AI](https://img.shields.io/badge/InterviewPro-AI-blue?style=for-the-badge)

### 📋 Overview

InterviewPro AI is an AI-powered mock interview preparation platform that helps students and professionals ace their technical interviews. It features intelligent question generation, real-time answer evaluation, and comprehensive progress tracking.

### ✨ Key Features

1. **🤖 AI Interviewer** - Real-time mock interviews with AI-generated questions
2. **📝 Dynamic Question Bank** - 500+ curated technical questions across 10+ categories
3. **⏱️ Time-Boxed Sessions** - Realistic interview environment with time limits
4. **📊 Instant Evaluation** - AI evaluates answers with keyword matching
5. **🎯 Role-Based Preparation** - Specific questions for SDE, Data Scientist, ML Engineer, etc.
6. **📈 Progress Dashboard** - Visual charts showing improvement over time
7. **🔄 Adaptive Difficulty** - Questions adjust based on performance
8. **🏆 Achievements & Badges** - Gamification to motivate practice

### 🚀 Getting Started

#### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip

#### Installation

1. **Clone and navigate to the project**
```bash
cd InterviewPro_AI
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install flask mysql-connector-python openai
```

4. **Setup database**
```bash
# Create database in MySQL
mysql -u root -p < schema.sql

# Or use the setup script
python setup_database.py
```

5. **Configure environment variables**
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=interviewpro_ai
export DB_PORT=3306
export OPENAI_API_KEY=your_api_key  # Optional
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
```
http://localhost:8000
```

### 👤 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@interviewpro.com | admin123 |
| Demo Student | student1@edu.com | any |

### 📁 Project Structure

```
InterviewPro_AI/
├── app.py              # Main Flask application
├── models.py           # Database models and operations
├── ai_engine.py        # AI integration for questions and evaluation
├── schema.sql          # MySQL database schema
├── static/
│   └── style.css       # Main stylesheet
├── templates/
│   ├── base.html       # Base template
│   ├── index.html      # Landing page
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Student dashboard
│   ├── interview.html  # Interview interface
│   ├── result.html     # Interview results
│   ├── progress.html   # Progress tracking
│   └── admin/          # Admin templates
└── README.md
```

### 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** MySQL
- **AI Integration:** OpenAI API / Local LLM (Ollama)
- **Frontend:** HTML5, CSS3, JavaScript
- **Session Management:** Flask-Session

### 📊 Database Tables

1. `users` - Authentication
2. `students` - Student profiles
3. `interview_sessions` - Session history
4. `questions` - Question bank
5. `question_categories` - Topic categories
6. `evaluations` - AI evaluations
7. `achievements` - Gamification badges
8. `user_achievements` - User badges

### 🎓 Academic Usage

This project is suitable for:
- Final year projects
- Mini projects
- Internship projects
- Technical interview practice

### 📈 Future Scope

- Integration with video conferencing for live mock interviews
- Company-specific interview preparation
- Resume review integration
- Job application tracking
- Salary negotiation coaching
- Integration with LinkedIn API

### 📝 License

This project is for educational purposes.

### 🤝 Contributing

Feel free to contribute by adding more questions, improving the AI evaluation, or enhancing the UI.

---

**Built with ❤️ for interview preparation success!**

