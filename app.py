import os
import re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf"}

SKILLS = [
    "python", "java", "javascript", "html", "css", "react", "node", "flask",
    "django", "sql", "mysql", "mongodb", "git", "github", "machine learning",
    "data science", "pandas", "numpy", "scikit-learn", "tensorflow",
    "power bi", "excel", "communication", "leadership", "problem solving",
    "teamwork", "api", "rest api", "bootstrap", "tailwind"
]

IMPORTANT_KEYWORDS = [
    "experience", "project", "skills", "education", "certification",
    "internship", "achievement", "responsibility", "summary", "objective",
    "github", "linkedin", "portfolio"
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    text = ""

    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "

    except Exception:
        text = ""

    return text.lower()


def calculate_ats_score(text, found_skills):
    score = 0

    if len(text) > 500:
        score += 20
    elif len(text) > 250:
        score += 10

    if len(found_skills) >= 8:
        score += 30
    elif len(found_skills) >= 5:
        score += 20
    elif len(found_skills) >= 2:
        score += 10

    keyword_count = 0
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in text:
            keyword_count += 1

    score += min(keyword_count * 4, 30)

    if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text):
        score += 10

    if "linkedin" in text or "github" in text:
        score += 10

    return min(score, 100)


def analyze_resume(text):
    found_skills = []
    missing_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill.title())
        else:
            missing_skills.append(skill.title())

    ats_score = calculate_ats_score(text, found_skills)

    tips = []

    if ats_score < 60:
        tips.append("Your resume needs improvement. Add more relevant skills, projects, and measurable achievements.")

    if "github" not in text:
        tips.append("Add your GitHub profile link to improve technical credibility.")

    if "linkedin" not in text:
        tips.append("Add your LinkedIn profile link for professional visibility.")

    if "project" not in text:
        tips.append("Add a dedicated Projects section with technologies used and outcomes.")

    if "internship" not in text and "experience" not in text:
        tips.append("Add internship, training, freelance, or academic project experience.")

    if len(found_skills) < 5:
        tips.append("Add more technical skills related to your target job role.")

    if not tips:
        tips.append("Good resume! You can improve further by adding quantified achievements and role-specific keywords.")

    return {
        "ats_score": ats_score,
        "found_skills": found_skills,
        "missing_skills": missing_skills[:12],
        "tips": tips,
        "word_count": len(text.split())
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return render_template("index.html", error="Please upload a resume PDF.")

    file = request.files["resume"]

    if file.filename == "":
        return render_template("index.html", error="No file selected.")

    if file and allowed_file(file.filename):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        resume_text = extract_text_from_pdf(file_path)

        if not resume_text.strip():
            return render_template("index.html", error="Could not read this PDF. Please upload a text-based resume PDF.")

        result = analyze_resume(resume_text)

        return render_template("result.html", result=result)

    return render_template("index.html", error="Only PDF files are allowed.")


if __name__ == "__main__":
    app.run(debug=True)