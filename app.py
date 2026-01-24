print("🔥 APP.PY RUNNING - Using AI Engine 🔥")

from flask import Flask, render_template, request, session, redirect, url_for
import os
import random
from models import db

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize database and create tables
db.create_tables()

# Import AI functions from new engine
try:
    from ai_engine import (
        ask_ai as ask_ai_func,
        chat_with_ai,
        generate_questions,
        evaluate_answer,
        recommend_training_path,
        generate_ats_resume,
        analyze_placement_readiness
    )
    print("✅ AI Engine functions imported successfully!")
    USING_AI = True
except ImportError:
    print("⚠️ AI Engine module not found, using fallback functions")
    USING_AI = False

# ================= AI HELPER =================
def ask_ai(prompt):
    """Send a prompt to AI and get response"""
    if USING_AI:
        result = ask_ai_func(prompt)
        if result:
            return result
    return _fallback_ai(prompt)

def _fallback_ai(prompt):
    """Fallback when AI is not available"""
    return "AI is currently unavailable. Please try again later."


# ================= QUESTIONS GENERATOR =================
def generate_questions_ai():
    """Generate interview questions using AI"""
    skills = session.get("skills", "General programming")
    interest = session.get("interest", "Software Development")
    
    if USING_AI:
        questions = generate_questions(skills, interest, 5)
        if questions and len(questions) >= 3:
            return questions
    
    # Fallback questions based on skills
    fallback = [
        "Tell me about your technical background and the programming languages you're comfortable with.",
        "Describe a challenging project you've worked on and what you learned from it.",
        "How do you stay updated with the latest technology trends?",
        "What are your career goals and how do you plan to achieve them?",
        "Describe a situation where you had to learn something new quickly."
    ]
    return fallback


# ================= AI FUNCTIONS =================
def chat_with_ai_mentor(message):
    """Chat with AI mentor"""
    if USING_AI:
        return chat_with_ai(message)
    return _fallback_chat(message)

def _fallback_chat(message):
    return f"Thank you for your question about '{message}'. As your AI mentor, I'd recommend focusing on building strong fundamentals and practical skills. Keep learning!"

def generate_questions_skills_interest(skills, interest):
    """Generate interview questions based on skills and interest"""
    if USING_AI:
        return generate_questions(skills, interest, 5)
    # fallback
    return [
        f"Tell me about your experience with {skills}.",
        f"Why are you interested in {interest}?",
        "Describe a challenging project you worked on.",
        "How do you stay updated with technology?",
        "What are your career goals?"
    ]

def evaluate_answer_ai(question, answer):
    """Evaluate a student answer"""
    if USING_AI:
        return evaluate_answer(question, answer)
    return f"Score: 3/5\nFeedback: Good attempt! Consider providing more specific examples."

def recommend_training_path_ai(skills, interest):
    """Recommend training path based on skills and interest"""
    if USING_AI:
        return recommend_training_path(skills, interest)
    return f"Based on your skills in {skills} and interest in {interest}, we recommend focusing on practical projects and building a strong portfolio."

def generate_resume_ai(name, year, cgpa, skills, objective, projects):
    """Generate ATS resume"""
    if USING_AI:
        return generate_ats_resume(name, year, cgpa, skills, objective, projects)
    # fallback
    return f"""
Resume Score: 75/100

{name}

Career Objective:
{objective}

Skills:
{skills}

Projects:
{projects}

Education:
Year: {year}
CGPA: {cgpa}
    """


# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/student", methods=["GET", "POST"])
def student():
    # Check if already logged in
    if session.get("student_logged_in"):
        return redirect(url_for("placement"))
    
    if request.method == "POST":
        name = request.form.get("name")
        year = request.form.get("year")
        cgpa = request.form.get("cgpa")
        skills = request.form.get("skills")
        interest = request.form.get("interest")

        # Save to session for current session
        session["name"] = name
        session["year"] = year
        session["cgpa"] = cgpa
        session["skills"] = skills
        session["interest"] = interest

        # Save to database
        try:
            db.add_student(name, int(year), float(cgpa), skills, interest)
            print("✅ Student data saved to database")
        except Exception as e:
            print(f"❌ Error saving student data: {e}")

        return redirect(url_for("placement"))
    return render_template("student.html")


