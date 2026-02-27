from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"

# 🏆 Temporary Storage for Leaderboard
leaderboard = []

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- START QUIZ ----------------
@app.route("/start", methods=["POST"])
def start_quiz():
    student_name = request.form.get("student_name")

    questions = [

        # Math
        {"question": "5 + 3 = ?", "options": ["6", "7", "8", "9"], "answer": "8", "topic": "Math"},
        {"question": "10 × 2 = ?", "options": ["10", "15", "20", "25"], "answer": "20", "topic": "Math"},

        # Science
        {"question": "Water formula?", "options": ["CO2", "H2O", "O2", "NaCl"], "answer": "H2O", "topic": "Science"},
        {"question": "Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars", "topic": "Science"},

        # GK
        {"question": "Capital of India?", "options": ["Mumbai", "Delhi", "Chennai", "Kolkata"], "answer": "Delhi", "topic": "GK"},
        {"question": "Father of Nation?", "options": ["Nehru", "Gandhi", "Bose", "Ambedkar"], "answer": "Gandhi", "topic": "GK"},
    ]

    session["student_name"] = student_name
    session["questions"] = questions
    session["current_question"] = 0
    session["score"] = 0
    session["topic_scores"] = {}

    return redirect(url_for("quiz"))


# ---------------- QUIZ ----------------
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = session.get("questions", [])
    current = session.get("current_question", 0)

    if request.method == "POST":
        if current < len(questions):
            selected = request.form.get("answer")
            correct = questions[current]["answer"]
            topic = questions[current]["topic"]

            if topic not in session["topic_scores"]:
                session["topic_scores"][topic] = {"correct": 0, "total": 0}

            session["topic_scores"][topic]["total"] += 1

            if selected == correct:
                session["score"] += 1
                session["topic_scores"][topic]["correct"] += 1

            session["current_question"] = current + 1

        return redirect(url_for("quiz"))

    if current >= len(questions):
        return redirect(url_for("result"))

    return render_template("quiz.html", question=questions[current])


# ---------------- RESULT ----------------
@app.route("/result")
def result():
    student_name = session.get("student_name")
    score = session.get("score")
    questions = session.get("questions")
    topic_scores = session.get("topic_scores")

    total = len(questions)
    percentage = round((score / total) * 100)

    # 🏆 Save to Leaderboard
    leaderboard.append({
        "name": student_name,
        "score": score,
        "percentage": percentage,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    # Sort Leaderboard by percentage (highest first)
    leaderboard.sort(key=lambda x: x["percentage"], reverse=True)

    topic_analysis = {}
    for topic, data in topic_scores.items():
        topic_percentage = round((data["correct"] / data["total"]) * 100)
        topic_analysis[topic] = topic_percentage

    return render_template("result.html",
                           student_name=student_name,
                           score=score,
                           total=total,
                           percentage=percentage,
                           topic_analysis=topic_analysis)


# ---------------- LEADERBOARD PAGE ----------------
@app.route("/leaderboard")
def show_leaderboard():
    return render_template("leaderboard.html", leaderboard=leaderboard)


if __name__ == "__main__":
    app.run(debug=True)