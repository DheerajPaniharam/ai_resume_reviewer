import datetime
import os

from flask import Flask, render_template, request
from utils.text_extractor import ALLOWED_EXTENSIONS, extract_text
from utils.resume_analyzer import analyze_resume

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["ANALYSIS_HISTORY"] = []


def allowed_file(filename):
    return "." in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    history = list(reversed(app.config["ANALYSIS_HISTORY"]))[:5]

    if request.method == "POST":
        resume_text = request.form.get("resume_text", "").strip()
        job_title = request.form.get("job_title", "").strip()
        job_description = request.form.get("job_description", "").strip()
        file = request.files.get("resume")

        if resume_text:
            text = resume_text
        elif file and file.filename:
            if not allowed_file(file.filename):
                error = "Supported formats are PDF, DOCX, and TXT."
                text = None
            else:
                try:
                    text = extract_text(file)
                except Exception as e:
                    error = f"Error reading document: {str(e)}"
                    text = None
        else:
            error = "Please provide resume text or upload a supported file."
            text = None

        if text is not None:
            if not text.strip():
                error = "Could not extract text from the provided resume content."
            else:
                result = analyze_resume(text, target_job=job_title, job_description=job_description)
                app.config["ANALYSIS_HISTORY"].append({
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "score": result["score"],
                    "job_title": job_title or "General Resume",
                    "sections": result["sections_found"],
                    "keywords": result["keywords_found"][:5],
                })
                history = list(reversed(app.config["ANALYSIS_HISTORY"]))[:5]

    return render_template("index.html", result=result, error=error, history=history)


if __name__ == "__main__":
    app.run(debug=True)