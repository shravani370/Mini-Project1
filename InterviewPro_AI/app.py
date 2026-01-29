"""
InterviewPro AI - Main Flask Application
Technical Interview Preparation Platform
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from datetime import datetime, timedelta
from models import db
import random

app = Flask(__name__)
app.secret_key = "interviewpro_secret_key_2024"

# Daily Challenges Data
DAILY_CHALLENGES = [
    {"id": 1, "title": "Morning Brain Boost", "description": "Complete 3 technical questions", "type": "technical", "count": 3, "xp_reward": 50},
    {"id": 2, "title": "Behavioral Master", "description": "Answer 2 behavioral questions", "type": "behavioral", "count": 2, "xp_reward": 40},
    {"id": 3, "title": "Code Warrior", "description": "Complete 2 coding challenges", "type": "coding", "count": 2, "xp_reward": 60},
    {"id": 4, "title": "Speed Demon", "description": "Finish an interview in under 5 minutes", "type": "speed", "count": 1, "xp_reward": 30},
    {"id": 5, "title": "Streak Saver", "description": "Practice for 3 consecutive days", "type": "streak", "count": 3, "xp_reward": 100},
]

# Motivational Quotes
QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal. - Winston Churchill",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The future belongs to those who believe in their dreams. - Eleanor Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
    "Your limitation—it's only your imagination. - Unknown",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau",
]

# Initialize database and create tables
try:
    db.create_tables()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

# Import AI functions
try:
    from ai_engine import (
        generate_questions,
        evaluate_answer,
        generate_follow_up,
        get_learning_recommendation
    )
    AI_AVAILABLE = True
    print("✅ AI Engine functions imported successfully!")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Engine not available, using basic functionality")

# ==================== HELPER FUNCTIONS ====================

def is_logged_in():
    """Check if user is logged in"""
    return session.get("user_id") is not None

def get_current_user():
    """Get current logged in user"""
    if is_logged_in():
        return db.get_user_by_id(session.get("user_id"))
    return None

# ==================== ROUTES ====================

@app.route("/")
def index():
    """Home page"""
    user = get_current_user()
    return render_template("index.html", user=user)


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
        target_role = request.form.get("target_role")
        experience = request.form.get("experience", "beginner")
        
        # Create user
        user_id = db.create_user(email, password, "student", first_name, last_name)
        
        if user_id:
            # Create student profile
            db.create_student(user_id, year, department, None, target_role, experience)
            
            # Auto login
            session["user_id"] = user_id
            session["email"] = email
            session["first_name"] = first_name
            session["role"] = "student"
            
            return redirect(url_for("dashboard"))
        else:
            return render_template("register.html", error="Email already registered or error occurred")
    
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
            
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    """Student dashboard"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    student = db.get_student_by_user_id(user_id)
    sessions = db.get_student_sessions(user_id, limit=5)
    achievements = db.get_user_achievements(user_id)
    
    # Get all achievements to show progress
    all_achievements = db.get_all_achievements()
    
    return render_template("dashboard.html", 
                           student=student, 
                           sessions=sessions,
                           achievements=achievements,
                           all_achievements=all_achievements)


