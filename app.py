# app.py

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
from io import BytesIO
from PIL import Image
import cv2
import string
from textblob import TextBlob
import textstat

from model import predict, FEATURE_ORDER

# ─── Full clickbait / power / timed word lists ─────────────────────────────────

CLICKBAIT_WORDS = {
    "amazing", "incredible", "shocking", "jaw-dropping", "mind-blowing",
    "unbelievable", "you won’t believe", "you’ll never guess", "what happens next",
    "epic", "ultimate", "must", "insane", "secret", "exposed", "revealed",
    "hack", "these reasons", "10 reasons", "this trick", "don’t miss",
    "game changer", "craziest", "revealed", "the truth about", "deal of the day"
}

POWER_WORDS = {
    "best", "top", "new", "essential", "easy", "quick", "instant", "effortless",
    "guaranteed", "proven", "genius", "exclusive", "remarkable", "powerful",
    "revolutionary", "breakthrough", "must-have", "unlock", "master", "ultimate",
    "secret", "simple", "transform", "hacks", "tips", "tricks"
}

TIMED_WORDS = {
    "now", "today", "just now", "breaking", "this morning", "this afternoon",
    "this evening", "tonight", "this week", "this weekend", "this month",
    "this season", "this year", "last minute", "last week", "2023", "2024",
    "2025", "coming soon", "newly released", "upcoming", "recent", "daily",
    "weekly", "monthly", "yearly"
}

# ─── FastAPI app setup ─────────────────────────────────────────────────━━━━━━━
app = FastAPI(
    title="YouTube Virality Predictor",
    description="Upload a thumbnail image and enter a video title to predict virality.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST","GET"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── Utility feature functions ─────────────────────────────────────────────────

def compute_clickbait_score(text: str) -> int:
    words = text.split()
    return sum(w.lower() in CLICKBAIT_WORDS for w in words)

def compute_dominant_color_hue(img: np.ndarray) -> float:
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    return float(np.argmax(hist))

def compute_title_features(title: str) -> dict:
    blob = TextBlob(title)
    words = title.split()
    punctuation = set("!?.,:;-()[]{}")
    upper_words = [w for w in words if w.isupper()]
    letters = [c for c in title if c.isalpha()]
    uppercase_letters = [c for c in letters if c.isupper()]

    return {
        "title_sentiment": blob.sentiment.polarity,
        "title_subjectivity": blob.sentiment.subjectivity,
        "num_question_marks": title.count("?"),
        "num_exclamation_marks": title.count("!"),
        "starts_with_keyword": int(words[0].lower() in {"how", "what", "why", "when", "is", "are", "does", "who"} if words else 0),
        "title_length": len(title),
        "word_count": len(words),
        "punctuation_count": sum(1 for c in title if c in punctuation),
        "uppercase_word_count": len(upper_words),
        "percent_letters_uppercase": round(len(uppercase_letters) / len(letters), 3) if letters else 0,
        "num_digits": sum(c.isdigit() for c in title),
        "clickbait_score": compute_clickbait_score(title),
        "num_power_words": sum(w.lower() in POWER_WORDS for w in words),
        "num_timed_words": sum(any(phrase in title.lower() for phrase in TIMED_WORDS) for _ in [0]),
        "clickbait_phrase_match": int(any(phrase in title.lower() for phrase in CLICKBAIT_WORDS)),
        "title_readability": textstat.flesch_reading_ease(title),
        "is_listicle": int(title.strip().lower().split()[0].isdigit()),
        "is_tutorial": int(title.lower().startswith("how to")),
        "power_word_count": sum(w.lower() in POWER_WORDS for w in words),
        "timed_word_count": sum(phrase in title.lower() for phrase in TIMED_WORDS)
    }

# ─── Main endpoint ─────────────────────────────────────────────────━━━━━━━━━

@app.post("/extract_and_predict")
async def extract_and_predict(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(...),
    thumbnail: UploadFile = File(...)
):
    # 1. Read image
    img_bytes = await thumbnail.read()
    pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
    img = np.array(pil_img)

    # 2a. Image features
    avg_red, avg_green, avg_blue = img[:,:,0].mean(), img[:,:,1].mean(), img[:,:,2].mean()
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    brightness, contrast = float(gray.mean()), float(gray.std())
    edges = cv2.Canny(gray, 100, 200)
    thumbnail_edge_density = float((edges>0).mean())
    dominant_color_hue = compute_dominant_color_hue(img)

    # 2b. Title features
    title_feats = compute_title_features(title)

    # 3. Description features
    desc_blob = TextBlob(description or "")
    description_length = len(description)
    description_sentiment = desc_blob.sentiment.polarity
    description_has_keywords = int(any(k in description.lower() for k in {"subscribe","giveaway","limited time","offer","new video"}))

    # 4. Tag features
    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    tag_count = len(tags_list)
    tag_sentiment = float(np.mean([TextBlob(t).sentiment.polarity for t in tags_list])) if tags_list else 0.0
    num_unique_tags = len(set(t.lower() for t in tags_list))
    avg_tag_length = float(np.mean([len(t) for t in tags_list])) if tags_list else 0.0

    # 5. Assemble all features
    feature_values = {
        'avg_red': float(avg_red),
        'avg_green': float(avg_green),
        'avg_blue': float(avg_blue),
        'brightness': brightness,
        'contrast': contrast,
        **title_feats,
        'description_length': description_length,
        'description_sentiment': description_sentiment,
        'description_has_keywords': description_has_keywords,
        'tag_count': tag_count,
        'tag_sentiment': tag_sentiment,
        'num_unique_tags': num_unique_tags,
        'avg_tag_length': avg_tag_length,
        'thumbnail_edge_density': thumbnail_edge_density,
        'dominant_color_hue': dominant_color_hue
    }

    # 6. Predict
    result = predict(feature_values, threshold=0.3)
    return result
