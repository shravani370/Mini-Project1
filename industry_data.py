"""
Industry Data and Placement Analysis Module
Provides industry-specific placement data and analysis
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score


# Industry categories
INDUSTRIES = {
    "tech": {
        "name": "Technology & Software",
        "skills": ["Python", "Java", "JavaScript", "C++", "AI", "ML", "Web Dev"],
        "growth_rate": "15%",
        "avg_salary": "$80,000 - $120,000"
    },
    "finance": {
        "name": "Finance & Banking",
        "skills": ["Excel", "SQL", "Python", "R", "Data Analysis", "Risk Management"],
        "growth_rate": "8%",
        "avg_salary": "$70,000 - $100,000"
    },
    "consulting": {
        "name": "Consulting",
        "skills": ["Communication", "Problem Solving", "Analytics", "Presentation"],
        "growth_rate": "10%",
        "avg_salary": "$75,000 - $110,000"
    },
    "healthcare": {
        "name": "Healthcare",
        "skills": ["Biology", "Chemistry", "Data Analysis", "Research"],
        "growth_rate": "12%",
        "avg_salary": "$65,000 - $95,000"
    },
    "marketing": {
        "name": "Marketing & Digital",
        "skills": ["SEO", "Social Media", "Content Creation", "Analytics"],
        "growth_rate": "14%",
        "avg_salary": "$50,000 - $80,000"
    }
}


def load_industry_data():
    """Load industry placement data"""
    try:
        data = pd.read_csv("placement_data.csv")
        return data
    except FileNotFoundError:
        return None


def get_industry_info(industry_key):
    """Get information about a specific industry"""
    return INDUSTRIES.get(industry_key.lower(), {
        "name": "General",
        "skills": ["General Skills"],
        "growth_rate": "Unknown",
        "avg_salary": "Varies"
    })


def get_all_industries():
    """Get list of all industries"""
    return INDUSTRIES


def get_skills_by_industry(industry):
    """Get recommended skills for a specific industry"""
    industry_info = get_industry_info(industry)
    return industry_info.get("skills", [])


def get_placement_stats():
    """Get overall placement statistics"""
    data = load_industry_data()
    
    if data is None:
        return {
            "total_students": 0,
            "placed_students": 0,
            "placement_rate": 0,
            "avg_cgpa": 0
        }
    
    total = len(data)
    placed = data["placed"].sum() if "placed" in data.columns else 0
    
    return {
        "total_students": total,
        "placed_students": int(placed),
        "placement_rate": round((placed / total) * 100, 2) if total > 0 else 0,
        "avg_cgpa": round(data["cgpa"].mean(), 2) if "cgpa" in data.columns else 0
    }


def get_year_distribution():
    """Get student distribution by year"""
    data = load_industry_data()
    
    if data is None or "year" not in data.columns:
        return {"1st": 0, "2nd": 0, "3rd": 0, "4th": 0}
    
    return data["year"].value_counts().to_dict()


def get_skill_trends():
    """Get trending skills based on placement data"""
    data = load_industry_data()
    
    if data is None or "skills" not in data.columns:
        return {"Python": 10, "Java": 8, "AI": 7, "Web": 6}
    
    # Count skill occurrences
    skill_counts = {}
    for skills in data["skills"]:
        if pd.notna(skills):
            for skill in str(skills).split(","):
                skill = skill.strip().lower()
                if skill:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    return skill_counts


def suggest_skills_for_interest(interest, year):
    """
    Suggest skills based on interest and year of study
    
    Args:
        interest: Student's area of interest
        year: Year of study
        
    Returns:
        list: Recommended skills to learn
    """
    interest_lower = interest.lower()
    
    # Skill recommendations based on interest
    skill_map = {
        "ai": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Data Science"],
        "ml": ["Python", "Machine Learning", "Statistics", "Data Analysis", "Math"],
        "web": ["HTML", "CSS", "JavaScript", "React", "Django", "Node.js"],
        "backend": ["Java", "Python", "SQL", "APIs", "Docker", "AWS"],
        "frontend": ["HTML", "CSS", "JavaScript", "React", "Vue", "TypeScript"],
        "cloud": ["AWS", "Azure", "Docker", "Kubernetes", "DevOps"],
        "mobile": ["React Native", "Flutter", "Swift", "Kotlin", "Android"],
        "data": ["Python", "SQL", "Pandas", "Tableau", "Machine Learning"],
        "sde": ["Data Structures", "Algorithms", "C++", "Java", "System Design"],
        "android": ["Java", "Kotlin", "Android Studio", "Firebase"],
        "ios": ["Swift", "Xcode", "Firebase", "UI/UX"],
        "cybersecurity": ["Networking", "Linux", "Python", "Security Tools"],
        "blockchain": ["Solidity", "Web3", "Python", "Cryptography"],
    }
    # Find matching skills
    suggested = []
    for key, skills in skill_map.items():
        if key in interest_lower or any(k in interest_lower for k in key.split()):
            suggested.extend(skills)
    
    # Add year-specific advice
    try:
        year_num = int(year) if str(year).isdigit() else 3
    except (ValueError, TypeError):
        year_num = 3
    
    if year_num <= 2:
        suggested.extend(["Problem Solving", "Programming Basics", "Data Structures"])
    else:
        suggested.extend(["System Design", "Advanced Algorithms", "Real-world Projects"])
    
    # Remove duplicates and return
    return list(dict.fromkeys(suggested))[:10]


# Main function for testing
if __name__ == "__main__":
    print("Industry Data Module")
    print("=" * 40)
    print(f"\nAvailable Industries: {list(INDUSTRIES.keys())}")
    print(f"\nPlacement Stats: {get_placement_stats()}")
    print(f"\nSkill Trends: {get_skill_trends()}")
    print(f"\nSuggested skills for AI (3rd year): {suggest_skills_for_interest('AI', 3)}")

