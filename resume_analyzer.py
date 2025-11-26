import spacy

nlp = spacy.load("en_core_web_sm")

# Predefined keywords (customize for your project domain)
KEYWORDS = [
    "Python", "Machine Learning", "Communication", "Leadership",
    "Data Analysis", "Teamwork", "Java", "SQL", "Problem Solving"
]

def analyze_resume(text):
    """Analyze resume text using NLP and keyword matching."""
    doc = nlp(text)

    found_keywords = [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    keyword_score = (len(found_keywords) / len(KEYWORDS)) * 100

    feedback = []
    if keyword_score < 50:
        feedback.append("Add more technical and soft skills related to your role.")
    if "project" not in text.lower():
        feedback.append("Include a Projects section to highlight your work.")
    if "education" not in text.lower():
        feedback.append("Mention your Education details clearly.")
    if len(feedback) == 0:
        feedback.append("Excellent! Your resume covers most essential areas.")

    result = {
        "score": round(keyword_score, 2),
        "keywords_found": found_keywords,
        "feedback": feedback
    }
    return result
