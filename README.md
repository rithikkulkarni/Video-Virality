# 🎬 YouTube Video Virality Prediction

This project aims to predict the **virality of YouTube videos** before they're posted — using only features that are known at the time of upload. These include:

- Thumbnail image features (color, contrast, embeddings)
- Thumbnail text (OCR-based)
- Video title text features (sentiment, structure, clickbait)
- Video metadata (duration, publish time, etc.)

The ultimate goal is to understand what makes content go viral and provide actionable insights for creators and marketers.

---

## 📁 Project Structure

Video-Virality/

├── scripts/ # Python scripts for data collection using YouTube API

├── notebooks/ # Notebooks for feature extraction and modeling

├── data/ # CSV files at different stages of processing

└── README.md # This file

---

## 🔍 Key Features Extracted

### 🖼️ Image-Based
- Average brightness, contrast, color values
- Deep ResNet embeddings (2048-dimensional)
- Thumbnail text (via OCR)

### 🧠 Title-Based
- Sentiment & subjectivity (TextBlob)
- Structural features (length, word count, caps, punctuation)
- Clickbait-related keywords
- Presence of numbers, power words, timed phrases

---

## 📊 Target Variable (Planned)
The final model will predict a binary or continuous measure of virality based on:
- `viewCount` or `likeCount` thresholds
- Optionally, normalized by channel size or video age

---

## 🚀 Goals
- Analyze what types of titles and thumbnails lead to virality
- Build a predictive model to estimate virality likelihood
- Offer creators insights into optimizing their content before posting

---

## 🛠️ How to Run It

1. **Collect Data**
   - Run `scripts/main.py` to pull video data via YouTube Data API v3

2. **Extract Features**
   - Run `notebooks/feature_extraction.ipynb`
   - Upload thumbnails manually or generate using video IDs

3. **Train Models**
   - Run 'notebooks/modeling.ipynb' to build and evaluate classifiers or regressors

---

## 📌 Requirements

- Python 3.8+
- `pandas`, `numpy`, `tensorflow`, `pytesseract`, `textblob`, `Pillow`, `requests`
- Google Colab (recommended for ease and GPU support)

---

## 📬 Future Plans

- Integrate additional metadata (e.g., tags, video duration)
- Normalize virality metrics by time/channel
- Build a web-based tool to test virality before publishing

---

## 📄 License
MIT License

---

## 🙌 Credits
Built by [Rithik Kulkarni](https://github.com/rithikkulkarni) as a research tool to reverse engineer how viewers evaluate videos while browsing YouTube.
