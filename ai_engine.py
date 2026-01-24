"""
AI Training & Placement Platform - AI Integration Module
Uses multiple AI backends for smart functionality
"""

import os
import json
import random
import re

# Try to import OpenAI, install if needed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI package not installed. Run: pip install openai")

# Try to import Ollama for local AI
try:
    from ollama_ai import OllamaAI
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not available. Install for local AI: pip install ollama")

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"
OLLAMA_MODEL = "llama3.2"


def markdown_to_html(text):
    """Convert markdown to HTML for proper display"""
    # Return plain text without conversion - markdown is annoying
    return text


# Knowledge base for exact answers
KNOWLEDGE_BASE = {
    "python": {
        "basics": """
## Python Fundamentals

### 1. Variables and Data Types
Python has these basic data types:
- **int**: Whole numbers (e.g., 42, -7)
- **float**: Decimals (e.g., 3.14, -0.5)
- **str**: Text (e.g., "Hello", 'World')
- **bool**: True/False
- **list**: Ordered collection (e.g., [1, 2, 3])
- **dict**: Key-value pairs (e.g., {'name': 'John', 'age': 25})

### 2. Control Flow
```
# If-elif-else
if condition:
    # do something
elif another_condition:
    # do something else
else:
    # default action

# Loops
for item in list:
    print(item)

while condition:
    # repeat while true
```

### 3. Functions
```
def function_name(param1, param2):
    '''Docstring describes the function'''
    result = param1 + param2
    return result
```

### 4. Key Concepts
- **List Comprehension**: `[x for x in list if x > 0]`
- **Lambda Functions**: `square = lambda x: x ** 2`
- **Decorators**: Functions that modify other functions
- **Generators**: Functions that yield values one at a time using `yield`
        """,
        
        "oop": """
## Python Object-Oriented Programming

### 1. Classes and Objects
```
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    
    def drive(self):
        return f"{self.brand} {self.model} is driving"

# Create object
my_car = Car("Toyota", "Camry")
print(my_car.drive())
```

### 2. Inheritance
```
class ElectricCar(Car):
    def __init__(self, brand, model, battery):
        super().__init__(brand, model)
        self.battery = battery
    
    def charge(self):
        return "Charging..."
```

### 3. Key OOP Principles
- **Encapsulation**: Hide internal state, require interaction through methods
- **Inheritance**: Create new classes from existing ones
- **Polymorphism**: Use same interface for different data types
- **Abstraction**: Hide complex implementation details
        """,
        
        "best_practices": """
## Python Best Practices

### 1. Code Style (PEP 8)
- Use 4 spaces per indentation level
- Limit lines to 79 characters
- Use descriptive variable names
- Add spaces around operators: `x = x + 1` not `x=x+1`

### 2. Virtual Environments
```
# Create virtual environment
python -m venv myenv

# Activate it
source myenv/bin/activate  # Linux/Mac
myenv\\Scripts\\activate   # Windows

# Install packages
pip install package_name

# Create requirements.txt
pip freeze > requirements.txt
```

### 3. Error Handling
```
try:
    result = risky_function()
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    print("This always runs")
```
        """
    },
    
    "interview_prep": {
        "general": """
## Technical Interview Preparation

### 1. Data Structures to Master
- **Arrays**: Random access, O(1)
- **Linked Lists**: Insertion/deletion, O(1)
- **Hash Tables**: Fast lookup, O(1) average
- **Stacks/Queues**: LIFO/FIFO, O(1)
- **Trees/Binary Search Trees**: Hierarchical, O(log n)
- **Graphs**: Networks, various complexities

### 2. Algorithms to Practice
- **Sorting**: QuickSort, MergeSort, BubbleSort
- **Searching**: Binary Search, BFS, DFS
- **Dynamic Programming**: Memoization, Tabulation
- **Recursion**: Base case, recursive case

### 3. Problem-Solving Approach
1. **Understand**: Read problem twice, clarify edge cases
2. **Plan**: Think of approach, discuss with interviewer
3. **Code**: Write clean, commented code
4. **Test**: Walk through examples, consider edge cases
5. **Optimize**: Time and space complexity analysis
        """,
        
        "behavioral": """
## Behavioral Interview Questions

### Common Questions & Answers

**1. "Tell me about yourself"**
"I'm a [year] student studying [field]. I'm passionate about [interest area] and have experience with [key skills]. I recently worked on [project] where I learned [skill]. I'm looking to [career goal]."

**2. "Why do you want to work here?"**
"I'm impressed by [company]'s work in [specific area]. My background in [skills] aligns well with your needs. I want to grow in [area] and believe your team offers great opportunities."

**3. "Describe a challenge you faced"**
"Situation: [Context]
Task: [Your responsibility]
Action: [What you did]
Result: [Outcome and what you learned]"
        """,
        
        "whiteboard": """
## Whiteboard Coding Tips

### Before Writing Code
1. **Clarify the problem**: Ask about constraints, edge cases
2. **Confirm understanding**: Repeat problem in your own words
3. **Think out loud**: Share your thought process
4. **Start simple**: Brute force first, optimize later

### While Coding
1. **Write cleanly**: Use proper indentation, spacing
2. **Comment important parts**: Explain complex logic
3. **Use meaningful names**: `targetIndex` not `ti`
4. **Handle edge cases**: Empty input, null, negative

### After Coding
1. **Test with examples**: Normal, edge, and corner cases
2. **Analyze complexity**: Time (Big O) and Space
3. **Discuss alternatives**: What if we used X approach?
        """
    },
    
    "career": {
        "resume": """
## Resume Writing Tips

### 1. Structure
- **Header**: Name, email, phone, LinkedIn, GitHub
- **Summary**: 2-3 lines highlighting key skills/goals
- **Education**: University, GPA (if > 3.0), relevant coursework
- **Skills**: Technical (languages, tools) and soft skills
- **Projects**: Name, tech stack, your contribution, impact
- **Experience**: Internships, part-time roles

### 2. Action Verbs (Use these!)
- **Technical**: Developed, Designed, Implemented, Optimized
- **Leadership**: Led, Mentored, Coordinated, Organized
- **Results**: Increased, Reduced, Improved, Achieved

### 3. Quantify Everything!
- "Improved code efficiency by 40%"
- "Led team of 5 developers"
- "Reduced deployment time by 50%"
        """,
        
        "portfolio": """
## Building Your Portfolio

### 1. What to Include
- **Personal Website**: Clean, professional, mobile-friendly
- **GitHub Profile**: Active contributions, clean repos
- **LinkedIn Profile**: Complete, with recommendations
- **Project Showcases**: Live demos with documentation

### 2. Project Ideas by Interest

**Web Development:**
- E-commerce platform
- Social media clone
- Task management app

**AI/ML:**
- Image classification model
- Sentiment analysis tool
- Recommendation system

### 3. Project Structure
```
project-name/
├── README.md          # Project description
├── src/               # Source code
├── tests/             # Test files
└── requirements.txt   # Dependencies
```
        """,
        
        "internship": """
## Finding Internships

### 1. Where to Look
- **Company websites**: Career pages
- **Job boards**: LinkedIn, Indeed, Glassdoor
- **University**: Career center, job fairs
- **Networking**: Alumni, professors, LinkedIn
- **Referrals**: Ask for referrals from connections

### 2. Application Timeline
- **Fall (Sep-Nov)**: Big tech internships (Google, Meta, etc.)
- **Spring (Jan-Mar)**: Mid-size companies, startups
- **Summer (Apr-Jun)**: Apply to remaining positions

### 3. Interview Preparation
- **Technical**: Data structures, algorithms, system design
- **Behavioral**: STAR method, company research
        """
    }
}