@app.route("/start-interview", methods=["GET", "POST"])
def start_interview():
    """Start a new interview session"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    if request.method == "POST":
        session_type = request.form.get("session_type", "mixed")
        difficulty = request.form.get("difficulty", "medium")
        target_role = request.form.get("target_role", "SDE")
        question_count = int(request.form.get("question_count", 5))
        
        # Get student info for personalized questions
        student = db.get_student_by_user_id(session.get("user_id"))
        skills = student.get("target_role", "SDE") if student else "SDE"
        
        # Generate questions using AI
        if AI_AVAILABLE:
            questions = generate_questions(skills, skills, question_count)
        else:
            # Fallback questions
            questions = db.get_random_questions(question_count, session_type, difficulty)
        
        if not questions:
            questions = db.get_fallback_questions(question_count)
        
        # Store in session
        session["interview_questions"] = questions
        session["interview_answers"] = []
        session["interview_q_index"] = 0
        session["interview_score"] = 0
        session["interview_type"] = session_type
        session["interview_difficulty"] = difficulty
        session["interview_target_role"] = target_role
        
        # Create session in database
        session_id = db.create_interview_session(
            session.get("user_id"), 
            session_type, 
            difficulty, 
            target_role,
            [q.get("question", "") for q in questions]
        )
        session["current_session_id"] = session_id
        
        return redirect(url_for("interview"))
    
    # Get categories for display
    categories = db.get_question_categories()
    return render_template("start_interview.html", categories=categories)


@app.route("/interview", methods=["GET", "POST"])
def interview():
    """Interview interface"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    questions = session.get("interview_questions", [])
    q_index = session.get("interview_q_index", 0)
    
    if not questions or q_index >= len(questions):
        return redirect(url_for("interview_result"))
    
    current_question = questions[q_index]
    
    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        
        if answer:
            # Evaluate answer
            if AI_AVAILABLE:
                evaluation = evaluate_answer(current_question, answer)
            else:
                evaluation = {"score": 70, "feedback": "Good attempt!", "strengths": ["Answered"], "improvements": ["Add details"]}
            
            # Store answer and evaluation
            answers = session.get("interview_answers", [])
            answers.append({
                "question": current_question.get("question", ""),
                "answer": answer,
                "evaluation": evaluation
            })
            session["interview_answers"] = answers
            
            # Update score
            current_score = session.get("interview_score", 0)
            session["interview_score"] = current_score + evaluation.get("score", 0)
            
            # Move to next question
            session["interview_q_index"] = q_index + 1
            
            # Check if interview is complete
            if session["interview_q_index"] >= len(questions):
                return redirect(url_for("interview_result"))
        
        return redirect(url_for("interview"))
    
    # Calculate time remaining (5 minutes per question)
    time_limit = current_question.get("estimated_time", 5) * 60
    
    return render_template("interview.html",
                           question=current_question,
                           q_no=q_index + 1,
                           total=len(questions),
                           time_limit=time_limit)


@app.route("/interview/skip")
def skip_question():
    """Skip current question"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    q_index = session.get("interview_q_index", 0)
    questions = session.get("interview_questions", [])
    
    if questions and q_index < len(questions):
        # Store skipped question
        answers = session.get("interview_answers", [])
        answers.append({
            "question": questions[q_index].get("question", ""),
            "answer": "[SKIPPED]",
            "evaluation": {"score": 0, "feedback": "Question was skipped", "strengths": [], "improvements": ["Attempt all questions"]}
        })
        session["interview_answers"] = answers
        session["interview_q_index"] = q_index + 1
    
    return redirect(url_for("interview"))


@app.route("/interview/result")
def interview_result():
    """Show interview results"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    answers = session.get("interview_answers", [])
    total_score = session.get("interview_score", 0)
    questions = session.get("interview_questions", [])
    
    if not answers:
        return redirect(url_for("start_interview"))
    
    # Calculate final score
    max_score = sum(q.get("points", 10) for q in questions)
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Update database
    session_id = session.get("current_session_id")
    if session_id:
        db.update_interview_session(session_id, completed=True, score=total_score)
        db.update_student_stats(session.get("user_id"), total_score)
        db.check_and_award_achievements(session.get("user_id"))
    
    # Calculate category performance
    category_scores = {}
    for i, ans in enumerate(answers):
        if i < len(questions):
            category = questions[i].get("category", "unknown")
            score = ans.get("evaluation", {}).get("score", 0)
            if category not in category_scores:
                category_scores[category] = {"total": 0, "count": 0}
            category_scores[category]["total"] += score
            category_scores[category]["count"] += 1
    
    category_performance = {}
    for cat, data in category_scores.items():
        category_performance[cat] = data["total"] / data["count"] if data["count"] > 0 else 0
    
    # Determine weak areas for recommendations
    weak_areas = [cat for cat, score in category_performance.items() if score < 60]
    recommendations = get_learning_recommendation(weak_areas) if weak_areas else []
    
    # Clear session data
    session.pop("interview_questions", None)
    session.pop("interview_answers", None)
    session.pop("interview_q_index", None)
    session.pop("interview_score", None)
    session.pop("current_session_id", None)
    
    return render_template("result.html",
                           answers=answers,
                           total_score=total_score,
                           max_score=max_score,
                           percentage=percentage,
                           category_performance=category_performance,
                           recommendations=recommendations)


@app.route("/progress")
def progress():
    """View progress and analytics"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    student = db.get_student_by_user_id(user_id)
    sessions = db.get_student_sessions(user_id, limit=20)
    achievements = db.get_user_achievements(user_id)
    
    return render_template("progress.html",
                           student=student,
                           sessions=sessions,
                           achievements=achievements)


@app.route("/practice")
def practice():
    """Practice questions by category"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    categories = db.get_question_categories()
    return render_template("practice.html", categories=categories)


