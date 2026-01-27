# 🛤️ SkillPath AI

## Personalized Career Development Platform

![SkillPath AI](https://img.shields.io/badge/SkillPath-AI-green?style=for-the-badge)

### 📋 Overview

SkillPath AI is an intelligent career development platform that helps students and professionals identify the right skills, generate personalized learning roadmaps, and achieve their career goals with AI-powered guidance.

### ✨ Key Features

1. **🔍 AI Skill Analyzer** - Comprehensive assessment evaluating technical and soft skills
2. **📊 Industry Gap Analysis** - Compare your skills with real-time job market demands
3. **🗺️ Personalized Learning Roadmap** - Day-by-day/ week-by-week learning plans
4. **📚 Resource Curator** - Curated courses, tutorials, projects, and certifications
5. **🎯 Goal Setting** - Set career goals and break into achievable milestones
6. **📈 Progress Tracker** - Visual progress tracking with completion percentages
7. **🔔 Smart Reminders** - Notification system for daily/weekly learning goals
8. **💡 Career Insights** - Market trends, salary ranges, job demand by role/location

### 🚀 Getting Started

#### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip

#### Installation

1. **Clone and navigate to the project**
```bash
cd SkillPath_AI
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
export DB_NAME=skillpath_ai
export DB_PORT=3306
export OPENAI_API_KEY=your_api_key  # Optional
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
```
http://localhost:8001
```

### 👤 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@skillpath.ai | admin123 |
| Demo Learner | learner1@edu.com | any |

### 📁 Project Structure

```
SkillPath_AI/
├── app.py              # Main Flask application
├── models.py           # Database models and operations
├── ai_engine.py        # AI for skill analysis and recommendations
├── schema.sql          # MySQL database schema
├── static/
│   └── style.css       # Main stylesheet
├── templates/
│   ├── base.html       # Base template
│   ├── index.html      # Landing page
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Learner dashboard
│   ├── skills.html     # Skills exploration
│   ├── roadmap.html    # Learning roadmap
│   ├── resources.html  # Learning resources
│   ├── goals.html      # Goal management
│   ├── trends.html     # Industry trends
│   ├── progress.html   # Progress tracking
│   └── admin/          # Admin templates
└── README.md
```

### 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** MySQL
- **AI Integration:** OpenAI API / Local LLM
- **Frontend:** HTML5, CSS3, JavaScript
- **Session Management:** Flask-Session

### 📊 Database Tables

1. `users` - Authentication
2. `learner_profiles` - Learner information
3. `skills` - Skill database
4. `user_skills` - User skill proficiency
5. `learning_paths` - Generated roadmaps
6. `resources` - Curated learning materials
7. `user_progress` - Progress tracking
8. `goals` - User goals
9. `industry_trends` - Market data

### 🎯 Career Paths

| Path | Duration | Difficulty | Description |
|------|----------|------------|-------------|
| ML Engineer | 24 weeks | Intermediate | Build and deploy ML models |
| Full Stack Developer | 16 weeks | Beginner | Frontend + Backend development |
| Data Scientist | 20 weeks | Intermediate | Data analysis and insights |
| Cloud Engineer | 18 weeks | Intermediate | Cloud infrastructure management |
| SDE | 16 weeks | Intermediate | Software development fundamentals |

### 🎓 Academic Usage

This project is suitable for:
- Final year projects
- Mini projects
- Career guidance systems
- Skill development platforms

### 📈 Future Scope

- Integration with Coursera, Udemy, edX APIs
- Blockchain-based skill certificates
- AI-powered career counselor chatbot
- Job matching based on skill profile
- Virtual cohort-based learning groups
- GitHub portfolio analysis integration

### 📝 License

This project is for educational purposes.

### 🤝 Contributing

Feel free to contribute by adding more skills, improving recommendations, or enhancing the UI.

---

**Built with ❤️ for career growth success!**