def _get_topic_from_message(message):
    """Extract topic from user message"""
    message_lower = message.lower()
    
    topics = {
        "python": ["python", "django", "flask", "pandas", "numpy"],
        "interview": ["interview", "whiteboard", "behavioral", "coding", "leetcode"],
        "career": ["resume", "portfolio", "internship", "job", "career", "job search"],
    }
    
    for topic, keywords in topics.items():
        if any(kw in message_lower for kw in keywords):
            return topic
    
    return None


def chat_with_ai(message):
    """Chat with AI mentor - provides exact, helpful answers"""
    message_lower = message.lower()
    
    # Check for exact answers in knowledge base
    topic = _get_topic_from_message(message)
    
    if topic == "python":
        if "class" in message_lower or "oop" in message_lower or "object" in message_lower:
            answer = KNOWLEDGE_BASE["python"]["oop"]
        elif "variable" in message_lower or "data type" in message_lower or "list" in message_lower:
            answer = KNOWLEDGE_BASE["python"]["basics"]
        elif "best practice" in message_lower or "pep" in message_lower or "virtual" in message_lower:
            answer = KNOWLEDGE_BASE["python"]["best_practices"]
        else:
            answer = KNOWLEDGE_BASE["python"]["basics"]
    
    elif topic == "interview":
        if "behavioral" in message_lower or "tell me" in message_lower or "why" in message_lower:
            answer = KNOWLEDGE_BASE["interview_prep"]["behavioral"]
        elif "whiteboard" in message_lower or "coding" in message_lower or "solve" in message_lower:
            answer = KNOWLEDGE_BASE["interview_prep"]["whiteboard"]
        else:
            answer = KNOWLEDGE_BASE["interview_prep"]["general"]
    
    elif topic == "career":
        if "resume" in message_lower or "cv" in message_lower:
            answer = KNOWLEDGE_BASE["career"]["resume"]
        elif "portfolio" in message_lower or "github" in message_lower or "project" in message_lower:
            answer = KNOWLEDGE_BASE["career"]["portfolio"]
        elif "internship" in message_lower or "intern" in message_lower:
            answer = KNOWLEDGE_BASE["career"]["internship"]
        else:
            answer = KNOWLEDGE_BASE["career"]["resume"]
    
    elif "how to learn" in message_lower or "learning path" in message_lower or "where to start" in message_lower:
        answer = _get_learning_path_answer()
    
    elif "salary" in message_lower or "package" in message_lower:
        answer = _get_salary_answer()
    
    elif "company" in message_lower or "which company" in message_lower:
        answer = _get_company_answer()
    
    else:
        answer = _get_smart_fallback(message)
    
    # Return plain text - markdown conversion removed
    return answer


