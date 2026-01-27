"""
InterviewPro AI - AI Integration Module
Handles interview question generation, answer evaluation, and follow-up questions
"""

import os
import json
import random
import re

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI package not installed. Run: pip install openai")

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"

# Question bank by category and difficulty
QUESTION_BANK = {
    "data_structures": {
        "easy": [
            {"q": "What is the difference between an array and a linked list?", "a": "Arrays have fixed size and O(1) random access. Linked lists are dynamic with O(1) insertion/deletion at head.", "keywords": ["array", "linked list", "O(1)", "random access", "dynamic"]},
            {"q": "What is a stack?", "a": "A stack is a LIFO data structure where elements are added and removed from the top.", "keywords": ["LIFO", "push", "pop", "top"]},
            {"q": "What is a queue?", "a": "A queue is a FIFO data structure where elements are added at rear and removed from front.", "keywords": ["FIFO", "enqueue", "dequeue", "front", "rear"]},
            {"q": "What is a binary tree?", "a": "A binary tree is a tree data structure where each node has at most two children.", "keywords": ["tree", "nodes", "children", "root"]},
            {"q": "What is a hash table?", "a": "A hash table stores key-value pairs using a hash function to compute index in an array.", "keywords": ["hash", "key-value", "collision", "O(1)"]},
        ],
        "medium": [
            {"q": "Explain the different types of binary trees.", "a": "Full: every node has 0 or 2 children. Complete: all levels filled except last. Perfect: all leaves at same level.", "keywords": ["full", "complete", "perfect", "levels"]},
            {"q": "How do you detect a cycle in a linked list?", "a": "Use Floyd's cycle detection algorithm with slow and fast pointers.", "keywords": ["Floyd", "slow pointer", "fast pointer", "cycle"]},
            {"q": "What is the difference between BFS and DFS?", "a": "BFS explores level by level using a queue. DFS explores depth-first using recursion/stack.", "keywords": ["BFS", "DFS", "queue", "recursion", "stack"]},
            {"q": "Explain heap data structure and its types.", "a": "A complete binary tree with heap property. Min-heap: parent ≤ children. Max-heap: parent ≥ children.", "keywords": ["heap", "complete binary tree", "min-heap", "max-heap"]},
            {"q": "What is a balanced binary search tree?", "a": "A BST where height difference between left and right subtrees is at most 1 (e.g., AVL, Red-Black).", "keywords": ["AVL", "Red-Black", "balanced", "height"]},
        ],
        "hard": [
            {"q": "Design a LRU Cache with O(1) operations.", "a": "Use a doubly linked list for recency and hash map for O(1) lookup.", "keywords": ["LRU", "doubly linked list", "hash map", "O(1)"]},
            {"q": "How would you implement a trie for autocomplete?", "a": "Use tree structure where each node is a character. Store word endings and frequency counts.", "keywords": ["trie", "autocomplete", "prefix", "nodes"]},
            {"q": "Explain segment tree and its applications.", "a": "Segment tree stores data in tree structure for range queries and updates in O(log n).", "keywords": ["segment tree", "range query", "lazy propagation"]},
        ]
    },
    "algorithms": {
        "easy": [
            {"q": "What is the time complexity of binary search?", "a": "O(log n) - search space halves each comparison.", "keywords": ["O(log n)", "halves", "comparison"]},
            {"q": "What is sorting?", "a": "Arranging elements in a specific order (ascending/descending).", "keywords": ["arrange", "order", "ascending", "descending"]},
            {"q": "What is recursion?", "a": "A function calling itself with a base case to terminate.", "keywords": ["function", "base case", "recursive"]},
            {"q": "What is big O notation?", "a": "Big O describes upper bound of algorithm's time/space complexity as input grows.", "keywords": ["complexity", "upper bound", "growth"]},
        ],
        "medium": [
            {"q": "Explain merge sort algorithm.", "a": "Divide array into halves, sort each half, merge sorted halves. Time: O(n log n).", "keywords": ["divide", "conquer", "merge", "O(n log n)"]},
            {"q": "What is dynamic programming?", "a": "Solving complex problems by breaking into overlapping subproblems and storing solutions.", "keywords": ["optimal substructure", "overlapping", "memoization", "tabulation"]},
            {"q": "Explain greedy algorithm approach.", "a": "Make locally optimal choice at each step, hoping for global optimum.", "keywords": ["local optimum", "global optimum", "choice"]},
            {"q": "What is two-pointer technique?", "a": "Use two pointers to solve problems by moving them based on conditions (e.g., sorted array).", "keywords": ["two pointers", "sorted array", "conditions"]},
        ],
        "hard": [
            {"q": "Explain the travelling salesman problem and its solution approaches.", "a": "Find shortest path visiting all cities. NP-hard, solutions: brute force O(n!), DP O(n²2^n), approximation.", "keywords": ["NP-hard", "TSP", "Hamiltonian cycle", "approximation"]},
            {"q": "How does the A* search algorithm work?", "a": "Uses f(n) = g(n) + h(n) where g is path cost, h is heuristic. Finds optimal path if h is admissible.", "keywords": ["heuristic", "admissible", "path cost", "optimal"]},
        ]
    },
    "oop": {
        "easy": [
            {"q": "What are the four pillars of OOP?", "a": "Encapsulation, Inheritance, Polymorphism, and Abstraction.", "keywords": ["encapsulation", "inheritance", "polymorphism", "abstraction"]},
            {"q": "What is a class?", "a": "A blueprint/template for creating objects with attributes and methods.", "keywords": ["blueprint", "object", "attributes", "methods"]},
            {"q": "What is an object?", "a": "An instance of a class that contains actual data and behavior.", "keywords": ["instance", "data", "behavior"]},
        ],
        "medium": [
            {"q": "Difference between method overloading and overriding?", "a": "Overloading: same class, same name, different parameters. Overriding: subclass provides specific implementation.", "keywords": ["overloading", "overriding", "subclass", "parameters"]},
            {"q": "What is inheritance?", "a": "Mechanism where a class inherits properties/methods from a parent class.", "keywords": ["parent", "child", "extends", "super"]},
            {"q": "Explain abstraction with example.", "a": "Hiding complex implementation details. Example: You use TV remote without knowing internal circuits.", "keywords": ["hide", "implementation", "interface"]},
        ],
        "hard": [
            {"q": "Explain SOLID principles.", "a": "S: Single Responsibility, O: Open/Closed, L: Liskov Substitution, I: Interface Segregation, D: Dependency Inversion.", "keywords": ["SOLID", "SRP", "OCP", "LSP", "ISP", "DIP"]},
            {"q": "What is the difference between composition and inheritance?", "a": "Composition: has-a relationship (object contains another). Inheritance: is-a relationship (class is a type of another).", "keywords": ["has-a", "is-a", "relationship"]},
        ]
    },
    "database": {
        "easy": [
            {"q": "What is a primary key?", "a": "Unique identifier for each row. Cannot be NULL.", "keywords": ["unique", "identifier", "NULL"]},
            {"q": "What is SQL?", "a": "Structured Query Language for managing and manipulating relational databases.", "keywords": ["query", "relational", "database"]},
            {"q": "What are DML and DDL?", "a": "DML: Data Manipulation Language (SELECT, INSERT, UPDATE). DDL: Data Definition Language (CREATE, ALTER, DROP).", "keywords": ["DML", "DDL", "query", "structure"]},
        ],
        "medium": [
            {"q": "Difference between INNER JOIN and LEFT JOIN?", "a": "INNER JOIN: only matching rows. LEFT JOIN: all rows from left + matching from right.", "keywords": ["INNER JOIN", "LEFT JOIN", "matching", "rows"]},
            {"q": "What is normalization?", "a": "Organizing data to reduce redundancy and improve integrity. 1NF, 2NF, 3NF, BCNF.", "keywords": ["normalization", "redundancy", "integrity", "BCNF"]},
            {"q": "What is indexing?", "a": "Data structure improving query speed by creating pointers to data locations.", "keywords": ["index", "query speed", "B-tree", "pointers"]},
        ],
        "hard": [
            {"q": "Explain ACID properties of transactions.", "a": "Atomicity: all or nothing. Consistency: valid state. Isolation: concurrent safe. Durability: permanent.", "keywords": ["Atomicity", "Consistency", "Isolation", "Durability"]},
            {"q": "What are database locks and their types?", "a": "Mechanisms to control concurrent access. Types: Shared (read), Exclusive (write), Deadlock prevention.", "keywords": ["locks", "shared", "exclusive", "deadlock"]},
        ]
    },
    "system_design": {
        "easy": [
            {"q": "What is scalability?", "a": "System's ability to handle increased load by adding resources.", "keywords": ["scalability", "load", "resources"]},
            {"q": "What is load balancing?", "a": "Distributing network traffic across multiple servers to ensure no single server is overwhelmed.", "keywords": ["load balancer", "traffic", "servers"]},
        ],
        "medium": [
            {"q": "Design a URL shortening service.", "a": "Use hash/Base62 for short codes. Store mapping in DB. Use Redis cache. Handle collisions.", "keywords": ["URL", "hash", "Base62", "Redis", "collision"]},
            {"q": "What is caching and where to use it?", "a": "Store frequently accessed data in fast memory. Use for read-heavy operations, expensive computations.", "keywords": ["cache", "memory", "read-heavy", "Redis", "Memcached"]},
        ],
        "hard": [
            {"q": "Design a real-time chat application like WhatsApp.", "a": "Use WebSocket for real-time. Store messages in MongoDB. Use Redis for presence. Implement E2E encryption.", "keywords": ["WebSocket", "MongoDB", "Redis", "E2E encryption", "presence"]},
            {"q": "Explain distributed system CAP theorem.", "a": "Cannot have Consistency, Availability, Partition tolerance simultaneously. Choose 2 of 3.", "keywords": ["CAP", "Consistency", "Availability", "Partition"]},
        ]
    },
    "behavioral": {
        "easy": [
            {"q": "Tell me about yourself.", "a": "Brief intro covering education, interests, and career goals related to role.", "keywords": ["education", "goals", "relevant"]},
            {"q": "What are your strengths?", "a": "Identify 2-3 relevant strengths with examples.", "keywords": ["strengths", "examples", "relevant"]},
            {"q": "What are your weaknesses?", "a": "Honest but improving. Mention a real weakness and steps taken to improve.", "keywords": ["weakness", "improving", "steps"]},
        ],
        "medium": [
            {"q": "Describe a challenging project.", "a": "Use STAR: Situation, Task, Action, Result. Focus on problem-solving.", "keywords": ["STAR", "challenge", "problem-solving", "result"]},
            {"q": "Why do you want to work here?", "a": "Show research: company values, products, culture match your goals.", "keywords": ["research", "values", "goals", "culture"]},
        ],
        "hard": [
            {"q": "Tell me about a time you failed.", "a": "Be honest about failure, take responsibility, explain what you learned.", "keywords": ["failure", "responsibility", "learning"]},
            {"q": "How do you handle conflict in a team?", "a": "Stay calm, listen, find common ground, focus on solutions.", "keywords": ["conflict", "communication", "solution"]},
        ]
    },
    "web_technologies": {
        "easy": [
            {"q": "Difference between GET and POST?", "a": "GET: parameters in URL, for fetching. POST: parameters in body, for creating.", "keywords": ["GET", "POST", "URL", "body", "idempotent"]},
            {"q": "What is HTTP?", "a": "Hypertext Transfer Protocol for communication between client and server.", "keywords": ["HTTP", "client", "server", "request", "response"]},
        ],
        "medium": [
            {"q": "What is REST API?", "a": "Architectural style using HTTP methods. Stateless, resource-based URLs, JSON responses.", "keywords": ["REST", "HTTP methods", "stateless", "JSON"]},
            {"q": "Explain the DOM.", "a": "Document Object Model - tree structure representing HTML/XML documents. Can be manipulated via JavaScript.", "keywords": ["DOM", "tree", "JavaScript", "manipulate"]},
        ],
        "hard": [
            {"q": "How does React work under the hood?", "a": "Virtual DOM for efficient updates. Components, state, props, hooks, reconciliation algorithm.", "keywords": ["Virtual DOM", "components", "state", "hooks", "reconciliation"]},
        ]
    },
    "machine_learning": {
        "easy": [
            {"q": "What is machine learning?", "a": "Field where computers learn from data without being explicitly programmed.", "keywords": ["learn", "data", "program"]},
            {"q": "Difference between supervised and unsupervised learning?", "a": "Supervised: labeled data. Unsupervised: unlabeled data, finds patterns.", "keywords": ["supervised", "unsupervised", "labeled", "patterns"]},
        ],
        "medium": [
            {"q": "Explain overfitting and underfitting.", "a": "Overfitting: model learns noise (high train, low test accuracy). Underfitting: too simple (low train accuracy).", "keywords": ["overfitting", "underfitting", "accuracy", "noise"]},
            {"q": "What is gradient descent?", "a": "Optimization algorithm minimizing loss by iteratively moving in opposite direction of gradient.", "keywords": ["gradient", "optimization", "loss", "iterative"]},
        ],
        "hard": [
            {"q": "Explain the bias-variance tradeoff.", "a": "High bias causes underfitting, high variance causes overfinding. Find optimal complexity.", "keywords": ["bias", "variance", "underfitting", "overfitting"]},
        ]
    }
}


