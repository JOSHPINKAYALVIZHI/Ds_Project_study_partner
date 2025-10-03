import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt", quiet=True)

def generate_flashcards(text, num_flashcards=5):
    sentences = sent_tokenize(text)
    flashcards = []
    for sent in sentences[:num_flashcards]:
        flashcards.append({
            "front": sent,
            "back": "Answer"  
        })
    return flashcards