@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    """Student login - simple session-based login"""
    # Check if already logged in
    if session.get("student_logged_in"):
        return redirect(url_for("placement"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        
        # Simple login - just store in session (demo mode)
        session["email"] = email
        session["phone"] = phone
        session["student_logged_in"] = True
        print(f"✅ Student logged in: {email}")
        
        return redirect(url_for("placement"))
    
    return render_template("student_login.html")


@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    """Student registration"""
    # Check if already logged in
    if session.get("student_logged_in"):
        return redirect(url_for("placement"))
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        year = request.form.get("year")
        cgpa = request.form.get("cgpa")
        skills = request.form.get("skills")
        interest = request.form.get("interest")
        
        # Save to session
        session["name"] = name
        session["email"] = email
        session["phone"] = phone
        session["year"] = year
        session["cgpa"] = cgpa
        session["skills"] = skills
        session["interest"] = interest
        session["student_logged_in"] = True
        
        # Save to database
        try:
            db.add_student(name, int(year), float(cgpa), skills, interest, email)
            print("✅ Student registered and logged in")
        except Exception as e:
            print(f"❌ Error saving student data: {e}")
        
        return redirect(url_for("placement"))
    
    return render_template("student_register.html")


@app.route("/placement")
def placement():
    return render_template("placement.html")


@app.route("/start-interview")
def start_interview():
    session["questions"] = generate_questions_ai()
    session["q_no"] = 0
    session["score"] = 0
    if "name" not in session:
        session["name"] = "Student"
    return redirect(url_for("interview"))


@app.route("/interview", methods=["GET", "POST"])
def interview():
    questions = session.get("questions", [])
    q_no = session.get("q_no", 0)

    if not questions or q_no >= len(questions):
        return redirect(url_for("result"))

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        if len(answer) >= 20:
            session["score"] += 5
        session["q_no"] += 1
        return redirect(url_for("interview"))

    return render_template(
        "ai_interview.html",
        question=questions[q_no],
        q_no=q_no + 1,
        total=len(questions)
    )


@app.route("/result")
def result():
    return render_template(
        "result.html",
        name=session.get("name", "Student"),
        score=session.get("score", 0)
    )


@app.route("/logout")
def logout():
    """
    Secure Logout - Destroy user session, clear authentication tokens,
    prevent back navigation, and redirect to login page.
    
    Security measures:
    1. Clear all session data including authentication flags
    2. Set cache-control headers to prevent back navigation
    3. Redirect to login page with logout flag
    """
    # Determine which user type is logging out for the message
    user_type = "User"
    if session.get("student_logged_in"):
        user_type = "Student"
    elif session.get("recruiter_logged_in"):
        user_type = "Recruiter"
    elif session.get("admin_logged_in"):
        user_type = "Administrator"
    
    # Step 1: Clear all session data (authentication tokens/cookies)
    # This destroys the user session on logout
    session.clear()
    
    # Step 2: Set response headers to prevent back navigation after logout
    # These headers instruct the browser not to cache protected pages
    response = redirect(url_for("index", logged_out=user_type))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response


@app.route("/resume-builder")
def resume_builder():
    return render_template("resume_builder.html")


@app.route("/resume-form")
def resume_form():
    """Resume form page"""
    return render_template("resume_form.html")


@app.route("/resume", methods=["GET", "POST"])
def resume():
    """Display generated resume from form data"""
    if request.method == "POST":
        data = request.form
        # Store resume data in session
        session["resume_name"] = data.get("name", "")
        session["resume_year"] = data.get("year", "")
        session["resume_cgpa"] = data.get("cgpa", "")
        session["resume_skills"] = data.get("skills", "")
        session["resume_objective"] = data.get("objective", "")
        session["resume_projects"] = data.get("projects", "")
    
    # Get data from session or use defaults
    return render_template(
        "resume.html",
        name=session.get("resume_name", "Your Name"),
        year=session.get("resume_year", "2"),
        cgpa=session.get("resume_cgpa", "8.0"),
        skills=session.get("resume_skills", "Python, Java, JavaScript"),
        objective=session.get("resume_objective", "Motivated student seeking opportunities."),
        projects=session.get("resume_projects", "Various projects using modern technologies."),
        university=session.get("name", "Your University"),
        degree="Bachelor of Technology",
        email=session.get("email", ""),
        phone=session.get("phone", ""),
        location="India"
    )


@app.route("/generate-resume", methods=["POST"])
def generate_resume():
    data = request.form

    name = data.get("name")
    year = data.get("year")
    cgpa = data.get("cgpa")
    skills = data.get("skills")
    objective = data.get("objective")
    projects = data.get("projects")

    ai_response = generate_resume_ai(name, year, cgpa, skills, objective, projects)

    # extract score
    score = "75"
    if "Resume Score:" in ai_response:
        try:
            score = ai_response.split("Resume Score:")[1].split("/")[0].strip()
        except:
            pass

    return render_template(
        "resume_result.html",
        score=score,
        name=name,
        resume=ai_response
    )


@app.route("/ai-training", methods=["GET", "POST"])
def ai_training():
    """AI Training page with personalized content"""
    name = session.get("name", "Student")
    year = session.get("year", "1")
    skills = session.get("skills", "General")
    interest = session.get("interest", "Software Development")
    
    chat_response = None
    chat_response_user = None
    
    # Handle chat message
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            chat_response_user = message
            # Get AI response
            if USING_AI:
                chat_response = chat_with_ai(message)
            else:
                chat_response = f"Thanks for your question about '{message}'. As your AI mentor, I'd recommend focusing on building strong fundamentals in {skills} and gaining practical experience in {interest}."

    # Safe integer conversion
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        year_int = 1

    # Personalized training content using AI
    if USING_AI:
        ai_training_content = recommend_training_path_ai(skills, interest)
    else:
        ai_training_content = None

    # Build training content list
    training_content = []

    if "Python" in skills or "python" in skills.lower():
        training_content.append({
            "topic": "Python Programming",
            "tip": "Practice Python syntax, OOP concepts, and small projects relevant to your interest.",
            "link": "https://docs.python.org/",
            "icon": "🐍"
        })

    if "AI" in skills or "Machine Learning" in skills or "ML" in skills:
        training_content.append({
            "topic": "AI & Machine Learning",
            "tip": "Revise algorithms, model building, and practical coding exercises.",
            "link": "https://scikit-learn.org/",
            "icon": "🤖"
        })

    if year_int >= 3:
        training_content.append({
            "topic": "Advanced Topics",
            "tip": "Focus on system design, APIs, and mock interview problem-solving.",
            "link": "#",
            "icon": "⚡"
        })

    if "Web" in interest or "web" in interest.lower():
        training_content.append({
            "topic": "Web Development",
            "tip": "Learn HTML, CSS, JavaScript, and popular frameworks like React or Django.",
            "link": "https://developer.mozilla.org/",
            "icon": "🌐"
        })

    if "Cloud" in interest or "AWS" in skills or "Azure" in skills:
        training_content.append({
            "topic": "Cloud Computing",
            "tip": "Get familiar with AWS, Azure, or GCP services and cloud deployment.",
            "link": "https://aws.amazon.com/",
            "icon": "☁️"
        })

    if "Java" in skills:
        training_content.append({
            "topic": "Java Development",
            "tip": "Master Java fundamentals, Spring framework, and enterprise applications.",
            "link": "https://spring.io/",
            "icon": "☕"
        })

    if "Data" in interest or "data" in interest.lower():
        training_content.append({
            "topic": "Data Science",
            "tip": "Learn data analysis, visualization, and statistical methods.",
            "link": "https://pandas.pydata.org/",
            "icon": "📊"
        })

    if not training_content:
        training_content.append({
            "topic": "General Training",
            "tip": "Work on programming basics, problem-solving, and interview tips.",
            "link": "#",
            "icon": "📚"
        })

    return render_template("ai_training.html",
                           name=name,
                           year=year,
                           skills=skills,
                           interest=interest,
                           training_content=training_content,
                           ai_training=ai_training_content,
                           chat_response=chat_response,
                           chat_response_user=chat_response_user)


@app.route("/chat-ai", methods=["GET", "POST"])
def chat_ai():
    """AI Chat interface"""
    response = ""
    if request.method == "POST":
        message = request.form.get("message", "")
        if message:
            response = chat_with_ai_mentor(message)
    
    return render_template("ai_chat.html", response=response)


@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")


@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    """Admin dashboard with students and recruiters data"""
    # Simple authentication (in production, use proper auth)
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        # For demo, check simple credentials (case-insensitive username)
        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            print(f"✅ Admin login successful for user: {username}")
        else:
            print(f"❌ Admin login failed - Username: '{username}', Password length: {len(password)}")
            return render_template("admin.html", error="Invalid credentials")
    # Check if admin is logged in
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    # Get data from database
    students = db.get_students()
    recruiters = db.get_recruiters()

    # Calculate stats
    total_interviews = len(students)
    avg_score = sum(s.get("total_score", 0) for s in students) / len(students) if students else 0

    return render_template("admin_dashboard.html",
                           students=students,
                           recruiters=recruiters,
                           total_interviews=total_interviews,
                           avg_score=round(avg_score, 1))


@app.route("/recruiter", methods=["GET", "POST"])
def recruiter():
    """Recruiter registration page"""
    # Check if already logged in
    if session.get("recruiter_logged_in"):
        return redirect(url_for("recruiter_dashboard"))
    
    if request.method == "POST":
        company = request.form.get("company")
        recruiter_name = request.form.get("recruiter_name")
        email = request.form.get("email")
        skills = request.form.get("skills")

        # Store recruiter info in session
        session["recruiter_company"] = company
        session["recruiter_name"] = recruiter_name
        session["recruiter_email"] = email

        # Save to database
        try:
            db.add_recruiter(company, recruiter_name, email, skills)
            print("✅ Recruiter data saved to database")
        except Exception as e:
            print(f"❌ Error saving recruiter data: {e}")

        return redirect(url_for("recruiter_dashboard"))
    return render_template("recruiter.html")


@app.route("/recruiter/login", methods=["GET", "POST"])
def recruiter_login():
    """Recruiter login - simple session-based login"""
    # Check if already logged in
    if session.get("recruiter_logged_in"):
        return redirect(url_for("recruiter_dashboard"))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        
        # Simple login - just store in session (demo mode)
        session["email"] = email
        session["phone"] = phone
        session["recruiter_logged_in"] = True
        session["recruiter_email"] = email
        session["recruiter_phone"] = phone
        print(f"✅ Recruiter logged in: {email}")
        
        return redirect(url_for("recruiter_dashboard"))
    
    return render_template("recruiter_login.html")


@app.route("/recruiter/register", methods=["GET", "POST"])
def recruiter_register():
    """Recruiter registration"""
    # Check if already logged in
    if session.get("recruiter_logged_in"):
        return redirect(url_for("recruiter_dashboard"))
    
    if request.method == "POST":
        company = request.form.get("company")
        recruiter_name = request.form.get("recruiter_name")
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        skills = request.form.get("skills", "")
        
        # Store recruiter info in session
        session["recruiter_company"] = company
        session["recruiter_name"] = recruiter_name
        session["recruiter_email"] = email
        session["recruiter_phone"] = phone
        session["recruiter_skills"] = skills
        session["recruiter_logged_in"] = True
        
        # Save to database
        try:
            db.add_recruiter(company, recruiter_name, email, skills)
            print("✅ Recruiter registered and logged in")
        except Exception as e:
            print(f"❌ Error saving recruiter data: {e}")
        
        return redirect(url_for("recruiter_dashboard"))
    
    return render_template("recruiter_register.html")


@app.route("/recruiter_dashboard")
def recruiter_dashboard():
    """Recruiter dashboard with student profiles from database"""
    # Check if recruiter is logged in
    if not session.get("recruiter_logged_in"):
        return redirect(url_for("recruiter_login"))
    
    # Get students from database
    students_data = db.get_students()
    
    # Convert skills string to list for display
    students = []
    for s in students_data:
        student = dict(s)
        # Convert skills string to list
        if student.get('skills') and isinstance(student['skills'], str):
            student['skills'] = [skill.strip() for skill in student['skills'].split(',')]
        elif not student.get('skills'):
            student['skills'] = []
        # Set default score if not present
        if not student.get('score'):
            student['score'] = student.get('total_score', 0)
        students.append(student)
    
    # Get registered recruiters for the company info
    recruiters_data = db.get_recruiters()
    
    return render_template("recruiter_dashboard.html", 
                           students=students, 
                           recruiters=recruiters_data,
                           company_name=session.get("recruiter_company", "Company"))


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

