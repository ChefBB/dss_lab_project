"""
Creates categories based off of lyrics.
"""

import json
import os
import spacy
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF


my_stopwords = [
    'ah', 'uh', 'yeah', 'ehi', 'eh', 'seh', 'pe',
    'uoh', 'no', 'yah', 'mhm', 'oh', 'ca', 'nu',
    'int', 'you', 'the', 'to', 'it', 'and', 'my',
    'we', 'on', 'your', 'that', 'na', 'ra', 'ta',
    'lyrics', 'contributorsintro', 'contributorsil',
    'interludio', 'song', 'pt', 'pubblicata', 'that',
    'tha', 'contributoril', 'skrrt', 'nn', 'ohm',
    'lario', 'badabum', 'mcf', 'contributorsbloody',
    'aahhhh', 'pes', 'busdeez', 'lewa', 'amemì', 'llámame',
    'pih', 'baing', 'grah', 'ciny', 'lyricscoming',
    'lyricsthis', 'instrumental', 'contributorsinterlude',
    'eooh', 'phi', 'att', 'ce', 'cu', 'mo', 'bu',
    'contributorsoutro', 'contributorspaghetti', 'contributoryour',
    'nanananana', 'lyric', 'strumentale', 'vinyl', 'strumentale',
    'mix'
]



parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
dataset_dir = f'{parent_dir}/dataset'

with open(f'{dataset_dir}/correct_ids/tracks.json') as f:
    tracks = json.load(f)
    

texts = list()

for track in tracks:
    texts.append(track['lyrics'])
    


# spacy.cli.download("it_core_news_sm")
# spacy.cli.download("en_core_web_sm")

nlp_it = spacy.load("it_core_news_sm", disable=["ner", "parser"])
nlp_en = spacy.load("en_core_web_sm", disable=["ner", "parser"])


# detect language
def lemmatize_lyrics(text):
    """
    Lemmatize song lyrics using automatic language detection (English / Italian).

    Parameters
    ----------
    text : str
        Raw lyrics text to be lemmatized.

    Returns
    -------
    str
        A space-separated string of lemmatized tokens.
    """
    english_chars = sum(c.isascii() for c in text) / max(len(text), 1)

    if english_chars > 0.85:
        doc = nlp_en(text)
    else:
        doc = nlp_it(text)

    return " ".join(
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and len(token) > 2
    )


texts = [lemmatize_lyrics(text) for text in texts]


nltk.download('stopwords')
ita_stopwords = stopwords.words('italian')

# extend stopwords with dataset-specific stopwords
ita_stopwords.extend(my_stopwords)


# nltk.download('stopwords')

# Build TF-IDF document-term matrix from lyrics
vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words=ita_stopwords)
dtm = vectorizer.fit_transform(texts)

# Train NMF topic model
num_topics = 8
nmf_model = NMF(n_components=num_topics, random_state=42)
nmf_model.fit(dtm)

# Extract topic-word matrix
H = nmf_model.components_

# Compute document-topic matrix
W = nmf_model.transform(dtm)

# Print top words for each topic
n_top_words = 20
feature_names = vectorizer.get_feature_names_out()

for topic_idx, topic in enumerate(H):
    top_terms = [feature_names[i] for i in topic.argsort()[-n_top_words:][::-1]]
    print(f"Topic {topic_idx}: {', '.join(top_terms)}")

# Assign each song to its dominant topic
topic_assignment = W.argmax(axis=1)

# Count number of songs per topic
topic_counts = np.zeros(num_topics, dtype=int)
for t in range(num_topics):
    topic_counts[t] = np.sum(topic_assignment == t)

for t, count in enumerate(topic_counts):
    print(f"Topic {t}: {count} songs")

# Human-readable topic labels
topic_names = {
    0: 'italian_pop',
    1: 'neapolitan',
    2: 'rap_street',
    3: 'italian_love',
    4: 'english_pop',
    5: 'trap_gang',
    6: 'storytelling',
    7: 'dark_poetic'
}

# Assign topic category to each track (if lyrics are available)
for i in range(len(topic_assignment)):
    if tracks[i].get('lyrics') != '':
        tracks[i]['category'] = topic_names[topic_assignment[i]]
    else:
        tracks[i]['category'] = None

# Save updated tracks with assigned categories
with open(f'{dataset_dir}/correct_ids/tracks.json', 'w') as f:
    json.dump(tracks, f)