@app.route("/practice/category/<int:category_id>")
def practice_category(category_id):
    """Practice questions from a specific category"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    questions = db.get_questions_by_category(category_id, limit=20)
    return render_template("practice_category.html", questions=questions, category_id=category_id)


# ==================== NEW FEATURES ====================

@app.route("/leaderboard")
def leaderboard():
    """View the leaderboard"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    # Get top students (using mock data for demo)
    leaderboard_data = [
        {"rank": 1, "name": "Alex Chen", "xp": 2450, "interviews": 45, "avatar": "🎯"},
        {"rank": 2, "name": "Sarah Kim", "xp": 2280, "interviews": 42, "avatar": "🚀"},
        {"rank": 3, "name": "Mike Johnson", "xp": 2100, "interviews": 38, "avatar": "💻"},
        {"rank": 4, "name": "Emma Davis", "xp": 1950, "interviews": 35, "avatar": "⭐"},
        {"rank": 5, "name": "James Wilson", "xp": 1800, "interviews": 32, "avatar": "🔥"},
        {"rank": 6, "name": "Lisa Park", "xp": 1650, "interviews": 29, "avatar": "💡"},
        {"rank": 7, "name": "David Brown", "xp": 1500, "interviews": 26, "avatar": "⚡"},
        {"rank": 8, "name": "Sophie Turner", "xp": 1380, "interviews": 24, "avatar": "🌟"},
    ]
    
    current_user_xp = 750  # Mock user XP
    current_user_rank = 12
    
    return render_template("leaderboard.html", 
                           leaderboard=leaderboard_data,
                           current_user_xp=current_user_xp,
                           current_user_rank=current_user_rank)


@app.route("/challenges")
def challenges():
    """Daily challenges page"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get user's completed challenges for today
    completed_challenges = session.get("completed_challenges", [])
    user_xp = session.get("xp", 0)
    streak = session.get("streak", 0)
    
    quote = random.choice(QUOTES)
    
    return render_template("challenges.html",
                           challenges=DAILY_CHALLENGES,
                           completed_challenges=completed_challenges,
                           today=today,
                           user_xp=user_xp,
                           streak=streak,
                           quote=quote)


@app.route("/challenges/complete/<int:challenge_id>")
def complete_challenge(challenge_id):
    """Mark a challenge as complete"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    challenge = next((c for c in DAILY_CHALLENGES if c["id"] == challenge_id), None)
    
    if challenge:
        completed = session.get("completed_challenges", [])
        if challenge_id not in completed:
            completed.append(challenge_id)
            session["completed_challenges"] = completed
            session["xp"] = session.get("xp", 0) + challenge["xp_reward"]
            session["streak"] = session.get("streak", 0) + 1
    
    return redirect(url_for("challenges"))


@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    """Skills assessment quiz"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    if request.method == "POST":
        # Calculate score based on answers
        score = 0
        total = 5
        
        # Mock scoring
        score = random.randint(3, 5)
        percentage = (score / total) * 100
        
        # Update user XP
        session["xp"] = session.get("xp", 0) + percentage
        
        return render_template("assessment_result.html", 
                               score=score, 
                               total=total,
                               percentage=percentage)
    
    # Assessment questions
    assessment_questions = [
        {
            "id": 1,
            "question": "What is the time complexity of binary search?",
            "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
            "correct": 1
        },
        {
            "id": 2,
            "question": "Which data structure uses LIFO?",
            "options": ["Queue", "Stack", "Array", "Tree"],
            "correct": 1
        },
        {
            "id": 3,
            "question": "What is polymorphism in OOP?",
            "options": ["Hiding data", "Many forms", "Inheritance", "Encapsulation"],
            "correct": 1
        },
        {
            "id": 4,
            "question": "What does SQL stand for?",
            "options": ["Structured Query Language", "Simple Query Logic", "Standard Query Loop", "System Query Link"],
            "correct": 0
        },
        {
            "id": 5,
            "question": "Which sorting algorithm is fastest on average?",
            "options": ["Bubble Sort", "Quick Sort", "Selection Sort", "Insertion Sort"],
            "correct": 1
        }
    ]
    
    return render_template("assessment.html", questions=assessment_questions)


@app.route("/analytics")
def analytics():
    """Detailed performance analytics"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_id = session.get("user_id")
    sessions = db.get_student_sessions(user_id, limit=20)
    
    # Calculate statistics
    total_interviews = len(sessions)
    avg_score = sum(s.percentage for s in sessions) / total_interviews if total_interviews > 0 else 0
    
    # Mock chart data
    weekly_progress = [
        {"day": "Mon", "score": 65},
        {"day": "Tue", "score": 72},
        {"day": "Wed", "score": 68},
        {"day": "Thu", "score": 80},
        {"day": "Fri", "score": 75},
        {"day": "Sat", "score": 85},
        {"day": "Sun", "score": 78},
    ]
    
    skills_breakdown = [
        {"skill": "Technical", "score": 82},
        {"skill": "Behavioral", "score": 75},
        {"skill": "Coding", "score": 68},
        {"skill": "System Design", "score": 70},
    ]
    
    improvement_areas = ["System Design", "Coding Speed", "Data Structure Questions"]
    strengths = ["Problem Analysis", "Communication", "Behavioral Questions"]
    
    return render_template("analytics.html",
                           total_interviews=total_interviews,
                           avg_score=round(avg_score, 1),
                           weekly_progress=weekly_progress,
                           skills_breakdown=skills_breakdown,
                           improvement_areas=improvement_areas,
                           strengths=strengths)


