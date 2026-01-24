"""
Ollama AI Integration Module
Provides AI-powered functions for interview, training, and resume generation
"""

import requests

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"
MODEL_LIGHT = "llama3.2:1b"


def ask_ollama(prompt, model=None, timeout=60):
    """
    Send a prompt to Ollama and get AI response
    
    Args:
        prompt: The prompt to send to the AI
        model: The model to use (defaults to llama3)
        timeout: Request timeout in seconds
        
    Returns:
        str: AI response text
    """
    if model is None:
        model = MODEL
        
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"Error: Ollama returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running."
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def chat_with_ai(message):
    """
    Chat with AI mentor for students
    
    Args:
        message: The question/message from student
        
    Returns:
        str: AI mentor's response
    """
    prompt = f"""
    You are an AI mentor for students.
    Answer clearly and professionally.
    Keep your response concise and helpful.

    Question:
    {message}
    """
    return ask_ollama(prompt)


def generate_questions(skills, interest, num_questions=2):
    """
    Generate interview questions based on student's skills and interest
    
    Args:
        skills: Student's skills
        interest: Student's area of interest
        num_questions: Number of questions to generate
        
    Returns:
        list: List of interview questions
    """
    prompt = f"""
    Generate exactly {num_questions} technical interview questions
    tailored to the following student profile:
    
    Skills: {skills}
    Interest: {interest}
    
    Requirements:
    - Questions should test both theoretical knowledge and practical skills
    - Number the questions clearly (1., 2., etc.)
    - Make questions appropriate for the student's skill level
    """
    
    text = ask_ollama(prompt)
    questions = [q.strip() for q in text.split("\n") if q.strip()]
    
    # Filter and clean questions
    clean_questions = []
    for q in questions:
        # Remove numbering if present
        clean_q = q.lstrip("1234567890. ")
        if clean_q and len(clean_q) > 10:
            clean_questions.append(clean_q)
    
    return clean_questions[:num_questions]


def evaluate_answer(question, answer):
    """
    Evaluate a student's interview answer
    
    Args:
        question: The interview question
        answer: The student's answer
        
    Returns:
        str: AI evaluation with score and feedback
    """
    prompt = f"""
    You are an AI interviewer evaluating a student's answer.
    
    Question:
    {question}
    
    Student's Answer:
    {answer}
    
    Please provide evaluation in the following format:
    Score: X/5
    Feedback: Your constructive feedback
    """
    return ask_ollama(prompt)


def recommend_training_path(skills, interest):
    """
    Recommend a personalized training path based on skills and interest
    
    Args:
        skills: Student's current skills
        interest: Student's area of interest
        
    Returns:
        str: Training recommendations
    """
    prompt = f"""
    You are an AI career advisor. Create a personalized training roadmap.
    
    Student Profile:
    - Skills: {skills}
    - Interest: {interest}
    
    Please provide:
    1. Recommended learning path (step by step)
    2. Key topics to master
    3. Recommended resources (courses, books, websites)
    4. Practical projects to build
    5. Career opportunities in this field
    """
    return ask_ollama(prompt)


def generate_ats_resume(name, year, cgpa, skills, objective, projects):
    """
    Generate an ATS-friendly resume
    
    Args:
        name: Student's name
        year: Year of study
        cgpa: CGPA
        skills: Technical skills
        objective: Career objective
        projects: Project descriptions
        
    Returns:
        str: Generated resume with ATS score
    """
    prompt = f"""
    Create a professional, ATS-friendly resume for the following student:
    
    Name: {name}
    Year: {year}
    CGPA: {cgpa}
    Skills: {skills}
    Objective: {objective}
    Projects: {projects}
    
    Format requirements:
    1. Start with Resume Score: X/100
    2. Include proper sections: Header, Education, Skills, Projects, Objective
    3. Use action verbs and quantifiable achievements
    4. Keep formatting clean and ATS-compatible
    5. Make it professional and compelling
    """
    return ask_ollama(prompt)


def analyze_placement_readiness(year, skills, cgpa, interview_score):
    """
    Analyze student's placement readiness
    
    Args:
        year: Year of study
        skills: Technical skills
        cgpa: CGPA
        interview_score: Mock interview score
        
    Returns:
        str: Analysis and recommendations
    """
    prompt = f"""
    Analyze this student's placement readiness:
    
    - Year: {year}
    - Skills: {skills}
    - CGPA: {cgpa}
    - Interview Score: {interview_score}
    
    Provide:
    1. Overall assessment
    2. Strengths
    3. Areas for improvement
    4. Specific recommendations
    """
    return ask_ollama(prompt)


# Fallback responses for when Ollama is not available
FALLBACK_QUESTIONS = [
    "Tell me about yourself.",
    "What are your technical skills?",
    "Explain one project you have worked on.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?"
]


def get_fallback_questions(num=2):
    """Get fallback questions when AI is unavailable"""
    return FALLBACK_QUESTIONS[:num]

