from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import random

# 🔥 If you want real AI question generation later, we can connect OpenAI API.
# For now we generate questions automatically using topic.

app = Flask(__name__)
app.secret_key = "smart_quiz_system"

leaderboard = []


# ==========================================
# HOME PAGE
# Student enters Name + Topic
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# START QUIZ
# Store Topic + Generate Questions
# ==========================================
@app.route("/start", methods=["POST"])
def start():

    student_name = request.form.get("student_name")
    topic = request.form.get("topic")

    session["student_name"] = student_name
    session["topic"] = topic
    session["score"] = 0
    session["current_question"] = 0
    session["answers"] = []

    # 🔥 Smart Question Generator
    verbs = [
        "Explain",
        "Define",
        "Describe",
        "What is",
        "Why is",
        "How does"
    ]

    concepts = [
        "basic concept",
        "key feature",
        "main advantage",
        "important use",
        "core principle"
    ]

    generated_questions = []

    for i in range(5):

        verb = random.choice(verbs)
        concept = random.choice(concepts)

        correct_answer = f"{topic} {concept}"

        wrong_options = [
            f"Wrong idea about {topic}",
            f"Not related to {topic}",
            f"Incorrect {topic} concept",
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


# ==========================================
# QUIZ PAGE
# ==========================================
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    questions = session.get("questions", [])
    index = session.get("current_question", 0)

    if index >= len(questions):
        return redirect("/result")

    question = questions[index]

    if request.method == "POST":

        selected_answer = request.form.get("answer")
        session["answers"].append(selected_answer)

        # ✅ Check Answer
        if selected_answer == question["answer"]:
            session["score"] += 1
            session["feedback"] = "✅ Correct Answer!"
        else:
            session["feedback"] = f"❌ Wrong! Learn more about {question['topic']}"

        session["current_question"] += 1

        return redirect("/quiz")

    return render_template(
        "quiz.html",
        question=question,
        feedback=session.get("feedback")
    )


# ==========================================
# RESULT PAGE
# ==========================================
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

    # ✅ Create topic_analysis safely
    topic_analysis = {}

    for i in range(total):
        topic = questions[i]["topic"]

        if topic not in topic_analysis:
            topic_analysis[topic] = 0

        if i < len(answers) and answers[i] == questions[i]["answer"]:
            topic_analysis[topic] += 1

    # Convert to percentage
    for topic in topic_analysis:
        topic_analysis[topic] = round((topic_analysis[topic] / total) * 100, 2)

    return render_template(
        "result.html",
        student_name=student_name,
        score=score,
        total=total,
        percentage=percentage,
        topic_analysis=topic_analysis   # 🔥 IMPORTANT
    )

    return render_template(
        "result.html",
        student_name=student_name,
        score=score,
        total=total,
        percentage=percentage,
        topic=topic
    )


# ==========================================
# LEADERBOARD
# ==========================================
@app.route("/leaderboard")
def leaderboard_page():

    sorted_board = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    return render_template("leaderboard.html", leaderboard=sorted_board)


if __name__ == "__main__":
    app.run(debug=True)