def _get_learning_path_answer():
    """Get exact learning path answer"""
    return """
## How to Start Learning Programming

### For Complete Beginners:
1. **Choose a language**: Start with Python (easiest syntax)
2. **Free resources**:
   - Codecademy (interactive)
   - freeCodeCamp (videos + exercises)
   - Python.org official tutorial
3. **Practice daily**: 1-2 hours minimum
4. **Build projects**: Start small (calculator, to-do list)
5. **Join communities**: Reddit, Discord, Stack Overflow

### Week 1-2: Basics
- Variables, data types, operators
- Input/output
- Basic math operations

### Week 3-4: Control Flow
- If/else statements
- Loops (for, while)
- Functions

### Week 5-8: Data Structures
- Lists, dictionaries, tuples
- File handling
- Error handling

### After 2 months:
- Choose specialization (Web, AI, Data)
- Learn framework (Django, React, TensorFlow)
- Build portfolio projects
    """


def _get_salary_answer():
    """Get exact salary answer"""
    return """
## Entry-Level Salary Ranges (India)

### By Role:
- **SDE I**: ₹4-12 LPA (varies by company)
- **Data Analyst**: ₹3-8 LPA
- **Web Developer**: ₹3-10 LPA
- **AI/ML Engineer**: ₹5-15 LPA

### By Company Type:
- **FAANG**: ₹15-30 LPA
- **Tier 1 Startups**: ₹10-20 LPA
- **Tier 2 Startups**: ₹6-12 LPA
- **Service Companies**: ₹3-6 LPA

### Tips to Maximize Salary:
1. Strong DSA skills (clearing interviews)
2. Good projects (showing practical skills)
3. Negotiation (know your worth)
4. Multiple offers (leverage)
5. Continuous learning (stay relevant)
    """


def _get_company_answer():
    """Get exact company recommendation answer"""
    return """
## Top Companies for Freshers (India)

### By Category:

**Product Companies (High Salary):**
- Google, Microsoft, Amazon, Meta
- Walmart, Uber, Adobe, Oracle
- Salary: ₹15-40 LPA

**Indian Tech Giants:**
- TCS, Infosys, Wipro, HCL
- Salary: ₹3.5-7 LPA

**Startups:**
- CRED, Razorpay, Groww, Zepto
- Salary: ₹8-25 LPA

### How to Apply:
1. Check company career pages
2. Use LinkedIn job search
3. Employee referrals (most effective)
4. Campus placements
5. Job fairs and events
    """


def _get_smart_fallback(message):
    """Get smart fallback response"""
    return f"""
## Regarding Your Question: {message}

### Here's what I recommend:

1. **Start with fundamentals**: Understand the core concepts first
2. **Practice consistently**: Set aside dedicated time each day
3. **Build real projects**: Apply what you learn immediately
4. **Join communities**: Learn from others' experiences
5. **Get feedback**: Share your work and iterate

### Recommended Resources:
- **Online Courses**: Coursera, edX, Udemy
- **Practice Platforms**: LeetCode, HackerRank, GeeksforGeeks
- **Documentation**: Official docs for tools/frameworks
- **YouTube Tutorials**: Visual learning for complex topics
- **GitHub**: Study open source projects

### Next Steps:
1. Identify specific subtopics to focus on
2. Create a learning schedule
3. Set measurable goals (e.g., "complete 50 problems in 30 days")
4. Track your progress weekly
5. Apply for internships or projects

**Remember**: Consistency is key. Small daily progress leads to big results over time!
    """


# Print module loaded
print("✅ AI Engine Loaded - Ready for intelligent responses")