@app.route("/xp")
def xp_details():
    """XP and achievements details"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    user_xp = session.get("xp", 750)
    level = user_xp // 500 + 1
    xp_to_next = 500 - (user_xp % 500)
    
    # All possible achievements
    all_badges = [
        {"name": "First Interview", "icon": "🎤", "xp": 50, "desc": "Complete your first mock interview"},
        {"name": "Perfect Score", "icon": "💯", "xp": 100, "desc": "Score 100% in an interview"},
        {"name": "Week Warrior", "icon": "🔥", "xp": 150, "desc": "Practice for 7 days in a row"},
        {"name": "Speed Demon", "icon": "⚡", "xp": 75, "desc": "Complete an interview in under 5 minutes"},
        {"name": "Coding Wizard", "icon": "🧙", "xp": 200, "desc": "Answer 10 coding questions correctly"},
        {"name": "Social Butterfly", "icon": "🦋", "xp": 50, "desc": "Share your progress on social media"},
        {"name": "Night Owl", "icon": "🦉", "xp": 50, "desc": "Practice after midnight"},
        {"name": "Early Bird", "icon": "🐦", "xp": 50, "desc": "Practice before 6 AM"},
    ]
    
    earned_xp = user_xp
    total_possible = sum(b["xp"] for b in all_badges)
    
    return render_template("xp_details.html",
                           user_xp=user_xp,
                           level=level,
                           xp_to_next=xp_to_next,
                           badges=all_badges,
                           earned_xp=earned_xp,
                           total_possible=total_possible)


@app.route("/resume", methods=["GET", "POST"])
def resume_builder():
    """Resume builder tool with ATS checking and job matching"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    if request.method == "POST":
        # Collect form data
        resume_data = {
            "full_name": request.form.get("full_name", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "linkedin": request.form.get("linkedin", ""),
            "github": request.form.get("github", ""),
            "portfolio": request.form.get("portfolio", ""),
            "summary": request.form.get("summary", ""),
            "target_job_title": request.form.get("target_job_title", ""),
            "target_company": request.form.get("target_company", ""),
            "job_description": request.form.get("job_description", ""),
            "template": request.form.get("template", "modern"),
            "education": [],
            "experience": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "awards": []
        }
        
        # Education
        edu_count = int(request.form.get("edu_count", 0))
        for i in range(edu_count):
            education = {
                "institution": request.form.get(f"edu_institution_{i}", ""),
                "degree": request.form.get(f"edu_degree_{i}", ""),
                "year": request.form.get(f"edu_year_{i}", ""),
                "cgpa": request.form.get(f"edu_cgpa_{i}", ""),
                "honors": request.form.get(f"edu_honors_{i}", "")
            }
            if education["institution"]:
                resume_data["education"].append(education)
        
        # Experience
        exp_count = int(request.form.get("exp_count", 0))
        for i in range(exp_count):
            experience = {
                "company": request.form.get(f"exp_company_{i}", ""),
                "position": request.form.get(f"exp_position_{i}", ""),
                "duration": request.form.get(f"exp_duration_{i}", ""),
                "description": request.form.get(f"exp_description_{i}", ""),
                "achievements": request.form.get(f"exp_achievements_{i}", "")
            }
            if experience["company"]:
                resume_data["experience"].append(experience)
        
        # Skills
        skills_input = request.form.get("skills", "")
        if skills_input:
            resume_data["skills"] = [s.strip() for s in skills_input.split(",")]
        
        # Projects
        proj_count = int(request.form.get("proj_count", 0))
        for i in range(proj_count):
            project = {
                "name": request.form.get(f"proj_name_{i}", ""),
                "description": request.form.get(f"proj_description_{i}", ""),
                "technologies": request.form.get(f"proj_tech_{i}", ""),
                "link": request.form.get(f"proj_link_{i}", ""),
                "impact": request.form.get(f"proj_impact_{i}", "")
            }
            if project["name"]:
                resume_data["projects"].append(project)
        
        # Certifications
        cert_count = int(request.form.get("cert_count", 0))
        for i in range(cert_count):
            cert = {
                "name": request.form.get(f"cert_name_{i}", ""),
                "issuer": request.form.get(f"cert_issuer_{i}", ""),
                "year": request.form.get(f"cert_year_{i}", "")
            }
            if cert["name"]:
                resume_data["certifications"].append(cert)
        
        # Awards
        award_count = int(request.form.get("award_count", 0))
        for i in range(award_count):
            award = {
                "title": request.form.get(f"award_title_{i}", ""),
                "issuer": request.form.get(f"award_issuer_{i}", ""),
                "year": request.form.get(f"award_year_{i}", ""),
                "description": request.form.get(f"award_desc_{i}", "")
            }
            if award["title"]:
                resume_data["awards"].append(award)
        
        # Store in session for preview
        session["resume_data"] = resume_data
        
        # Analyze ATS compatibility and job match
        ats_analysis = analyze_ats_compatibility(resume_data)
        job_match = analyze_job_match(resume_data)
        
        return render_template("resume_preview.html", 
                               resume=resume_data, 
                               ats_analysis=ats_analysis,
                               job_match=job_match)
    
    return render_template("resume_builder.html")


def analyze_ats_compatibility(resume_data):
    """Analyze resume ATS compatibility"""
    issues = []
    score = 100
    
    # Check file formatting
    if not resume_data.get("full_name"):
        issues.append({"type": "critical", "message": "Missing candidate name"})
        score -= 20
    
    if not resume_data.get("email"):
        issues.append({"type": "critical", "message": "Missing email address"})
        score -= 15
    
    # Check section headers (ATS reads these)
    sections = ["education", "experience", "skills", "projects", "certifications"]
    present_sections = [s for s in sections if resume_data.get(s)]
    
    if "education" not in present_sections:
        issues.append({"type": "warning", "message": "Missing Education section"})
        score -= 10
    
    if "experience" not in present_sections and not resume_data.get("projects"):
        issues.append({"type": "warning", "message": "Missing Experience or Projects section"})
        score -= 10
    
    # Check for action verbs (better for ATS)
    action_verbs = ["achieved", "developed", "implemented", "managed", "led", "created", 
                   "designed", "improved", "increased", "reduced", "streamlined"]
    text_content = str(resume_data)
    has_action_verbs = any(verb in text_content.lower() for verb in action_verbs)
    
    if not has_action_verbs:
        issues.append({"type": "info", "message": "Add action verbs (achieved, developed, led...) for better ATS parsing"})
        score -= 5
    
    # Check for quantifiable achievements
    has_numbers = any(char.isdigit() for char in str(resume_data))
    if not has_numbers:
        issues.append({"type": "info", "message": "Add metrics and numbers (e.g., 'Improved performance by 40%')"})
        score -= 5
    
    # Check email format
    email = resume_data.get("email", "")
    if email and "@" not in email:
        issues.append({"type": "critical", "message": "Invalid email format"})
        score -= 10
    
    # Check for custom sections
    if resume_data.get("awards"):
        issues.append({"type": "success", "message": "Awards section detected - adds distinction"})
    else:
        issues.append({"type": "info", "message": "Consider adding Awards or Achievements section"})
    
    # Check contact info completeness
    contact_score = 0
    if resume_data.get("email"): contact_score += 25
    if resume_data.get("phone"): contact_score += 25
    if resume_data.get("linkedin"): contact_score += 25
    if resume_data.get("github"): contact_score += 25
    
    if contact_score < 75:
        issues.append({"type": "info", "message": "Add more contact methods (LinkedIn, GitHub, phone)"})
        score -= 5
    
    # Formatting recommendations
    issues.append({
        "type": "tips", 
        "message": "Use standard section headers, avoid tables/graphics, save as .docx or .pdf"
    })
    
    return {
        "score": max(0, score),
        "issues": issues,
        "rating": "Excellent" if score >= 90 else "Good" if score >= 75 else "Needs Work" if score >= 50 else "Poor"
    }


def analyze_job_match(resume_data):
    """Analyze how well resume matches a job description"""
    job_desc = resume_data.get("job_description", "").lower()
    target_title = resume_data.get("target_job_title", "").lower()
    
    if not job_desc:
        return {"matched": False, "message": "Paste a job description to get matching analysis"}
    
    # Extract key requirements from job description
    job_keywords = set()
    important_terms = ["python", "javascript", "react", "node", "sql", "aws", "docker", 
                      "kubernetes", "machine learning", "api", "rest", "agile", "scrum",
                      "cloud", "database", "frontend", "backend", "full stack", "devops",
                      "ci/cd", "git", "linux", "microservices", "html", "css", "java",
                      "typescript", "mongodb", "postgresql", "redis", "elasticsearch"]
    
    for term in important_terms:
        if term in job_desc:
            job_keywords.add(term)
    
    # Get resume keywords
    resume_text = " ".join([
        resume_data.get("summary", ""),
        " ".join(resume_data.get("skills", [])),
        " ".join(exp.get("description", "") + " " + exp.get("achievements", "") 
                 for exp in resume_data.get("experience", [])),
        " ".join(proj.get("description", "") + " " + proj.get("technologies", "") 
                 for proj in resume_data.get("projects", []))
    ]).lower()
    
    # Find matches and gaps
    matched_keywords = []
    missing_keywords = []
    
    for keyword in job_keywords:
        if keyword in resume_text:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    match_rate = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0
    
    recommendations = []
    if missing_keywords:
        recommendations.append({
            "priority": "high",
            "action": f"Add these skills: {', '.join(missing_keywords[:5])}"
        })
    
    # Check for title matching
    title_words = target_title.split() if target_title else []
    title_matches = sum(1 for word in title_words if word in resume_text)
    
    if title_matches < len(title_words) and title_words:
        recommendations.append({
            "priority": "medium",
            "action": f"Include more {target_title} terminology in your summary"
        })
    
    # Suggest content based on job description
    action_verbs = []
    if "lead" in job_desc or "manage" in job_desc:
        action_verbs.append("Led a team of 5 engineers...")
    if "improve" in job_desc or "optimize" in job_desc:
        action_verbs.append("Improved system performance by 35%...")
    if "develop" in job_desc or "build" in job_desc:
        action_verbs.append("Developed scalable microservices...")
    
    if action_verbs:
        recommendations.append({
            "priority": "info",
            "action": "Consider adding achievements like: " + action_verbs[0]
        })
    
    return {
        "matched": True,
        "match_rate": round(match_rate, 1),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "recommendations": recommendations,
        "target_title": resume_data.get("target_job_title", ""),
        "target_company": resume_data.get("target_company", "")
    }


@app.route("/resume/download")
def download_resume():
    """Download resume with template selection"""
    if not is_logged_in():
        return redirect(url_for("login"))
    
    resume_data = session.get("resume_data", {})
    template = resume_data.get("template", "modern")
    
    if template == "simple":
        return generate_simple_resume(resume_data)
    elif template == "professional":
        return generate_professional_resume(resume_data)
    else:
        return generate_modern_resume(resume_data)


def generate_modern_resume(resume_data):
    """Generate modern format resume"""
    resume_text = f"""
{'='*60}
{resume_data.get('full_name', 'Your Name').upper()}
{'='*60}

Contact Information
-------------------
Email:    {resume_data.get('email', 'N/A')}
Phone:    {resume_data.get('phone', 'N/A')}
LinkedIn: {resume_data.get('linkedin', 'N/A')}
GitHub:   {resume_data.get('github', 'N/A')}
Portfolio: {resume_data.get('portfolio', 'N/A')}

Target Position: {resume_data.get('target_job_title', 'Open to opportunities')}
Target Company:  {resume_data.get('target_company', 'N/A')}

{'─'*60}
Professional Summary
{'─'*60}
{resume_data.get('summary', 'Experienced professional seeking new opportunities.')}

{'─'*60}
Core Competencies / Skills
{'─'*60}
"""
    
    skills = resume_data.get("skills", [])
    for i in range(0, len(skills), 4):
        resume_text += "  • " + "  |  ".join(skills[i:i+4]) + "\n"
    
    if resume_data.get("education"):
        resume_text += f"\n{'─'*60}\nEducation\n{'─'*60}\n"
        for edu in resume_data.get("education", []):
            resume_text += f"\n  > {edu.get('institution', '')}\n    {edu.get('degree', '')} | {edu.get('year', '')}\n    CGPA: {edu.get('cgpa', 'N/A')}\n    {edu.get('honors', '')}\n"
    
    if resume_data.get("experience"):
        resume_text += f"\n{'─'*60}\nProfessional Experience\n{'─'*60}\n"
        for exp in resume_data.get("experience", []):
            resume_text += f"\n  > {exp.get('position', '')}\n    {exp.get('company', '')} | {exp.get('duration', '')}\n\n    {exp.get('description', '')}\n\n    Key Achievements:\n    {exp.get('achievements', 'N/A')}\n"
    
    if resume_data.get("projects"):
        resume_text += f"\n{'─'*60}\nKey Projects\n{'─'*60}\n"
        for proj in resume_data.get("projects", []):
            resume_text += f"\n  > {proj.get('name', '')}\n    {proj.get('description', '')}\n    Technologies: {proj.get('technologies', 'N/A')}\n    Impact: {proj.get('impact', 'N/A')}\n    Link: {proj.get('link', 'N/A')}\n"
    
    if resume_data.get("certifications"):
        resume_text += f"\n{'─'*60}\nCertifications\n{'─'*60}\n"
        for cert in resume_data.get("certifications", []):
            resume_text += f"\n  > {cert.get('name', '')} - {cert.get('issuer', '')} ({cert.get('year', '')})\n"
    
    if resume_data.get("awards"):
        resume_text += f"\n{'─'*60}\nAwards & Recognition\n{'─'*60}\n"
        for award in resume_data.get("awards", []):
            resume_text += f"\n  > {award.get('title', '')} - {award.get('issuer', '')} ({award.get('year', '')})\n    {award.get('description', 'N/A')}\n"
    
    resume_text += f"\n{'='*60}\nGenerated by InterviewPro AI Resume Builder\n{'='*60}\n"
    
    return resume_text, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': f'attachment; filename=resume_{resume_data.get("full_name", "user").replace(" ", "_")}.txt'
    }


