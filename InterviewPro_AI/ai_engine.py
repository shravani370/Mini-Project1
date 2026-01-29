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


def generate_questions(topics, interest, count=5):
    """Generate interview questions based on selected topics and role interest"""
    questions = []
    
    # Parse topics - handle various formats
    if not topics or topics == "all" or (isinstance(topics, str) and topics.lower() == "all"):
        # If no specific topics or "all" selected, use interest-based categories
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
    else:
        # Parse selected topics
        if isinstance(topics, str):
            # Handle comma-separated string
            topics_list = [t.strip().lower() for t in topics.split(",") if t.strip()]
        elif isinstance(topics, list):
            topics_list = [t.strip().lower() for t in topics if t.strip()]
        else:
            topics_list = []
        
        # Map topic names to categories
        topic_to_category = {
            "dsa": "data_structures",
            "data structures": "data_structures",
            "data structures and algorithms": "data_structures",
            "algorithms": "algorithms",
            "oop": "oop",
            "object oriented programming": "oop",
            "database": "database",
            "sql": "database",
            "system design": "system_design",
            "web": "web_technologies",
            "web technologies": "web_technologies",
            "machine learning": "machine_learning",
            "ml": "machine_learning",
            "behavioral": "behavioral",
        }
        
        categories = []
        for topic in topics_list:
            if topic in topic_to_category:
                categories.append(topic_to_category[topic])
            else:
                categories.append(topic)  # Use as-is
    
    # Calculate how many categories to use and questions per category
    num_categories = min(len(categories), max(2, (count + 1) // 2))
    selected_categories = categories[:num_categories]
    
    # Distribute questions evenly
    base_questions = count // num_categories if num_categories > 0 else count
    extra = count % num_categories if num_categories > 0 else 0
    
    for idx, category in enumerate(selected_categories):
        if category not in QUESTION_BANK:
            continue
        
        # Get questions for this category
        category_questions = []
        for difficulty in ["easy", "medium", "hard"]:
            if difficulty in QUESTION_BANK[category]:
                for q in QUESTION_BANK[category][difficulty]:
                    category_questions.append({
                        "category": category,
                        "difficulty": difficulty,
                        "question": q["q"],
                        "ideal_answer": q["a"],
                        "keywords": q["keywords"],
                        "points": {"easy": 10, "medium": 15, "hard": 20}[difficulty]
                    })
        
        # Shuffle and select specific number
        random.shuffle(category_questions)
        num_to_take = base_questions + (1 if idx < extra else 0)
        questions.extend(category_questions[:num_to_take])
    
    # Shuffle final result
    random.shuffle(questions)
    return questions[:count]


def evaluate_answer(question_data, user_answer):
    """Evaluate user answer and provide accurate feedback"""
    ideal_answer = question_data.get("ideal_answer", "")
    keywords = question_data.get("keywords", [])
    question = question_data.get("question", "")
    difficulty = question_data.get("difficulty", "medium")
    
    user_answer_lower = user_answer.lower()
    ideal_lower = ideal_answer.lower()
    
    if not user_answer.strip():
        return {
            "score": 0,
            "feedback": "❌ No answer provided. Please attempt the question.",
            "strengths": [],
            "improvements": ["Provide an answer to the question"],
            "keywords_found": [],
            "keywords_missing": keywords,
            "ideal_answer": ideal_answer
        }
    
    # Find keywords present and missing
    keywords_found = []
    keywords_missing = []
    
    for keyword in keywords:
        if keyword.lower() in user_answer_lower:
            keywords_found.append(keyword)
        else:
            keywords_missing.append(keyword)
    
    # Calculate comprehensive score
    score = 0
    
    # 1. Keyword Coverage (30%)
    keyword_coverage = len(keywords_found) / len(keywords) if keywords else 0
    keyword_score = keyword_coverage * 30
    
    # 2. Answer Length Appropriateness (20%)
    # Expected length varies by difficulty
    expected_min = {"easy": 30, "medium": 60, "hard": 100}
    expected_max = {"easy": 150, "medium": 300, "hard": 500}
    
    min_len = expected_min.get(difficulty, 60)
    max_len = expected_max.get(difficulty, 300)
    answer_len = len(user_answer)
    
    if answer_len < min_len:
        length_score = (answer_len / min_len) * 10
    elif answer_len > max_len:
        length_score = max(0, 10 - (answer_len - max_len) / 100 * 5)
    else:
        length_score = 10
    
    # 3. Technical Content Analysis (25%)
    technical_score = 0
    
    # Check for technical indicators
    technical_indicators = [
        "because", "for example", "such as", "instance", "this means",
        "the reason", "specifically", "in particular", "which is"
    ]
    
    explanation_words = sum(1 for word in technical_indicators if word in user_answer_lower)
    technical_score = min(25, explanation_words * 5)
    
    # Bonus for specific technical terms not in keywords
    bonus_terms = ["complexity", "algorithm", "implementation", "optimization", "efficient"]
    bonus_score = sum(3 for term in bonus_terms if term in user_answer_lower)
    technical_score = min(25, technical_score + bonus_score)
    
    # 4. Clarity and Structure (15%)
    clarity_score = 0
    
    # Check for structured response indicators
    structure_indicators = ["first", "second", "third", "step", "however", "therefore"]
    structure_words = sum(1 for word in structure_indicators if word in user_answer_lower)
    clarity_score = min(15, structure_words * 3)
    
    # Check for proper sentences
    sentences = user_answer.split('.')
    if len(sentences) >= 2:
        clarity_score += 5
    if len(sentences) >= 4:
        clarity_score += 5
    
    # 5. Relevance Check (10%)
    relevance_score = 10
    # Check if answer is relevant by looking for key question words
    question_words = ["what", "how", "why", "explain", "describe", "difference"]
    if any(word in user_answer_lower for word in question_words[:3]):
        relevance_score = 10
    else:
        # Check for direct answer indicators
        if len(user_answer) > 20:
            relevance_score = 8
        else:
            relevance_score = 5
    
    # Calculate total score
    total_score = keyword_score + length_score + technical_score + clarity_score + relevance_score
    
    # Difficulty adjustment
    difficulty_multiplier = {"easy": 1.1, "medium": 1.0, "hard": 0.9}
    total_score = total_score * difficulty_multiplier.get(difficulty, 1.0)
    
    # Cap score between 0-100
    score = min(100, max(0, int(total_score)))
    
    # Generate feedback
    feedback_parts = []
    
    if score >= 85:
        feedback_parts.append("🌟 Excellent answer! Very well articulated!")
    elif score >= 70:
        feedback_parts.append("✅ Strong answer! Good technical coverage.")
    elif score >= 55:
        feedback_parts.append("👍 Good attempt! Room for improvement.")
    elif score >= 40:
        feedback_parts.append("⚠️ Fair answer. Needs more depth.")
    else:
        feedback_parts.append("💪 Keep practicing! Focus on key concepts.")
    
    # Add specific feedback
    coverage_pct = int(keyword_coverage * 100)
    feedback_parts.append(f"Key concepts covered: {coverage_pct}%")
    
    if keywords_missing and len(keywords_missing) <= 3:
        feedback_parts.append(f"Consider including: {', '.join(keywords_missing)}")
    
    # Add length feedback
    if answer_len < min_len:
        feedback_parts.append(f"Tip: Expand your answer (aim for {min_len}+ characters)")
    elif answer_len > max_len:
        feedback_parts.append("Tip: Be more concise while covering key points")
    
    # Strengths and improvements
    strengths = []
    if keyword_coverage >= 0.6:
        strengths.append("Good keyword coverage")
    if len(user_answer) >= min_len:
        strengths.append("Adequate answer length")
    if technical_score >= 15:
        strengths.append("Clear technical explanation")
    if clarity_score >= 10:
        strengths.append("Well-structured response")
    
    if not strengths:
        strengths = keywords_found[:2] if keywords_found else ["Attempted the question"]
    
    improvements = []
    if keyword_coverage < 0.6:
        improvements.append("Include more key technical terms")
    if answer_len < min_len:
        improvements.append("Provide more detailed explanations")
    if technical_score < 10:
        improvements.append("Add examples or use cases")
    if clarity_score < 8:
        improvements.append("Structure your answer better")
    
    if not improvements:
        improvements = ["Maintain this quality!"] if score >= 70 else ["Review the ideal answer"]
    
    return {
        "score": score,
        "feedback": " ".join(feedback_parts),
        "strengths": strengths[:3],
        "improvements": improvements[:3],
        "keywords_found": keywords_found,
        "keywords_missing": keywords_missing,
        "ideal_answer": ideal_answer,
        "analysis": {
            "keyword_score": round(keyword_score, 1),
            "length_score": round(length_score, 1),
            "technical_score": round(technical_score, 1),
            "clarity_score": round(clarity_score, 1),
            "relevance_score": round(relevance_score, 1)
        }
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
