from flask import Flask, render_template, request, redirect, session, send_file
from datetime import datetime
import random
import io

# PDF Libraries
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import PageBreak
from reportlab.platypus.paragraph import ParagraphStyle
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import PageTemplate
from reportlab.platypus.flowables import KeepTogether
from reportlab.platypus import Paragraph
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
app.secret_key = "smart_quiz_system"

leaderboard = []


# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# START QUIZ (AUTO QUESTIONS)
# ==========================
@app.route("/start", methods=["POST"])
def start():

    student_name = request.form.get("student_name")
    topic = request.form.get("topic")

    session["student_name"] = student_name
    session["topic"] = topic
    session["score"] = 0
    session["current_question"] = 0
    session["answers"] = []

    # 🔥 Smart Question Generator (Different Every Time)
    verbs = ["Explain", "Define", "Describe", "What is", "Why is", "How does"]
    concepts = ["basic concept", "key feature", "main advantage", "important use"]

    generated_questions = []

    for i in range(5):

        verb = random.choice(verbs)
        concept = random.choice(concepts)

        correct_answer = f"{topic} {concept}"

        wrong_options = [
            f"Not related to {topic}",
            f"Wrong idea about {topic}",
            f"Incorrect {topic} concept"
        ]

        options = wrong_options + [correct_answer]
        random.shuffle(options)

        generated_questions.append({
            "question": f"{verb} the {concept} of {topic}",
            "options": options,
            "answer": correct_answer,
            "topic": topic
        })

    session["questions"] = generated_questions

    return redirect("/quiz")


# ==========================
# QUIZ PAGE
# ==========================
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    questions = session.get("questions", [])
    index = session.get("current_question", 0)

    if index >= len(questions):
        return redirect("/result")

    question = questions[index]

    if request.method == "POST":

        selected_answer = request.form.get("answer")

        # 🔥 If timer auto submits and no answer selected
        if selected_answer is None:
            selected_answer = "No Answer"

        session["answers"].append(selected_answer)

        if selected_answer == question["answer"]:
            session["score"] += 1
            session["feedback"] = "✅ Correct Answer!"
        else:
            session["feedback"] = f"❌ Time Over or Wrong! Learn {question['topic']}"

        session["current_question"] += 1

        return redirect("/quiz")

    return render_template(
        "quiz.html",
        question=question,
        feedback=session.get("feedback")
    )


# ==========================
# RESULT PAGE
# ==========================
@app.route("/result")
def result():

    student_name = session.get("student_name")
    questions = session.get("questions", [])
    answers = session.get("answers", [])
    score = session.get("score", 0)

    total = len(questions)

    if total == 0:
        return redirect("/")

    percentage = round((score / total) * 100, 2)

    # Topic Analysis
    topic_analysis = {}

    for i in range(total):

        topic = questions[i]["topic"]

        if topic not in topic_analysis:
            topic_analysis[topic] = 0

        if i < len(answers) and answers[i] == questions[i]["answer"]:
            topic_analysis[topic] += 1

    for topic in topic_analysis:
        topic_analysis[topic] = round((topic_analysis[topic] / total) * 100, 2)

    leaderboard.append({
        "name": student_name,
        "score": score,
        "percentage": percentage,
        "topic": session.get("topic"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    return render_template(
        "result.html",
        student_name=student_name,
        score=score,
        total=total,
        percentage=percentage,
        topic_analysis=topic_analysis
    )


# ==========================
# LEADERBOARD
# ==========================
@app.route("/leaderboard")
def leaderboard_page():

    sorted_board = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    return render_template("leaderboard.html", leaderboard=sorted_board)


# ==========================
# DOWNLOAD RESULT AS PDF
# ==========================
@app.route("/download-pdf")
def download_pdf():

    student_name = session.get("student_name")
    score = session.get("score", 0)
    questions = session.get("questions", [])

    total = len(questions)
    percentage = round((score / total) * 100, 2) if total > 0 else 0

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Quiz Result Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Student Name: {student_name}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Score: {score} / {total}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Percentage: {percentage}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Generated Questions:", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for q in questions:
        elements.append(Paragraph(f"• {q['question']}", styles["Normal"]))
        elements.append(Spacer(1, 5))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Quiz_Result.pdf",
        mimetype="application/pdf"
    )


# ==========================
# RUN APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)