import spacy

nlp = spacy.load("en_core_web_sm")

def highlight_entities(text):
    doc = nlp(text)
    for ent in doc.ents:
        text = text.replace(ent.text, f'<span class="highlight {ent.label_}">{ent.text}</span>')
    return text

