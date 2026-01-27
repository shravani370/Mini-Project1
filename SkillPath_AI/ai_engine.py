"""
SkillPath AI - AI Engine
Skill Assessment, Learning Path Generation, and Career Recommendations
"""

import os
import json
import random

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"

# Skill categories and their related skills
SKILL_RELATIONSHIPS = {
    "python": ["django", "flask", "pandas", "numpy", "machine learning", "data science"],
    "javascript": ["react", "node", "typescript", "vue", "angular"],
    "java": ["spring", "hibernate", "microservices", "android"],
    "sql": ["mysql", "postgresql", "mongodb", "database design"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
    "devops": ["docker", "kubernetes", "jenkins", "ci/cd", "terraform"]
}

# Learning paths by career goal
CAREER_PATHS = {
    "ml_engineer": {
        "title": "Machine Learning Engineer",
        "skills": ["Python Programming", "Statistics", "Machine Learning", "Deep Learning", "TensorFlow/PyTorch"],
        "duration_weeks": 24,
        "difficulty": "intermediate",
        "milestones": [
            {"week": 1, "title": "Python Mastery", "skills": ["Python Programming"]},
            {"week": 4, "title": "Statistics & Math", "skills": ["Statistics", "Linear Algebra"]},
            {"week": 8, "title": "ML Fundamentals", "skills": ["Machine Learning", "Scikit-learn"]},
            {"week": 16, "title": "Deep Learning", "skills": ["Deep Learning", "TensorFlow"]},
            {"week": 24, "title": "ML Ops & Projects", "skills": ["ML Ops", "Project Implementation"]}
        ]
    },
    "full_stack": {
        "title": "Full Stack Developer",
        "skills": ["HTML/CSS", "JavaScript", "React.js", "Node.js", "SQL & Databases"],
        "duration_weeks": 16,
        "difficulty": "beginner",
        "milestones": [
            {"week": 1, "title": "Web Fundamentals", "skills": ["HTML/CSS", "JavaScript"]},
            {"week": 4, "title": "Frontend Mastery", "skills": ["React.js", "CSS Frameworks"]},
            {"week": 8, "title": "Backend Development", "skills": ["Node.js", "REST APIs"]},
            {"week": 12, "title": "Database & DevOps", "skills": ["SQL & Databases", "Docker"]},
            {"week": 16, "title": "Full Stack Project", "skills": ["Project Implementation"]}
        ]
    },
    "data_scientist": {
        "title": "Data Scientist",
        "skills": ["Python Programming", "SQL & Databases", "Machine Learning", "Data Visualization", "Statistics"],
        "duration_weeks": 20,
        "difficulty": "intermediate",
        "milestones": [
            {"week": 1, "title": "Python & SQL", "skills": ["Python Programming", "SQL & Databases"]},
            {"week": 5, "title": "Statistics Foundation", "skills": ["Statistics", "Probability"]},
            {"week": 10, "title": "Machine Learning", "skills": ["Machine Learning", "Scikit-learn"]},
            {"week": 15, "title": "Data Visualization", "skills": ["Data Visualization", "Tableau"]},
            {"week": 20, "title": "Capstone Project", "skills": ["End-to-End Data Project"]}
        ]
    },
    "cloud_engineer": {
        "title": "Cloud Engineer",
        "skills": ["Linux", "AWS Cloud", "Docker & Containers", "Kubernetes", "CI/CD"],
        "duration_weeks": 18,
        "difficulty": "intermediate",
        "milestones": [
            {"week": 1, "title": "Linux Fundamentals", "skills": ["Linux", "Bash Scripting"]},
            {"week": 4, "title": "Cloud Basics", "skills": ["AWS Cloud", "Networking"]},
            {"week": 8, "title": "Containerization", "skills": ["Docker & Containers", "Dockerfile"]},
            {"week": 12, "title": "Orchestration", "skills": ["Kubernetes", "Helm"]},
            {"week": 18, "title": "DevOps Pipeline", "skills": ["CI/CD", "Infrastructure as Code"]}
        ]
    },
    "sde": {
        "title": "Software Development Engineer",
        "skills": ["Data Structures", "Algorithms", "SQL & Databases", "System Design", "Python Programming"],
        "duration_weeks": 16,
        "difficulty": "intermediate",
        "milestones": [
            {"week": 1, "title": "DSA Basics", "skills": ["Data Structures", "Basic Algorithms"]},
            {"week": 4, "title": "Advanced DSA", "skills": ["Advanced Algorithms", "DP"]},
            {"week": 8, "title": "System Design", "skills": ["System Design", "OOPS"]},
            {"week": 12, "title": "DBMS & SQL", "skills": ["SQL & Databases", "Normalization"]},
            {"week": 16, "title": "Mock Interviews", "skills": ["Interview Prep", "Mock Interviews"]}
        ]
    }
}

# Recommended resources by skill
RESOURCE_RECOMMENDATIONS = {
    "python": [
        {"title": "Python for Everybody", "type": "course", "url": "https://www.coursera.org/specializations/python", "provider": "Coursera", "rating": 4.8},
        {"title": "Automate the Boring Stuff", "type": "book", "url": "https://automatetheboringstuff.com/", "provider": "Free", "rating": 4.7},
        {"title": "Core Python Programming", "type": "course", "url": "https://www.udemy.com/python-core-and-advanced/", "provider": "Udemy", "rating": 4.5}
    ],
    "machine learning": [
        {"title": "Machine Learning by Andrew Ng", "type": "course", "url": "https://www.coursera.org/learn/machine-learning", "provider": "Coursera", "rating": 4.9},
        {"title": "Hands-On ML with Scikit-Learn", "type": "book", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/", "provider": "O'Reilly", "rating": 4.8},
        {"title": "Fast.ai Practical Deep Learning", "type": "course", "url": "https://course.fast.ai/", "provider": "Fast.ai", "rating": 4.7}
    ],
    "react": [
        {"title": "React - The Complete Guide", "type": "course", "url": "https://www.udemy.com/react-the-complete-guide-incl-redux/", "provider": "Udemy", "rating": 4.7},
        {"title": "React Documentation", "type": "tutorial", "url": "https://react.dev/", "provider": "Meta", "rating": 4.9},
        {"title": "Fullstack React", "type": "book", "url": "https://www.fullstackreact.com/", "provider": "Fullstack", "rating": 4.6}
    ],
    "aws": [
        {"title": "AWS Certified Solutions Architect", "type": "certification", "url": "https://aws.amazon.com/certification/", "provider": "AWS", "rating": 4.6},
        {"title": "AWS Free Tier Tutorials", "type": "tutorial", "url": "https://aws.amazon.com/getting-started/", "provider": "AWS", "rating": 4.5},
        {"title": "A Cloud Guru", "type": "course", "url": "https://acloudguru.com/", "provider": "A Cloud Guru", "rating": 4.4}
    ]
}


def analyze_skill_gaps(current_skills, target_role):
    """Analyze skill gaps between current skills and target role"""
    if target_role not in CAREER_PATHS:
        return {"error": "Unknown career path"}
    
    target_skills = CAREER_PATHS[target_role]["skills"]
    
    current_skills_lower = [s.lower() for s in current_skills]
    target_skills_lower = [s.lower() for s in target_skills]
    
    # Find missing skills
    missing_skills = []
    for skill in target_skills:
        skill_lower = skill.lower()
        found = False
        for current in current_skills_lower:
            if skill_lower in current or current in skill_lower:
                found = True
                break
        if not found:
            missing_skills.append(skill)
    
    # Find skills that need improvement
    improvement_skills = []
    for skill in target_skills:
        skill_lower = skill.lower()
        for current in current_skills_lower:
            if skill_lower in current or current in skill_lower:
                if skill not in improvement_skills:
                    improvement_skills.append(skill)
    
    return {
        "target_role": CAREER_PATHS[target_role]["title"],
        "total_skills_needed": len(target_skills),
        "current_skills_count": len(current_skills),
        "missing_skills": missing_skills,
        "skills_to_improve": improvement_skills,
        "completion_percentage": (len(current_skills) / len(target_skills)) * 100 if target_skills else 0
    }


def generate_learning_path(target_role, current_skills, weekly_hours=10):
    """Generate personalized learning path"""
    if target_role not in CAREER_PATHS:
        return None
    
    path = CAREER_PATHS[target_role]
    skill_gaps = analyze_skill_gaps(current_skills, target_role)
    
    # Calculate weeks needed based on weekly hours
    base_weeks = path["duration_weeks"]
    adjusted_weeks = base_weeks  # Could adjust based on weekly_hours
    
    learning_path = {
        "title": path["title"],
        "description": f"Complete path to become a {path['title']}",
        "total_weeks": adjusted_weeks,
        "difficulty": path["difficulty"],
        "skills_covered": path["skills"],
        "milestones": [],
        "weekly_schedule": []
    }
    
    # Generate weekly schedule
    weeks_per_milestone = adjusted_weeks // len(path["milestones"])
    
    for i, milestone in enumerate(path["milestones"]):
        start_week = i * weeks_per_milestone + 1
        end_week = (i + 1) * weeks_per_milestone
        
        learning_path["milestones"].append({
            "week": f"Week {start_week}-{end_week}",
            "title": milestone["title"],
            "skills": milestone["skills"],
            "resources": get_resources_for_skills(milestone["skills"]),
            "tasks": generate_weekly_tasks(milestone["skills"], weekly_hours)
        })
    
    return learning_path


def get_resources_for_skills(skills):
    """Get recommended resources for skills"""
    resources = []
    
    for skill in skills:
        skill_lower = skill.lower()
        for key, recs in RESOURCE_RECOMMENDATIONS.items():
            if key in skill_lower:
                resources.extend(recs[:2])
    
    # If no specific resources found, add general ones
    if not resources:
        resources = [
            {"title": "Coursera Online Courses", "type": "course", "provider": "Coursera"},
            {"title": "edX Free Courses", "type": "course", "provider": "edX"}
        ]
    
    return resources[:4]


def generate_weekly_tasks(skills, weekly_hours):
    """Generate weekly learning tasks"""
    tasks = []
    
    # Distribute hours across skills
    hours_per_skill = weekly_hours / len(skills) if skills else weekly_hours
    
    for skill in skills:
        tasks.append({
            "task": f"Learn {skill} fundamentals",
            "hours": round(hours_per_skill * 0.4, 1),
            "type": "learning"
        })
        tasks.append({
            "task": f"Practice {skill} exercises",
            "hours": round(hours_per_skill * 0.3, 1),
            "type": "practice"
        })
        tasks.append({
            "task": f"Build a {skill} mini-project",
            "hours": round(hours_per_skill * 0.3, 1),
            "type": "project"
        })
    
    return tasks


def get_career_recommendations(user_profile):
    """Get career recommendations based on user profile"""
    recommendations = []
    
    interests = user_profile.get("interests", "").lower()
    skills = user_profile.get("current_skills", "").lower()
    experience = user_profile.get("experience_level", "beginner")
    
    # Match career paths based on interests and skills
    if "ml" in interests or "ai" in interests or "machine learning" in skills:
        recommendations.append({
            "role": "ml_engineer",
            "title": "Machine Learning Engineer",
            "match_score": 90,
            "reason": "Based on your interest in AI/ML",
            "salary_range": "₹8-20 LPA",
            "demand": "Very High"
        })
    
    if "web" in interests or "frontend" in skills or "javascript" in skills:
        recommendations.append({
            "role": "full_stack",
            "title": "Full Stack Developer",
            "match_score": 85,
            "reason": "Based on your web development interest",
            "salary_range": "₹5-15 LPA",
            "demand": "High"
        })
    
    if "data" in interests or "sql" in skills or "python" in skills:
        recommendations.append({
            "role": "data_scientist",
            "title": "Data Scientist",
            "match_score": 88,
            "reason": "Based on your data analysis interest",
            "salary_range": "₹6-18 LPA",
            "demand": "Very High"
        })
    
    if "cloud" in interests or "aws" in skills or "devops" in skills:
        recommendations.append({
            "role": "cloud_engineer",
            "title": "Cloud Engineer",
            "match_score": 82,
            "reason": "Based on your cloud interest",
            "salary_range": "₹6-15 LPA",
            "demand": "High"
        })
    
    # Default recommendation based on experience
    if not recommendations:
        recommendations.append({
            "role": "sde",
            "title": "Software Development Engineer",
            "match_score": 75,
            "reason": "Popular choice for all skill levels",
            "salary_range": "₹4-12 LPA",
            "demand": "High"
        })
    
    return sorted(recommendations, key=lambda x: x["match_score"], reverse=True)


def analyze_industry_demand(skills):
    """Analyze industry demand for skills"""
    demand_data = []
    
    for skill in skills:
        skill_lower = skill.lower()
        
        # Machine Learning
        if "machine learning" in skill_lower or "ml" in skill_lower:
            demand_data.append({
                "skill": skill,
                "demand_growth": 25.0,
                "avg_salary": "₹8-20 LPA",
                "top_companies": "Google, Microsoft, Amazon, Meta",
                "trend": "rising",
                "job_openings": 15000
            })
        
        # Cloud
        elif "cloud" in skill_lower or "aws" in skill_lower:
            demand_data.append({
                "skill": skill,
                "demand_growth": 18.0,
                "avg_salary": "₹6-15 LPA",
                "top_companies": "TCS, Infosys, Amazon, Microsoft",
                "trend": "rising",
                "job_openings": 12000
            })
        
        # Python
        elif "python" in skill_lower:
            demand_data.append({
                "skill": skill,
                "demand_growth": 15.5,
                "avg_salary": "₹5-12 LPA",
                "top_companies": "Google, Facebook, Amazon, Startups",
                "trend": "rising",
                "job_openings": 20000
            })
        
        # Web Development
        elif "react" in skill_lower or "javascript" in skill_lower or "web" in skill_lower:
            demand_data.append({
                "skill": skill,
                "demand_growth": 12.0,
                "avg_salary": "₹5-10 LPA",
                "top_companies": "Paytm, Flipkart, Ola, Startups",
                "trend": "stable",
                "job_openings": 18000
            })
        
        # Data Science
        elif "data" in skill_lower or "sql" in skill_lower:
            demand_data.append({
                "skill": skill,
                "demand_growth": 20.0,
                "avg_salary": "₹6-18 LPA",
                "top_companies": "Amazon, Walmart, Google, Banks",
                "trend": "rising",
                "job_openings": 14000
            })
        
        # Default
        else:
            demand_data.append({
                "skill": skill,
                "demand_growth": 8.0,
                "avg_salary": "₹4-8 LPA",
                "top_companies": "Various",
                "trend": "stable",
                "job_openings": 5000
            })
    
    return demand_data


def get_ai_recommendation(user_query, context=None):
    """Get AI-powered career recommendation"""
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        # Return helpful fallback response
        return get_fallback_recommendation(user_query)
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a career guidance expert. Provide helpful, specific advice about careers, skills, and learning paths."
                },
                {
                    "role": "user",
                    "content": f"User question: {user_query}\n\nContext: {context if context else 'General career guidance'}"
                }
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ AI recommendation error: {e}")
        return get_fallback_recommendation(user_query)


def get_fallback_recommendation(query):
    """Fallback recommendation when AI is not available"""
    query_lower = query.lower()
    
    if "python" in query_lower or "learn" in query_lower:
        return """
## Learning Recommendations

### For Python Beginners:
1. **Start with fundamentals**: Variables, data types, control flow
2. **Practice daily**: 1-2 hours minimum
3. **Build projects**: Start with calculator, to-do list
4. **Resources**: 
   - Python.org official tutorial
   - freeCodeCamp Python course
   - Codecademy Python track

### Suggested Learning Path:
- **Week 1-2**: Basics (variables, loops, functions)
- **Week 3-4**: Data structures (lists, dicts, tuples)
- **Week 5-6**: File handling and error handling
- **Week 7-8**: OOP concepts
- **Week 9+**: Specialize based on interest
        """
    
    elif "career" in query_lower or "job" in query_lower:
        return """
## Career Guidance

### Top Career Paths in Tech:
1. **Machine Learning Engineer** - Highest demand, ₹8-20 LPA
2. **Full Stack Developer** - Consistent demand, ₹5-15 LPA
3. **Data Scientist** - Growing field, ₹6-18 LPA
4. **Cloud Engineer** - Cloud adoption growing, ₹6-15 LPA
5. **SDE** - Classic software role, ₹4-12 LPA

### Tips:
- Build a strong portfolio with projects
- Practice DSA for product companies
- Get certifications for cloud roles
- Network and contribute to open source
        """
    
    elif "salary" in query_lower or "package" in query_lower:
        return """
## Salary Ranges (India - Entry Level)

| Role | Range (LPA) |
|------|-------------|
| SDE I | ₹4-12 |
| Data Analyst | ₹3-8 |
| Web Developer | ₹3-10 |
| ML Engineer | ₹5-15 |
| Cloud Engineer | ₹6-12 |

### Tips to Maximize:
1. Strong DSA skills (clearing interviews)
2. Good projects portfolio
3. Multiple offers (leverage)
4. Continuous learning
        """
    
    else:
        return """
## Career Development Tips

### General Advice:
1. **Identify your interests**: What type of work excites you?
2. **Assess current skills**: What are you good at?
3. **Set clear goals**: Where do you want to be in 1/3/5 years?
4. **Create learning plan**: Break goals into actionable steps
5. **Stay consistent**: Daily learning leads to big results

### Resources:
- LinkedIn Learning
- Coursera/edX
- YouTube tutorials
- Books and documentation
- Practice platforms (LeetCode, HackerRank)
        """


print("✅ SkillPath AI Engine Loaded - Ready for career guidance")
