import os
import pickle
import gdown
import requests
import streamlit as st

# ----------------- Page Setup (must be the FIRST Streamlit call) -----------------
st.set_page_config(
    page_title="Movie Recommender | Movie Discovery Engine",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------- Styling -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0b0e14; color: #f1f5f9; }

    .spotlight-card {
        background: linear-gradient(90deg, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.6) 50%, rgba(15,23,42,0.2) 100%),
                    url('https://image.tmdb.org/t/p/original/oEIQKg1MkOSuuZ2yv1B8f2zVbO9.jpg');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .spotlight-tag {
        display: inline-block; padding: 4px 12px;
        background: rgba(229,9,20,0.2); color: #ff4d5a;
        border-radius: 999px; font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1px; text-transform: uppercase;
        border: 1px solid rgba(229,9,20,0.4); margin-bottom: 0.8rem;
    }
    .spotlight-title { font-size: 2.4rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff; }
    .spotlight-desc { color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; max-width: 650px; margin-bottom: 1rem; }

    .movie-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; overflow: hidden;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .movie-card:hover { transform: translateY(-6px); border-color: rgba(229,9,20,0.5); }
    .poster-img { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; }
    .movie-title-label {
        font-size: 0.9rem; font-weight: 700; color: #f8fafc;
        padding: 8px 10px 4px 10px; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
    }
    .card-footer {
        padding: 0 10px 10px 10px; display: flex;
        justify-content: space-between; font-size: 0.8rem; color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Load Data -----------------
# Google Drive file ID of similarity.pkl (file must be shared as "Anyone with the link")
SIMILARITY_FILE_ID = "1tntMGJgsF92viTgZ5nHzSc4-4xbBW5p_"
SIMILARITY_PATH = "similarity.pkl"


@st.cache_resource(show_spinner="Loading movie data...")
def load_data():
    movies = pickle.load(open("movies.pkl", "rb")).reset_index(drop=True)

    if not os.path.exists(SIMILARITY_PATH):
        # gdown handles Google Drive's "large file" confirmation page,
        # which plain requests.get() does not (it would save an HTML page).
        gdown.download(id=SIMILARITY_FILE_ID, output=SIMILARITY_PATH, quiet=True)

    with open(SIMILARITY_PATH, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity


try:
    movies, similarity = load_data()
except Exception as e:
    st.error(f"Could not load data files: {e}")
    st.stop()

# ----------------- TMDB API Setup -----------------
# Key is used directly as the default; a secret/env var named TMDB_API_KEY overrides it if set.
DEFAULT_TMDB_API_KEY = "ac003c422f33259f84897bb5b5343743"
try:
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", os.environ.get("TMDB_API_KEY", DEFAULT_TMDB_API_KEY))
except Exception:  # no secrets.toml present
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY", DEFAULT_TMDB_API_KEY)
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    if not TMDB_API_KEY:
        return PLACEHOLDER
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        res = requests.get(url, params={"api_key": TMDB_API_KEY, "language": "en-US"}, timeout=5)
        if res.status_code == 200:
            poster_path = res.json().get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"  # path already starts with "/"
    except Exception:
        pass
    return PLACEHOLDER


# ----------------- Recommendation Function -----------------
def recommend(movie_title):
    movie_index = movies[movies["title"] == movie_title].index[0]
    distances = similarity[movie_index]
    top = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]
    names, posters = [], []
    for idx, _ in top:
        row = movies.iloc[idx]
        names.append(row.title)
        posters.append(fetch_poster(row.movie_id))
    return names, posters


def card_html(poster, title, left, right):
    safe_title = str(title).replace('"', "&quot;")
    return (
        '<div class="movie-card">'
        f'<img class="poster-img" src="{poster}" />'
        f'<div class="movie-title-label" title="{safe_title}">{title}</div>'
        f'<div class="card-footer"><span>{left}</span><span>{right}</span></div>'
        "</div>"
    )


# ----------------- Session State -----------------
st.session_state.setdefault("show_recs", False)


def select_from_card(title):
    # Runs as a button callback, i.e. BEFORE the selectbox is re-created,
    # so it is allowed to change the selectbox's value.
    st.session_state["selected_movie"] = title
    st.session_state["show_recs"] = True


def show_recs():
    st.session_state["show_recs"] = True


# ----------------- Header & Search -----------------
st.markdown("## 🎬 Movie Recommender")

c1, c2 = st.columns([3, 1])
with c1:
    selected_movie = st.selectbox(
        "Search movie collection:",
        movies["title"].values,
        key="selected_movie",
        label_visibility="collapsed",
    )
with c2:
    st.button("✨ Recommend Similar", use_container_width=True, type="primary", on_click=show_recs)

st.write("")

# ----------------- Views -----------------
if st.session_state["show_recs"]:
    with st.spinner("Finding similar cinematic matches..."):
        names, posters = recommend(selected_movie)

    st.subheader(f"Recommendations for {selected_movie}")
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.markdown(card_html(posters[i], names[i], "Similarity Match", f"#{i + 1}"),
                        unsafe_allow_html=True)

    st.write("")
    if st.button("← Back to home"):
        st.session_state["show_recs"] = False
        st.rerun()

else:
    st.markdown("""
<div class="spotlight-card">
<span class="spotlight-tag">★ Featured Pick</span>
<div class="spotlight-title">Interstellar</div>
<div class="spotlight-desc">When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot,
Joseph Cooper, is tasked to pilot a spacecraft along with a team of researchers to find a new planet for humans.</div>
<span style="color:#facc15; font-weight:700;">★ 8.6/10</span> &nbsp;•&nbsp;
<span style="color:#94a3b8;">Sci-Fi / Adventure</span> &nbsp;•&nbsp;
<span style="color:#94a3b8;">2014</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🔥 Popular in Dataset")

    curated_titles = ["Avatar", "The Dark Knight Rises", "Inception", "The Avengers", "Interstellar"]
    curated_df = movies[movies["title"].isin(curated_titles)].head(5)

    cols = st.columns(5)
    for col, (_, row) in zip(cols, curated_df.iterrows()):
        with col:
            st.markdown(card_html(fetch_poster(row.movie_id), row.title, "Curated", "Top Pick"),
                        unsafe_allow_html=True)
            st.button("Explore", key=f"btn_curated_{row.movie_id}", use_container_width=True,
                      on_click=select_from_card, args=(row.title,))