def generate_professional_resume(resume_data):
    """Generate professional format resume"""
    lines = [
        resume_data.get('full_name', 'Your Name').upper(),
        "=" * 50,
        f"Email: {resume_data.get('email', 'N/A')} | Phone: {resume_data.get('phone', 'N/A')}",
        f"LinkedIn: {resume_data.get('linkedin', 'N/A')} | GitHub: {resume_data.get('github', 'N/A')}",
        "",
        "PROFESSIONAL SUMMARY",
        "-" * 50,
        resume_data.get('summary', 'Professional summary...'),
        "",
        "KEY SKILLS",
        "-" * 50,
        ", ".join(resume_data.get('skills', [])),
        "",
    ]
    
    if resume_data.get("experience"):
        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("-" * 50)
        for exp in resume_data.get("experience", []):
            lines.append(f"{exp.get('position', '')} at {exp.get('company', '')}")
            lines.append(f"{exp.get('duration', '')}")
            lines.append(exp.get('description', ''))
            if exp.get('achievements'):
                lines.append("Achievements: " + exp.get('achievements'))
            lines.append("")
    
    if resume_data.get("education"):
        lines.append("EDUCATION")
        lines.append("-" * 50)
        for edu in resume_data.get("education", []):
            lines.append(f"{edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('year', '')})")
            if edu.get('cgpa'):
                lines.append(f"CGPA: {edu.get('cgpa')}")
            lines.append("")
    
    if resume_data.get("projects"):
        lines.append("NOTABLE PROJECTS")
        lines.append("-" * 50)
        for proj in resume_data.get("projects", []):
            lines.append(f"{proj.get('name', '')}")
            lines.append(f"{proj.get('description', '')}")
            lines.append(f"Technologies: {proj.get('technologies', 'N/A')}")
            if proj.get('link'):
                lines.append(f"Link: {proj.get('link')}")
            lines.append("")
    
    if resume_data.get("certifications"):
        lines.append("CERTIFICATIONS")
        lines.append("-" * 50)
        for cert in resume_data.get("certifications", []):
            lines.append(f"{cert.get('name', '')} - {cert.get('issuer', '')} ({cert.get('year', '')})")
    
    return "\n".join(lines), 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': f'attachment; filename=resume_{resume_data.get("full_name", "user").replace(" ", "_")}.txt'
    }


