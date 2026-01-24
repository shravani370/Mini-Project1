def get_mock_questions():
    return [
        "Tell me about yourself.",
        "What are your technical skills?",
        "Explain one project you have worked on.",
        "What are your strengths and weaknesses?",
        "Why should we hire you?"
    ]


def evaluate_answers(answers):
    score = 0
    feedback = []

    for ans in answers:
        if len(ans.strip()) > 30:
            score += 2
            feedback.append("Good detailed answer")
        elif len(ans.strip()) > 10:
            score += 1
            feedback.append("Answer is okay, can be improved")
        else:
            feedback.append("Answer too short")

    return {
        "score": score,
        "out_of": 10,
        "feedback": feedback
    }