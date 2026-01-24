"""
ChatGPT AI Integration Module
Provides AI-powered functions for interview, training, and resume generation
Using OpenAI's ChatGPT API
"""

import os
import requests
import json

# Try to import openai, install if needed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI package not installed. Run: pip install openai")

# Configuration - Get API key from environment or use placeholder
OPENAI_API_KEY = os.environ.get("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", "")

# Fallback to OpenAI's official API
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# Default model
MODEL = "gpt-3.5-turbo"
MODEL_LIGHT = "gpt-3.5-turbo"

# Your API key (hardcoded for demo - replace with your own)
API_KEY = "YOUR_OPENAI_API_KEY_HERE"

def get_client():
    """Get OpenAI client"""
    if OPENAI_AVAILABLE:
        key = OPENAI_API_KEY if OPENAI_API_KEY else API_KEY
        if key and key != "YOUR_OPENAI_API_KEY_HERE":
            return OpenAI(api_key=key)
    return None


def ask_chatgpt(prompt, model=None, timeout=60):
    """
    Send a prompt to ChatGPT and get AI response
    
    Args:
        prompt: The prompt to send to the AI
        model: The model to use (defaults to gpt-3.5-turbo)
        timeout: Request timeout in seconds
        
    Returns:
        str: AI response text
    """
    client = get_client()
    
    if client:
        try:
            response = client.chat.completions.create(
                model=model if model else MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for students. Answer clearly and professionally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            return None
    else:
        # Fallback to direct API call
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            
            data = {
                "model": model if model else MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant for students. Answer clearly and professionally."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                OPENAI_URL,
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None


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
    result = ask_chatgpt(prompt)
    return result if result else _fallback_response(message)


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
    - Keep questions concise but meaningful
    """
    
    result = ask_chatgpt(prompt)
    if result:
        questions = [q.strip() for q in result.split("\n") if q.strip()]
        clean_questions = []
        for q in questions:
            clean_q = q.lstrip("1234567890. ")
            if clean_q and len(clean_q) > 10:
                clean_questions.append(clean_q)
        return clean_questions[:num_questions]
    
    return _get_fallback_questions(num_questions)


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
    Feedback: Your constructive feedback (2-3 sentences)
    """
    result = ask_chatgpt(prompt)
    return result if result else f"Score: 3/5\nFeedback: Good attempt! Consider providing more specific examples."


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
    
    Keep it concise but comprehensive.
    """
    result = ask_chatgpt(prompt)
    return result if result else _fallback_training(skills, interest)


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
    1. Start with "Resume Score: X/100" where X is an estimate
    2. Include proper sections: Header, Education, Skills, Projects, Objective
    3. Use action verbs and quantifiable achievements
    4. Keep formatting clean and ATS-compatible
    5. Make it professional and compelling
    6. Use proper resume formatting with headers and bullet points
    """
    result = ask_chatgpt(prompt)
    return result if result else _fallback_resume(name, year, cgpa, skills, objective, projects)


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
    1. Overall assessment (1-2 sentences)
    2. Strengths (bullet points)
    3. Areas for improvement (bullet points)
    4. Specific recommendations (bullet points)
    """
    result = ask_chatgpt(prompt)
    return result if result else _fallback_analysis(year, skills, cgpa, interview_score)


# ============ FALLBACK RESPONSES ============

def _fallback_response(message):
    """Fallback response when AI is unavailable"""
    return f"Thank you for your question about '{message}'. As your AI mentor, I'd recommend focusing on building strong fundamentals and gaining practical experience. Keep learning and stay curious!"


def _get_fallback_questions(num=2):
    """Get fallback questions when AI is unavailable"""
    fallback = [
        "Tell me about yourself and your technical background.",
        "What are your key skills and how have you applied them?",
        "Describe a challenging project you worked on.",
        "What are your career goals and how do you plan to achieve them?",
        "Why are you interested in this field?"
    ]
    return fallback[:num]


def _fallback_training(skills, interest):
    """Fallback training recommendations"""
    return f"""
## Personalized Training Path for Your Profile

### Based on Your Skills: {skills}
### Your Interest: {interest}

1. **Foundation Building**
   - Master core concepts in your area of interest
   - Practice coding daily on platforms like LeetCode

2. **Key Topics to Master**
   - Data structures and algorithms
   - System design basics
   - Industry-specific tools

3. **Recommended Resources**
   - Online courses (Coursera, Udemy)
   - Official documentation
   - Practice projects

4. **Projects to Build**
   - Create a portfolio project
   - Contribute to open source
   - Build real-world applications

5. **Career Opportunities**
   - Research intern positions
   - Apply for campus placements
   - Network with professionals
    """


def _fallback_resume(name, year, cgpa, skills, objective, projects):
    """Fallback resume when AI is unavailable"""
    return f"""Resume Score: 75/100

{name}

📧 Contact: email@example.com | 📱 Phone: +91-XXXXXXXXXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAREER OBJECTIVE:
{objective}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDUCATION:
• Year: {year} of Study
• CGPA: {cgpa}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECHNICAL SKILLS:
{skills}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECTS:
{projects}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Strong problem-solving abilities
• Quick learner and team player
• Dedication to delivering quality work

"""


def _fallback_analysis(year, skills, cgpa, interview_score):
    """Fallback analysis when AI is unavailable"""
    return f"""
## Placement Readiness Analysis

### Overall Assessment:
You are on a good path! Keep improving your skills and practice more interviews.

### Strengths:
• Solid CGPA of {cgpa}
• Relevant skills in {skills}
• Good foundation for placement preparation

### Areas for Improvement:
• Practice more technical interview questions
• Work on communication skills
• Build more real-world projects

### Recommendations:
• Start preparing for aptitude tests
• Practice coding problems daily
• Update your resume regularly
• Apply to multiple companies
    """


# Print module loaded
print("✅ ChatGPT AI Module Loaded - Using OpenAI GPT-3.5")