def generate_questions(skills, interest, count=5):
    """Generate interview questions based on skills and interest"""
    questions = []
    
    # Map interests to categories
    category_map = {
        "backend": ["data_structures", "algorithms", "database", "system_design"],
        "frontend": ["web_technologies", "oop", "data_structures"],
        "fullstack": ["web_technologies", "database", "oop", "algorithms"],
        "data": ["machine_learning", "algorithms", "database"],
        "sde": ["data_structures", "algorithms", "oop", "system_design"],
        "ai": ["machine_learning", "algorithms", "python"],
        "default": ["data_structures", "algorithms", "oop", "behavioral"]
    }
    
    categories = category_map.get(interest.lower() if interest else "default", category_map["default"])
    
    # Get questions from each category
    for category in categories[:3]:
        if category in QUESTION_BANK:
            # Mix of difficulties
            for difficulty in ["easy", "medium", "hard"]:
                if category in QUESTION_BANK and difficulty in QUESTION_BANK[category]:
                    q_list = QUESTION_BANK[category][difficulty]
                    for q in q_list:
                        questions.append({
                            "category": category,
                            "difficulty": difficulty,
                            "question": q["q"],
                            "ideal_answer": q["a"],
                            "keywords": q["keywords"],
                            "points": {"easy": 10, "medium": 15, "hard": 20}[difficulty]
                        })
    
    # Add behavioral questions
    for difficulty in ["easy", "medium"]:
        for q in QUESTION_BANK["behavioral"][difficulty]:
            questions.append({
                "category": "behavioral",
                "difficulty": difficulty,
                "question": q["q"],
                "ideal_answer": q["a"],
                "keywords": q["keywords"],
                "points": {"easy": 10, "medium": 15}[difficulty]
            })
    
    # Shuffle and select questions
    random.shuffle(questions)
    return questions[:count]


