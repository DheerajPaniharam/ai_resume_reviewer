from flask import Flask, render_template, request
from utils.text_extractor import extract_text
from utils.resume_analyzer import analyze_resume

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files["resume"]
        if file:
            text = extract_text(file)
            result = analyze_resume(text)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
    