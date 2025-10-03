from nltk.tokenize import sent_tokenize
import random

def generate_summary(text, max_sentences=5):
    text = text.strip()
    if not text:
        return " No valid content to summarize."
    
    sentences = sent_tokenize(text)
    sentences = [s for s in sentences if s.strip()]
    
    if not sentences:
        return " No valid sentences to summarize."
    
    # Take first few sentences or random sample
    summary_sentences = sentences[:max_sentences]
    return " ".join(summary_sentences)