def generate_simple_resume(resume_data):
    """Generate simple format resume"""
    lines = [
        resume_data.get('full_name', 'Your Name'),
        "=" * 40,
        f"Email: {resume_data.get('email', 'N/A')} | Phone: {resume_data.get('phone', 'N/A')}",
        f"LinkedIn: {resume_data.get('linkedin', 'N/A')} | GitHub: {resume_data.get('github', 'N/A')}",
        "",
        "SUMMARY",
        "-" * 40,
        resume_data.get('summary', 'Professional summary...'),
        "",
        "SKILLS",
        "-" * 40,
        ", ".join(resume_data.get('skills', [])),
        "",
    ]
    
    if resume_data.get("experience"):
        lines.append("EXPERIENCE")
        lines.append("-" * 40)
        for exp in resume_data.get("experience", []):
            lines.append(f"* {exp.get('position', '')} at {exp.get('company', '')}")
            lines.append(f"  {exp.get('duration', '')}")
            lines.append(f"  {exp.get('description', '')}")
            lines.append("")
    
    if resume_data.get("education"):
        lines.append("EDUCATION")
        lines.append("-" * 40)
        for edu in resume_data.get("education", []):
            lines.append(f"* {edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('year', '')})")
    
    return "\n".join(lines), 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': f'attachment; filename=resume_{resume_data.get("full_name", "user").replace(" ", "_")}.txt'
    }


