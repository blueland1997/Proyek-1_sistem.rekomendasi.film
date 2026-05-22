import streamlit as st
import pandas as pd
import pickle

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Sistem Rekomendasi Film",
    layout="centered"
)

# =========================================
# LOAD DATA
# =========================================

@st.cache_data
def load_data():
    return pd.read_csv("cleaned_data.csv")

@st.cache_resource
def load_similarity():
    with open("cosine_similarity.pkl", "rb") as f:
        return pickle.load(f)

df = load_data()
cosine_sim = load_similarity()

# =========================================
# FALLBACK HYBRID SCORE
# =========================================

if 'hybrid_score' not in df.columns:

    df['hybrid_score'] = (
        df['vote_average'] / 10
    )

if 'bayesian_score' not in df.columns:

    df['bayesian_score'] = (
        df['vote_average']
    )
# =========================================
# PREPROCESSING
# =========================================

df['title_lower'] = df['title'].str.lower()

# =========================================
# SMART RECOMMENDATION FUNCTION
# =========================================

def get_recommendations(user_input, top_n=5):

    cleaned_input = user_input.lower().strip()

    # =====================================
    # NORMALISASI INPUT USER
    # =====================================

    remove_words = [
        "film", "rekomendasi", "recommend",
        "tolong", "dong", "yang", "tentang",
        "aku", "saya", "mau", "ingin",
        "carikan", "kasih", "berikan",
        "buat", "ada", "mirip"
    ]

    for word in remove_words:
        cleaned_input = cleaned_input.replace(word, "")

    cleaned_input = cleaned_input.strip()

    # =====================================
    # DETEKSI GENRE DARI INPUT USER
    # =====================================

    genre_keywords = {
        "action": "Action", "aksi": "Action",
        "fight": "Action", "battle": "Action",
        "adventure": "Adventure", "petualangan": "Adventure",
        "animation": "Animation", "anime": "Animation", "kartun": "Animation",
        "comedy": "Comedy", "komedi": "Comedy",
        "lucu": "Comedy", "funny": "Comedy",
        "crime": "Crime", "kriminal": "Crime",
        "documentary": "Documentary", "dokumenter": "Documentary",
        "drama": "Drama", "sedih": "Drama",
        "family": "Family", "keluarga": "Family",
        "fantasy": "Fantasy", "magic": "Fantasy",
        "history": "History", "sejarah": "History",
        "horror": "Horror", "horor": "Horror",
        "seram": "Horror", "hantu": "Horror",
        "music": "Music", "musik": "Music",
        "mystery": "Mystery", "misteri": "Mystery",
        "romance": "Romance", "romantis": "Romance", "cinta": "Romance",
        "science fiction": "Science Fiction",
        "sci fi": "Science Fiction", "robot": "Science Fiction",
        "thriller": "Thriller", "menegangkan": "Thriller", "tegang": "Thriller",
        "war": "War", "militer": "War",
        "western": "Western", "koboi": "Western"
    }

    # =====================================
    # DETEKSI EMOSI DARI INPUT USER
    # =====================================

    emotion_keywords = {
        "senang": "joy", "bahagia": "joy", "seru": "joy", "happy": "joy",
        "sedih": "sadness", "menangis": "sadness", "haru": "sadness",
        "takut": "fear", "seram": "fear", "horor": "fear", "ngeri": "fear",
        "marah": "anger", "dendam": "anger", "perang": "anger",
        "kejutan": "surprise", "misteri": "surprise", "mengejutkan": "surprise"
    }

    detected_genre = None
    for keyword, genre in genre_keywords.items():
        if keyword in cleaned_input:
            detected_genre = genre
            break

    detected_emotion = None
    for keyword, emotion in emotion_keywords.items():
        if keyword in cleaned_input:
            detected_emotion = emotion
            break

    # =====================================
    # REKOMENDASI BERBASIS EMOSI
    # =====================================

    if detected_emotion is not None and 'dominant_emotion' in df.columns:
        emotion_result = df[
            df['dominant_emotion'] == detected_emotion
        ]
        if not emotion_result.empty:
            return emotion_result.sort_values(
                by='hybrid_score',
                ascending=False
            ).head(top_n)

    # =====================================
    # REKOMENDASI BERBASIS GENRE
    # =====================================

    if detected_genre is not None:
        genre_result = df[
            df['genres'].str.contains(
                detected_genre,
                case=False,
                na=False
            )
        ]
        if not genre_result.empty:
            return genre_result.sort_values(
                by='hybrid_score',
                ascending=False
            ).head(top_n)

    # =====================================
    # REKOMENDASI BERBASIS JUDUL FILM
    # =====================================

    for title in df['title_lower']:
        if cleaned_input in title:
            idx = df[df['title_lower'] == title].index[0]

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:top_n + 1]

            movie_indices = [i[0] for i in sim_scores]
            recommendations = df.iloc[movie_indices]

            return recommendations.sort_values(
                by='hybrid_score',
                ascending=False
            )

    # =====================================
    # JIKA TIDAK DITEMUKAN
    # =====================================

    return None

# =========================================
# LABEL REKOMENDASI
# =========================================

def hybrid_label(score):

    if score >= 0.75:
        return "Sangat Direkomendasikan"

    elif score >= 0.5:
        return "Direkomendasikan"

    else:
        return "Cukup Direkomendasikan"
# =========================================
# HEADER
# =========================================

st.title("Sistem Rekomendasi Film")

# =========================================
# INPUT
# =========================================

movie_input = st.text_input(
    "Mau nonton apa hari ini?",
    placeholder="Contoh: film action bagus, film mirip avatar, film lucu, thriller seram"
)

# =========================================
# BUTTON
# =========================================

if st.button("Cari Rekomendasi"):

    if movie_input.strip() == "":

        st.warning(
            "Masukkan judul film terlebih dahulu."
        )

    else:

        with st.spinner("Mencari rekomendasi..."):

            results = get_recommendations(movie_input)

            # =====================================
            # JIKA FILM TIDAK DITEMUKAN
            # =====================================

            if results is None:

                st.error(
                    "Film tidak ditemukan."
                )

            # =====================================
            # TAMPILKAN HASIL
            # =====================================

            else:

                st.success(
                    "Berikut rekomendasi film untuk Anda:"
                )

                for _, row in results.iterrows():

                    st.subheader(row['title'])

                    st.write(f"Genre      : {row['genres']}")
                    st.write(f"Rating     : {row['vote_average']}")
                    st.write(f"Popularitas: {int(row['vote_count'])} suara")
                    st.write(f"Emosi Film : {row['dominant_emotion'].capitalize()}" 
                            if 'dominant_emotion' in row else "")

                    label = hybrid_label(row['hybrid_score'])

                    st.write(f"Rekomendasi: **{label}**")

                    st.divider()

# =========================================
# SIDEBAR GENRE CATALOG
# =========================================

with st.sidebar:

    st.title("Katalog Genre Film")

    st.write(
        "Daftar seluruh genre yang tersedia:"
    )

    # Ambil genre unik
    all_genres = set()

    for genres in df['genres'].dropna():

        genre_list = [
            g.strip()
            for g in genres.split(',')
        ]

        all_genres.update(genre_list)

    # Urutkan genre
    sorted_genres = sorted(all_genres)

    # Tampilkan genre
    for genre in sorted_genres:

        # Hitung jumlah film per genre
        total_movies = len(
            df[
                df['genres']
                .str.contains(
                    genre,
                    case=False,
                    na=False
                )
            ]
        )

        st.write(
            f"• {genre} ({total_movies} film)"
        )