def evaluate_answer(question_data, user_answer):
    """Evaluate user answer and provide feedback"""
    ideal_answer = question_data.get("ideal_answer", "")
    keywords = question_data.get("keywords", [])
    question = question_data.get("question", "")
    
    user_answer_lower = user_answer.lower()
    ideal_lower = ideal_answer.lower()
    
    # Find keywords present and missing
    keywords_found = []
    keywords_missing = []
    
    for keyword in keywords:
        if keyword.lower() in user_answer_lower:
            keywords_found.append(keyword)
        else:
            keywords_missing.append(keyword)
    
    # Calculate keyword match percentage
    if len(keywords) > 0:
        keyword_match = len(keywords_found) / len(keywords)
    else:
        keyword_match = 0
    
    # Answer length scoring
    min_length = 20
    length_score = min(len(user_answer) / min_length, 1.0) if len(user_answer) >= min_length else 0.3
    
    # Keyword importance (60%) + length (40%)
    raw_score = (keyword_match * 0.6 + length_score * 0.4) * 100
    
    # Adjust based on answer quality
    if len(user_answer) < 30:
        raw_score *= 0.5  # Too short
    elif "because" in user_answer_lower or "for example" in user_answer_lower:
        raw_score *= 1.1  # Good explanation
    
    # Cap score
    score = min(int(raw_score), 100)
    
    # Generate feedback
    feedback_parts = []
    
    if score >= 80:
        feedback_parts.append("✅ Excellent answer!")
    elif score >= 60:
        feedback_parts.append("👍 Good attempt!")
    elif score >= 40:
        feedback_parts.append("⚠️ Room for improvement.")
    else:
        feedback_parts.append("❌ Needs more preparation.")
    
    # Add specific feedback
    if keywords_found:
        feedback_parts.append(f"Covered {len(keywords_found)}/{len(keywords)} key concepts: {', '.join(keywords_found[:3])}")
    
    if keywords_missing:
        feedback_parts.append(f"Missing key points: {', '.join(keywords_missing[:3])}")
    
    if len(user_answer) < 50:
        feedback_parts.append("Tip: Provide more detailed explanations with examples.")
    
    # Strengths and improvements
    strengths = keywords_found[:3] if keywords_found else ["Attempted to answer"]
    improvements = keywords_missing[:3] if keywords_missing else ["Add more details"]
    
    if len(user_answer) < 50:
        improvements.append("Include more specific examples")
    
    return {
        "score": score,
        "feedback": " ".join(feedback_parts),
        "strengths": strengths,
        "improvements": improvements,
        "keywords_found": keywords_found,
        "keywords_missing": keywords_missing,
        "ideal_answer": ideal_answer
    }


