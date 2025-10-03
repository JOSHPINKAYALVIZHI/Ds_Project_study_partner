import random
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
nltk.download("punkt")
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

def generate_mcqs(text, limit=10):
    mcqs = []
    sentences = sent_tokenize(text)

    for sentence in sentences:
        words = [w for w in word_tokenize(sentence) if w.isalpha() and w.lower() not in stop_words]
        if len(words) < 4:
            continue  # skip very short sentences

        answer = random.choice(words)
        question = sentence.replace(answer, "_____")

        wrong_options = random.sample([w for w in words if w != answer], min(3, len(words)-1))
        options = wrong_options + [answer]
        random.shuffle(options)

        mcqs.append({
            "question": question,
            "options": options,
            "answer": answer
        })

        if len(mcqs) >= limit:  # stop after limit
            break

    return mcqs
