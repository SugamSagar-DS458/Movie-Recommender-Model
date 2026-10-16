# 🎬 Movie Discovery Engine & Recommender System

A content-based movie recommendation web application built with **Python**, **Scikit-learn**, and **Streamlit**. The application predicts and suggests similar movies based on metadata features such as cast, crew, genres, keywords, and plot overviews from the TMDB 5,000 Movies dataset. It also fetches and displays high-resolution posters dynamically using the **TMDB API**.

---

## 🚀 Live Demo

- **Deployed App**: [Streamlit Cloud App Link](https://movie-recommender-model-458.streamlit.app/)

---

## 📌 Features

- **Content-Based Filtering**: Suggests top 5 movies similar to your selection based on cosine similarity metrics.
- **Dynamic Poster Fetching**: Integrates with TMDB API to pull official movie poster artwork and metadata in real-time.
- **Responsive UI**: Built with Streamlit with custom CSS card styling and spotlight features.
- **Automated Model Retrieval**: Large model dependencies (`similarity.pkl`) are downloaded on-demand from cloud storage via `gdown`, avoiding GitHub file size limitations.

---

## 🛠️ How It Works

1. **Feature Extraction & Preprocessing**:
   - Extracted `genres`, `keywords`, `cast` (top 3 actors), and the `director` from TMDB credits and movie datasets.
   - Merged text attributes into an unified `tags` bag-of-words column.
   - Cleaned text via whitespace stripping and Porter Stemming (`nltk.stem.porter`).

2. **Vectorization & Similarity**:
   - Extracted features using `CountVectorizer(max_features=5000, stop_words='english')`.
   - Computed pairwise distances across movies via **Cosine Similarity**.

3. **Inference & App Flow**:
   - The user selects or searches for a title in Streamlit.
   - The app retrieves the closest vector indices from the precalculated similarity matrix.
   - TMDB API delivers high-resolution posters corresponding to each suggested movie ID.

---

## 📁 Repository Structure

```text
├── .streamlit/
│   └── secrets.toml          # Local secrets (API keys)
├── app.py                    # Streamlit web application script
├── movie_recommendation.ipynb # Data cleaning, EDA, and model pipeline notebook
├── movies.pkl                # Processed movies DataFrame
├── requirements.txt          # Python dependencies
├── .gitignore                # Excludes large files (similarity.pkl) and secrets
└── README.md                 # Project documentation
```

---

## 💻 Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<SugamSagar-DS458>/movie-recommender-system.git
cd movie-recommender-system
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure TMDB API Key
 Add your personal TMDB API key to `.streamlit/secrets.toml`:
```toml
TMDB_API_KEY = "ac003c422f33259f84897bb5b5343743"
```

### 5. Run the Streamlit application
```bash
streamlit run app.py
```

---

## 📦 Dependencies

- `streamlit`
- `pandas`
- `numpy`
- `scikit-learn`
- `requests`
- `gdown`

---

## 📜 Dataset Reference

This project utilizes the [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) from Kaggle.
