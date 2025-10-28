import streamlit as st
import spacy
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from similarity import check_similarity  # Your existing similarity function

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Highlight entities for HTML display
def highlight_entities(text):
    doc = nlp(text)
    text_with_entities = text
    for ent in doc.ents:
        text_with_entities = text_with_entities.replace(
            ent.text, f'<span class="highlight {ent.label_}">{ent.text}</span>'
        )
    return text_with_entities

# Extract entities (tuple form)
def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]


# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="Content Similarity Checker", layout="wide")

st.title("🧠 Content Similarity Checker")
st.markdown("Compare two texts for semantic similarity and named entities.")

# Text Inputs
col1, col2 = st.columns(2)
with col1:
    text1 = st.text_area("Enter Text 1", height=200)
with col2:
    text2 = st.text_area("Enter Text 2", height=200)

if st.button("🔍 Check Similarity"):
    if text1.strip() == "" or text2.strip() == "":
        st.warning("Please enter both texts.")
    else:
        # Calculate similarity
        similarity_score = check_similarity(text1, text2)
        st.success(f"**Similarity Score:** {similarity_score}%")

        # Highlighted text
        highlighted_text1 = highlight_entities(text1)
        highlighted_text2 = highlight_entities(text2)
        entities1 = extract_entities(text1)
        entities2 = extract_entities(text2)

        st.markdown("### 📘 Highlighted Entities")
        st.markdown("""
        <style>
            .highlight { background-color: #ffff99; padding: 2px 4px; border-radius: 4px; }
            .ORG { background-color: #ffd6a5; }
            .PERSON { background-color: #b5e48c; }
            .GPE { background-color: #cdb4db; }
            .DATE { background-color: #a0c4ff; }
            .MONEY { background-color: #ffadad; }
        </style>
        """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Text 1**", unsafe_allow_html=True)
            st.markdown(highlighted_text1, unsafe_allow_html=True)
        with col4:
            st.markdown("**Text 2**", unsafe_allow_html=True)
            st.markdown(highlighted_text2, unsafe_allow_html=True)

        # Entity lists
        st.markdown("### 🏷️ Named Entities")
        col5, col6 = st.columns(2)
        with col5:
            st.write("**Entities in Text 1:**")
            for e, l in entities1:
                st.write(f"- {e} ({l})")
        with col6:
            st.write("**Entities in Text 2:**")
            for e, l in entities2:
                st.write(f"- {e} ({l})")

        # ---- Generate PDF Report ----
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, 750, "Content Similarity Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 730, f"Similarity Score: {similarity_score}%")

        pdf.drawString(100, 700, "Named Entities in Text 1:")
        y = 680
        for entity, label in entities1:
            pdf.drawString(120, y, f"- {entity} ({label})")
            y -= 20

        pdf.drawString(100, y - 20, "Named Entities in Text 2:")
        y -= 40
        for entity, label in entities2:
            pdf.drawString(120, y, f"- {entity} ({label})")
            y -= 20

        pdf.save()
        buffer.seek(0)

        st.download_button(
            label="📄 Download PDF Report",
            data=buffer,
            file_name="similarity_report.pdf",
            mime="application/pdf"
        )
