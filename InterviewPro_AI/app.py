"""
InterviewPro AI - Main Flask Application
Technical Interview Preparation Platform
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from models import db

app = Flask(__name__)
app.secret_key = "interviewpro_secret_key_2024"

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
