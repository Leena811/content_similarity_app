from flask import Flask, render_template, request, send_file, session
import spacy
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from similarity import check_similarity  # Import similarity function

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

nlp = spacy.load("en_core_web_sm")

def highlight_entities(text):
    """Wrap named entities in span tags for HTML highlighting"""
    doc = nlp(text)
    for ent in doc.ents:
        text = text.replace(ent.text, f'<span class="highlight {ent.label_}">{ent.text}</span>')
    return text

def extract_entities(text):
    """Extract named entities as a list of tuples (entity, label)"""
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]  # ✅ Return tuples

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text1 = request.form["text1"]
        text2 = request.form["text2"]
        
        similarity_score = check_similarity(text1, text2)

        highlighted_text1 = highlight_entities(text1)
        highlighted_text2 = highlight_entities(text2)

        entities1 = extract_entities(text1)
        entities2 = extract_entities(text2)

        # 🔹 Store in session for PDF download
        session["similarity"] = similarity_score
        session["entities1"] = entities1
        session["entities2"] = entities2

        return render_template("result.html", similarity=similarity_score, 
                               text1=highlighted_text1, text2=highlighted_text2,
                               entities1=entities1, entities2=entities2)
    
    return render_template("index.html")

@app.route("/download_pdf")
def download_pdf():
    """Generate a PDF report with similarity score and named entities"""
    similarity = session.get("similarity", "N/A")
    entities1 = session.get("entities1", [])
    entities2 = session.get("entities2", [])

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 750, "Content Similarity Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 730, f"Similarity Score: {similarity}%")

    pdf.drawString(100, 700, "Named Entities in Text 1:")
    y = 680
    for entity, label in entities1:  # ✅ Fix unpacking
        pdf.drawString(120, y, f"- {entity} ({label})")
        y -= 20

    pdf.drawString(100, y - 20, "Named Entities in Text 2:")
    y -= 40
    for entity, label in entities2:  # ✅ Fix unpacking
        pdf.drawString(120, y, f"- {entity} ({label})")
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="similarity_report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
