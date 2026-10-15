import streamlit as st
import pickle
import requests

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_resource
def load_and_compute():
    movies = pickle.load(open('movies.pkl', 'rb'))
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies['tags']).toarray()
    similarity = cosine_similarity(vectors)
    return movies, similarity

movies, similarity = load_and_compute()

# ----------------- Page Setup -----------------
st.set_page_config(
    page_title="Movie Recommender | Movie Discovery Engine",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- Modern Cinematic Styling -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #0b0e14;
        color: #f1f5f9;
    }

    /* Hero Spotlight Banner */
    .spotlight-card {
        background: linear-gradient(90deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.6) 50%, rgba(15, 23, 42, 0.2) 100%),
                    url('https://image.tmdb.org/t/p/original/oEIQKg1MkOSuuZ2yv1B8f2zVbO9.jpg');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .spotlight-tag {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(229, 9, 20, 0.2);
        color: #ff4d5a;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid rgba(229, 9, 20, 0.4);
        margin-bottom: 0.8rem;
    }
    .spotlight-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .spotlight-desc {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.5;
        max-width: 650px;
        margin-bottom: 1rem;
    }

    /* Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .movie-card:hover {
        transform: translateY(-6px);
        border-color: rgba(229, 9, 20, 0.5);
    }
    .poster-img {
        width: 100%;
        aspect-ratio: 2/3;
        object-fit: cover;
        display: block;
    }
    .movie-title-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #f8fafc;
        padding: 8px 10px 4px 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-footer {
        padding: 0 10px 10px 10px;
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Load Data -----------------
@st.cache_resource
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()

# ----------------- TMDB API Setup -----------------
TMDB_API_KEY = "ac003c422f33259f84897bb5b5343743"  # Add your TMDB Key here

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            poster_path = res.json().get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"

# ----------------- Recommendation Function -----------------
def recommend(movie_title):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    names, posters = [], []
    for item in movies_list:
        row = movies.iloc[item[0]]
        names.append(row.title)
        posters.append(fetch_poster(row.movie_id))
    return names, posters

# ----------------- App Header & Search -----------------
st.markdown("## 🎬 Movie Recommender")

c1, c2 = st.columns([3, 1])
with c1:
    selected_movie = st.selectbox(
        "Search movie collection:",
        movies['title'].values,
        index=0,
        label_visibility="collapsed"
    )
with c2:
    search_clicked = st.button("✨ Recommend Similar", use_container_width=True, type="primary")

st.write("")

# ----------------- Conditional Views -----------------
if search_clicked:
    # --- RECOMMENDATION VIEW ---
    with st.spinner("Finding similar cinematic matches..."):
        names, posters = recommend(selected_movie)

    st.subheader(f"Recommendations for {selected_movie}")
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.markdown(f"""
            <div class="movie-card">
                <img class="poster-img" src="{posters[i]}" />
                <div class="movie-title-label" title="{names[i]}">{names[i]}</div>
                <div class="card-footer">
                    <span>Similarity Match</span>
                    <span>#{i+1}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    # --- DEFAULT INITIAL VIEW ---
    
    # 1. Spotlight Feature Banner
    st.markdown("""
    <div class="spotlight-card">
        <span class="spotlight-tag">★ Featured Pick</span>
        <div class="spotlight-title">Interstellar</div>
        <div class="spotlight-desc">
            When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, 
            is tasked to pilot a spacecraft along with a team of researchers to find a new planet for humans.
        </div>
        <span style="color:#facc15; font-weight:700;">★ 8.6/10</span> &nbsp;•&nbsp; 
        <span style="color:#94a3b8;">Sci-Fi / Adventure</span> &nbsp;•&nbsp; 
        <span style="color:#94a3b8;">2014</span>
    </div>
    """, unsafe_allow_html=True)

    # 2. Curated Trending Section on Startup
    st.markdown("### 🔥 Popular in Dataset")
    
    # Pre-selected known titles from the TMDB 5000 dataset
    curated_titles = ["Avatar", "The Dark Knight Rises", "Inception", "The Avengers", "Interstellar"]
    curated_df = movies[movies['title'].isin(curated_titles)].head(5)

    cols = st.columns(5)
    for idx, (_, row) in enumerate(curated_df.iterrows()):
        poster_url = fetch_poster(row.movie_id)
        with cols[idx]:
            st.markdown(f"""
            <div class="movie-card">
                <img class="poster-img" src="{poster_url}" />
                <div class="movie-title-label" title="{row.title}">{row.title}</div>
                <div class="card-footer">
                    <span>Curated</span>
                    <span>Top Pick</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick-select button that populates recommendations directly
            if st.button("Explore", key=f"btn_curated_{row.movie_id}", use_container_width=True):
                st.session_state["selected_from_card"] = row.title
                st.rerun()