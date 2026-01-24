"""
ML-based Placement Prediction Module
Uses logistic regression to predict placement likelihood based on student data
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
import os

# Dataset path
DATA_PATH = "placement_data.csv"


def load_and_preprocess_data():
    """Load and preprocess the placement data"""
    try:
        data = pd.read_csv(DATA_PATH)
        
        # Normalize text data
        data["skills"] = data["skills"].str.lower()
        data["interest"] = data["interest"].str.lower()
        data["year"] = data["year"].str.lower()
        
        # Add 'other' category safety
        if "other" not in data["skills"].values:
            new_row = {
                "year": data["year"].iloc[0] if len(data) > 0 else "1st",
                "skills": "other",
                "interest": data["interest"].iloc[0] if len(data) > 0 else "general",
                "cgpa": data["cgpa"].mean() if len(data) > 0 else 7.0,
                "placed": 0
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        
        return data
    except FileNotFoundError:
        # Create dummy data if file not found
        return create_dummy_data()


def create_dummy_data():
    """Create dummy data for testing"""
    data = pd.DataFrame({
        "year": ["3rd", "4th", "3rd", "4th", "2nd", "3rd", "4th", "2nd"],
        "skills": ["python", "java", "python", "python", "javascript", "java", "python", "c++"],
        "interest": ["ai", "web", "ai", "backend", "web", "android", "ai", "sde"],
        "cgpa": [7.5, 8.0, 8.2, 7.8, 8.5, 6.9, 9.0, 7.5],
        "placed": [0, 1, 1, 1, 0, 0, 1, 0]
    })
    return data


def train_model():
    """Train the placement prediction model"""
    data = load_and_preprocess_data()
    
    # Encode categorical variables
    le_skill = LabelEncoder()
    le_interest = LabelEncoder()
    le_year = LabelEncoder()
    
    data["skills_encoded"] = le_skill.fit_transform(data["skills"])
    data["interest_encoded"] = le_interest.fit_transform(data["interest"])
    data["year_encoded"] = le_year.fit_transform(data["year"])
    
    # Features and target
    X = data[["year_encoded", "skills_encoded", "interest_encoded", "cgpa"]]
    y = data["placed"]
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, model.predict(X_test))
    
    return model, accuracy, {
        "le_skill": le_skill,
        "le_interest": le_interest,
        "le_year": le_year
    }


def analyze_student(year, skills, interest, cgpa):
    """
    Analyze a student's placement prediction
    
    Args:
        year: Year of study (e.g., "3rd")
        skills: Technical skills (e.g., "Python, AI")
        interest: Area of interest (e.g., "AI")
        cgpa: CGPA score
        
    Returns:
        dict: Placement prediction and model accuracy
    """
    # Train model and get encoders
    model, accuracy, encoders = train_model()
    
    le_skill = encoders["le_skill"]
    le_interest = encoders["le_interest"]
    le_year = encoders["le_year"]
    
    # Normalize input
    year_lower = year.lower()
    skills_lower = skills.lower()
    interest_lower = interest.lower()
    
    # Safe encoding with fallback
    if year_lower not in le_year.classes_:
        year_lower = le_year.classes_[0] if len(le_year.classes_) > 0 else "3rd"
    
    # Extract primary skill
    primary_skill = skills_lower.split(",")[0].strip()
    if primary_skill not in le_skill.classes_:
        primary_skill = "python" if "python" in primary_skill else "other"
    
    if interest_lower not in le_interest.classes_:
        interest_lower = "general"
    
    try:
        year_encoded = le_year.transform([year_lower])[0]
        skills_encoded = le_skill.transform([primary_skill])[0]
        interest_encoded = le_interest.transform([interest_lower])[0]
        
        # Prepare input
        input_data = [[year_encoded, skills_encoded, interest_encoded, float(cgpa)]]
        
        # Predict
        prediction = model.predict(input_data)[0]
        
        return {
            "placement_prediction": "Placed ✅" if prediction == 1 else "Not Placed ❌",
            "model_accuracy": round(accuracy * 100, 2),
            "raw_prediction": prediction
        }
    except Exception as e:
        return {
            "placement_prediction": "Unknown",
            "model_accuracy": round(accuracy * 100, 2),
            "error": str(e)
        }


def get_mock_questions():
    """Get mock interview questions"""
    return [
        "Tell me about yourself and your background.",
        "What are your technical skills and how have you applied them?",
        "Explain one project you have worked on in detail.",
        "What are your strengths and weaknesses?",
        "Why are you interested in this field/position?"
    ]


def evaluate_answers(answers):
    """
    Evaluate mock interview answers
    
    Args:
        answers: List of student answers
        
    Returns:
        dict: Score and feedback
    """
    score = 0
    feedback = []
    
    for ans in answers:
        if len(ans.strip()) > 50:
            score += 2
            feedback.append("Excellent detailed answer")
        elif len(ans.strip()) > 30:
            score += 1.5
            feedback.append("Good answer with reasonable detail")
        elif len(ans.strip()) > 10:
            score += 1
            feedback.append("Answer is adequate but could be more detailed")
        else:
            score += 0.5
            feedback.append("Answer too short - provide more details")
    
    return {
        "score": score,
        "out_of": 10,
        "feedback": feedback,
        "percentage": round((score / 10) * 100, 1)
    }


if __name__ == "__main__":
    # Test the model
    result = analyze_student("3rd", "Python, AI", "AI", 8.0)
    print(f"Prediction: {result}")
    print(f"Accuracy: {result.get('model_accuracy', 'N/A')}%")