@app.route("/resume/ats-check", methods=["POST"])
def ats_check():
    """API endpoint for ATS checking"""
    data = request.get_json()
    resume_data = data.get("resume", {})
    
    analysis = analyze_ats_compatibility(resume_data)
    job_match = analyze_job_match(resume_data)
    
    return jsonify({"ats_analysis": analysis, "job_match": job_match})


# ==================== ADMIN ROUTES ====================


@app.route("/admin")
def admin():
    """Admin login page"""
    return render_template("admin.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    """Admin login"""
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "admin" and password == "admin123":
        session["user_id"] = 1  # Admin user ID
        session["role"] = "admin"
        session["first_name"] = "Admin"
        return redirect(url_for("admin_dashboard"))
    
    return render_template("admin.html", error="Invalid credentials")


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard"""
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    stats = db.get_admin_stats()
    students = db.get_all_students()
    
    return render_template("admin_dashboard.html", stats=stats, students=students)


@app.route("/admin/questions")
def admin_questions():
    """Manage questions"""
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    categories = db.get_question_categories()
    return render_template("admin_questions.html", categories=categories)


@app.route("/admin/questions/add", methods=["POST"])
def admin_add_question():
    """Add new question"""
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    category_id = int(request.form.get("category_id"))
    question_type = request.form.get("question_type")
    difficulty = request.form.get("difficulty")
    question_text = request.form.get("question_text")
    ideal_answer = request.form.get("ideal_answer")
    keywords = request.form.get("keywords")
    points = int(request.form.get("points", 10))
    estimated_time = int(request.form.get("estimated_time", 5))
    
    db.add_question(category_id, question_type, difficulty, question_text, 
                   ideal_answer, keywords, points, estimated_time)
    
    return redirect(url_for("admin_questions"))


@app.route("/admin/achievements")
def admin_achievements():
    """Manage achievements"""
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    achievements = db.get_all_achievements()
    return render_template("admin_achievements.html", achievements=achievements)


@app.route("/admin/stats")
def admin_stats():
    """View detailed statistics"""
    if not session.get("role") == "admin":
        return redirect(url_for("admin"))
    
    stats = db.get_admin_stats()
    return jsonify(stats)


# ==================== API ROUTES ====================

@app.route("/api/questions")
def api_get_questions():
    """API to get questions (for AJAX)"""
    category_id = request.args.get("category_id", type=int)
    difficulty = request.args.get("difficulty")
    count = request.args.get("count", 5, type=int)
    
    questions = db.get_questions_by_category(category_id, count, difficulty)
    return jsonify(questions)


@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    """API to evaluate answer"""
    data = request.get_json()
    question_data = data.get("question", {})
    answer = data.get("answer", "")
    
    if AI_AVAILABLE:
        evaluation = evaluate_answer(question_data, answer)
    else:
        evaluation = {"score": 70, "feedback": "Good attempt!", "strengths": ["Answered"], "improvements": ["Add details"]}
    
    return jsonify(evaluation)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", error="Internal server error"), 500


# ==================== RUN APP ====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
