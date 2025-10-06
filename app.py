from flask import Flask, render_template, request, send_file
from utils.summarizer import generate_summary
from utils.question_gen import generate_questions
from utils.mcq_gen import generate_mcqs
from utils.text_processing import extract_text_from_pdf
from pymongo import MongoClient
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017/")
db = client["study_partner"]
sessions = db["sessions"]


last_result = {}


@app.route("/", methods=["GET", "POST"])
def index():
    global last_result
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        input_text = request.form.get("notes")

        text = ""
        if uploaded_file and uploaded_file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        elif input_text:
            text = input_text

        if not text.strip():
            return render_template("index.html", error=" Please enter text or upload PDF")

        
        summary = generate_summary(text)
        
        summary = summary.replace("•", "\n•").strip()

        questions = generate_questions(text, limit=5)
        mcqs = generate_mcqs(text, limit=10)

        indexed_mcqs = list(enumerate(mcqs))  

        
        doc = {
            "text": text,
            "summary": summary,
            "questions": questions,
            "mcqs": mcqs,
            "created_at": datetime.datetime.now()
        }
        sessions.insert_one(doc)

        
        last_result = {
            "summary": summary,
            "questions": questions,
            "mcqs": mcqs
        }

        return render_template(
            "result.html",
            summary=summary,
            questions=questions,
            indexed_mcqs=indexed_mcqs
        )

    return render_template("index.html")



@app.route("/submit_answers", methods=["POST"])
def submit_answers():
    global last_result
    user_answers = {}
    mcqs = last_result.get("mcqs", [])

    
    for i, mcq in enumerate(mcqs):
        ans = request.form.get(f"q{i}")
        user_answers[f"Q{i+1}"] = ans

    
    correct_answers = [m['answer'] for m in mcqs]
    score = sum(
        1 for i in range(len(mcqs))
        if user_answers.get(f"Q{i+1}") == correct_answers[i]
    )

    return render_template(
        "score.html",
        user_answers=user_answers,
        correct_answers=correct_answers,
        score=score,
        total=len(mcqs)
    )


 
@app.route("/download/<format>")
def download(format):
    global last_result
    if not last_result:
        return " No results available for download."

    if format == "txt":
        content = f"Summary:\n{last_result['summary']}\n\nQuestions:\n"
        for q in last_result['questions']:
            content += f"- {q}\n"
        content += "\nMCQs:\n"
        for i, mcq in enumerate(last_result['mcqs']):
            content += f"Q{i+1}: {mcq['question']}\n"
            for opt in mcq['options']:
                content += f"   - {opt}\n"
            content += f"Answer: {mcq['answer']}\n\n"

        return send_file(
            BytesIO(content.encode("utf-8")),
            as_attachment=True,
            download_name="study_partner_results.txt",
            mimetype="text/plain"
        )

    elif format == "pdf":
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph("AI Study Partner Results", styles["Heading1"]), Spacer(1, 12)]

        story.append(Paragraph("Summary:", styles["Heading2"]))
        story.append(Paragraph(last_result['summary'], styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Questions:", styles["Heading2"]))
        for q in last_result['questions']:
            story.append(Paragraph(q, styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("MCQs:", styles["Heading2"]))
        for i, mcq in enumerate(last_result['mcqs']):
            story.append(Paragraph(f"Q{i+1}: {mcq['question']}", styles["Normal"]))
            for opt in mcq['options']:
                story.append(Paragraph(f" - {opt}", styles["Normal"]))
            story.append(Paragraph(f"Answer: {mcq['answer']}", styles["Italic"]))
            story.append(Spacer(1, 8))

        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="study_partner_results.pdf",
            mimetype="application/pdf"
        )

    return "Invalid format."



@app.route("/history")
def history():
    records = sessions.find().sort("created_at", -1).limit(10)
    return render_template("history.html", records=records)
 
if __name__ == "__main__":
    app.run(debug=True)
