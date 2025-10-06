import nltk
from nltk.tokenize import sent_tokenize, PunktSentenceTokenizer
import re


nltk.download("punkt")

punkt_tokenizer = PunktSentenceTokenizer()  # standard tokenizer


def clean_sentences(sentences):
    filtered = []
    for s in sentences:
        s = s.strip()
        # Skip very short sentences
        if len(s.split()) < 5:
            continue
        # Skip common header/footer keywords
        if any(word.lower() in s.lower() for word in ["institute", "marks", "slide", "©", "page"]):
            continue
        # Skip sentences that are mostly numbers or special chars
        if re.match(r'^[\d\W]+$', s):
            continue
        filtered.append(s)
    return filtered

def generate_questions(text, limit=5):
    # Remove slide numbers, copyright, and common boilerplate
    text = re.sub(r"Page \d+|Slide \d+/\d+|©.*", "", text)
    
    sentences = punkt_tokenizer.tokenize(text)
    sentences = clean_sentences(sentences)

    questions = []
    for i, sent in enumerate(sentences[:limit]):  # limit number of questions
        q = f"Q{i+1}: {sent.replace('.', '?')}"
        questions.append(q)
    return questions
