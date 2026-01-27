"""
SkillPath AI - Main Flask Application
Personalized Career Development Platform
"""

from flask import Flask, render_template, request, session, redirect, url_for
import os
from models import db

app = Flask(__name__)
app.secret_key = "skillpath_secret_key_2024"

# Initialize database
try:
    db.create_tables()
    print("✅ SkillPath AI Database initialized!")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

# Import AI functions
try:
    from ai_engine import (
        generate_learning_path,
        analyze_skill_gaps,
        get_career_recommendations,
        analyze_industry_demand,
        get_ai_recommendation,
        CAREER_PATHS
    )
    AI_AVAILABLE = True
    print("✅ AI Engine functions imported successfully!")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Engine not available")


def is_logged_in():
    return session.get("user_id") is not None

def get_current_user():
    if is_logged_in():
        return db.get_user_by_id(session.get("user_id"))
    return None


# ==================== ROUTES ====================

@app.route("/")
def index():
    """Home page"""
    user = get_current_user()
    trends = db.get_industry_trends()
    return render_template("index.html", user=user, trends=trends)


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        year = request.form.get("year")
        department = request.form.get("department")
        current_skills = request.form.get("current_skills")
        target_skills = request.form.get("target_skills")
        career_goal = request.form.get("career_goal")
        experience = request.form.get("experience", "beginner")
        
        # Create user
        user_id = db.create_user(email, password, "learner", first_name, last_name)
        
        if user_id:
            # Create learner profile
            db.create_learner_profile(user_id, year, department, current_skills, target_skills, career_goal, experience)
            
            session["user_id"] = user_id
            session["email"] = email
            session["first_name"] = first_name
            session["role"] = "learner"
            
            return redirect(url_for("dashboard"))
        
        return render_template("register.html", error="Registration failed. Email may already exist.")
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = db.get_user_by_email(email)
        
        if user and user["password_hash"] == password:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["first_name"] = user["first_name"]
            session["role"] = user["role"]
            
            return redirect(url_for("dashboard"))
        
        return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    """Learner dashboard"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    profile = db.get_learner_by_user_id(user_id)
    progress = db.get_user_progress(user_id)
    goals = db.get_goals(user_id)[:3]
    paths = db.get_learning_paths(user_id)[:2]
    
    # Get career recommendations
    if profile and AI_AVAILABLE:
        recommendations = get_career_recommendations({
            "interests": profile.get("career_goal", ""),
            "current_skills": profile.get("current_skills", ""),
            "experience_level": profile.get("experience_level", "beginner")
        })
    else:
        recommendations = []
    
    return render_template("dashboard.html",
                           profile=profile,
                           progress=progress,
                           goals=goals,
                           paths=paths,
                           recommendations=recommendations)


@app.route("/skills")
def skills():
    """Skills exploration page"""
    all_skills = db.get_all_skills()
    
    # Group by category
    skills_by_category = {}
    for skill in all_skills:
        cat = skill.get("category", "other")
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(skill)
    
    return render_template("skills.html", skills_by_category=skills_by_category)


@app.route("/roadmap", methods=["GET", "POST"])
def roadmap():
    """Learning roadmap page"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    profile = db.get_learner_by_user_id(user_id)
    paths = db.get_learning_paths(user_id)
    
    if request.method == "POST":
        target_role = request.path.split("/")[-1] or request.form.get("target_role")
        if not target_role:
            target_role = list(CAREER_PATHS.keys())[0]
        
        current_skills = profile.get("current_skills", "") if profile else ""
        skill_list = [s.strip() for s in current_skills.split(",") if s.strip()]
        
        if AI_AVAILABLE:
            learning_path = generate_learning_path(target_role, skill_list, 10)
        else:
            learning_path = None
        
        if learning_path:
            db.create_learning_path(
                user_id,
                f"{CAREER_PATHS[target_role]['title']} Path",
                target_role,
                learning_path["description"],
                learning_path["total_weeks"],
                learning_path["difficulty"]
            )
            paths = db.get_learning_paths(user_id)
        
        return render_template("roadmap.html", profile=profile, paths=paths, learning_path=learning_path, career_paths=CAREER_PATHS)
    
    return render_template("roadmap.html", profile=profile, paths=paths, career_paths=CAREER_PATHS)


@app.route("/roadmap/<role>")
def roadmap_role(role):
    """Generate roadmap for specific role"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    profile = db.get_learner_by_user_id(user_id)
    
    if role in CAREER_PATHS:
        current_skills = profile.get("current_skills", "") if profile else ""
        skill_list = [s.strip() for s in current_skills.split(",") if s.strip()]
        
        if AI_AVAILABLE:
            learning_path = generate_learning_path(role, skill_list, 10)
        else:
            learning_path = CAREER_PATHS[role]
        
        paths = db.get_learning_paths(user_id)
        return render_template("roadmap.html", profile=profile, paths=paths, learning_path=learning_path, selected_role=role, career_paths=CAREER_PATHS)
    
    return redirect(url_for("roadmap"))


@app.route("/resources")
def resources():
    """Learning resources page"""
    resources_list = db.get_resources()
    
    # Group by type
    resources_by_type = {}
    for res in resources_list:
        rtype = res.get("type", "other")
        if rtype not in resources_by_type:
            resources_by_type[rtype] = []
        resources_by_type[rtype].append(res)
    
    return render_template("resources.html", resources_by_type=resources_by_type)


@app.route("/goals", methods=["GET", "POST"])
def goals_page():
    """Goals management page"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    goals = db.get_goals(user_id)
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        goal_type = request.form.get("goal_type")
        target_date = request.form.get("target_date")
        priority = request.form.get("priority", "medium")
        
        db.create_goal(user_id, title, description, goal_type, target_date, priority)
        goals = db.get_goals(user_id)
    
    return render_template("goals.html", goals=goals)


@app.route("/trends")
def trends():
    """Industry trends page"""
    trends = db.get_industry_trends()
    return render_template("trends.html", trends=trends)


@app.route("/progress")
def progress_tracker():
    """Progress tracking page"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    profile = db.get_learner_by_user_id(user_id)
    progress = db.get_user_progress(user_id)
    user_skills = db.get_user_skills(user_id)
    goals = db.get_goals(user_id)
    
    return render_template("progress.html",
                           profile=profile,
                           progress=progress,
                           user_skills=user_skills,
                           goals=goals)


# ==================== ADMIN ROUTES ====================

@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "admin" and password == "admin123":
        session["user_id"] = 1
        session["role"] = "admin"
        session["first_name"] = "Admin"
        return redirect(url_for("admin_dashboard"))
    
    return render_template("admin.html", error="Invalid credentials")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    stats = db.get_admin_stats()
    return render_template("admin_dashboard.html", stats=stats)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", error="Internal server error"), 500


# ==================== RUN ====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