def generate_follow_up(question_data, user_answer):
    """Generate follow-up questions based on user's answer"""
    score = evaluate_answer(question_data, user_answer).get("score", 0)
    
    # If answer was weak, ask clarifying question
    if score < 60:
        return "Can you explain that concept with a specific example from your experience?"
    
    # If answer was good, ask deeper question
    category = question_data.get("category", "")
    
    follow_ups = {
        "data_structures": "How would you implement this in production code? What are the space and time complexities?",
        "algorithms": "Can you think of an optimized solution? What's the time complexity of your approach?",
        "oop": "How would you design this in a real-world application? What design patterns would you use?",
        "database": "How would you scale this for millions of users? What indexing strategy would you use?",
        "system_design": "What are the potential bottlenecks in this design? How would you handle failures?",
        "behavioral": "What specific actions did you take in that situation? What was the measurable outcome?",
        "web_technologies": "How would you test this implementation? What security considerations are important?",
        "machine_learning": "How would you evaluate the model's performance? What metrics would you use?"
    }
    
    return follow_ups.get(category, "Can you elaborate on your answer with more details?")


def get_ai_evaluation(question, user_answer, api_key=None):
    """Get AI-powered evaluation using OpenAI"""
    if not OPENAI_AVAILABLE or not api_key:
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. Evaluate the candidate's answer and provide detailed feedback."
                },
                {
                    "role": "user",
                    "content": f"""
Question: {question}

Candidate's Answer: {user_answer}

Please evaluate this answer on:
1. Technical accuracy (0-100)
2. Completeness (0-100)
3. Clarity (0-100)
4. Provide specific feedback on strengths and weaknesses
5. Suggest improvements
6. Rate overall (0-100)

Format your response as JSON:
{{
    "technical_accuracy": score,
    "completeness": score,
    "clarity": score,
    "overall_score": score,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "feedback": "detailed feedback",
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""
                }
            ],
            temperature=0.3
        )
        
        # Parse JSON response
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        print(f"❌ AI evaluation error: {e}")
        return None


def get_learning_recommendation(weak_categories):
    """Get learning recommendations based on weak areas"""
    recommendations = {
        "data_structures": "Practice more problems on arrays, linked lists, trees, and graphs. Use LeetCode or GeeksforGeeks.",
        "algorithms": "Focus on sorting, searching, and dynamic programming. Practice coding problems daily.",
        "oop": "Review OOP concepts and design patterns. Build small projects to apply concepts.",
        "database": "Practice SQL queries and normalization. Learn about indexing and query optimization.",
        "system_design": "Study distributed systems. Practice designing scalable applications.",
        "behavioral": "Prepare STAR method answers. Research common behavioral questions.",
        "web_technologies": "Build web projects to understand HTML, CSS, JavaScript, and frameworks.",
        "machine_learning": "Learn ML fundamentals. Practice with scikit-learn and real datasets."
    }
    
    return [recommendations.get(cat, "Keep practicing!") for cat in weak_categories]


print("✅ InterviewPro AI Engine Loaded - Ready for intelligent interviews")
