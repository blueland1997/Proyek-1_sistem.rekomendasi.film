import streamlit as st
import pandas as pd
import pickle
import os

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Chatbot Blueland",
    page_icon="",
    layout="centered"
)

# ==================================================
# LOAD DATA & MODEL
# ==================================================
DATA_PATH = "cleaned_data.csv"
MODEL_PATH = "cosine_similarity.pkl"

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

@st.cache_resource
def load_similarity():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

df = load_data()
cosine_sim = load_similarity()

if df is None or cosine_sim is None:
    st.error("File dataset atau model tidak ditemukan.")
    st.stop()

# Ambil daftar genre unik untuk ditampilkan di sidebar
if df is not None:
    # Mengambil semua genre, membersihkan spasi, dan mencari nilai unik
    all_genres = set()
    for g_str in df['genres'].dropna():
        genres_list = [g.strip() for g in g_str.split(',')]
        all_genres.update(genres_list)
    # Urutkan secara abjad dan hilangkan 'Tidak ada' jika ada
    list_genre_display = sorted([g for g in all_genres if g != 'Tidak ada'])
else:
    list_genre_display = []

# ==================================================
# LOGIC: SEARCH BY GENRE 
# ==================================================
def get_recommendations(user_input, top_n=5):
    user_input = user_input.strip().lower()
    
    # 1. CEK APAKAH INPUT ADALAH PERMINTAAN GENRE (Contoh: "film komedi")
    # Kita ambil kata kuncinya saja (misal user ketik "film action" -> kita ambil "action")
    keywords = user_input.replace("film", "").replace("cari", "").replace("berikan", "").replace("saya", "").strip()
    
    # Cek apakah keyword ada di dalam kolom genres
    # Kami menggunakan str.contains untuk mencari kecocokan kata
    genre_match = df[df['genres'].str.lower().str.contains(keywords, na=False)]
    
    if not genre_match.empty and len(keywords) > 2:
        # Jika ketemu sebagai genre, urutkan berdasarkan rating tertinggi (Bayesian/Vote Average)
        return genre_match.sort_values(by='vote_average', ascending=False).head(top_n)

    # 2. JIKA BUKAN GENRE, CARI BERDASARKAN JUDUL (Similarity)
    temp_df = df.copy()
    temp_df['title_lower'] = temp_df['title'].str.lower()

    if user_input in temp_df['title_lower'].values:
        idx = temp_df[temp_df['title_lower'] == user_input].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]
        movie_indices = [i[0] for i in sim_scores]
        return df.iloc[movie_indices]
    
    return None

# ==================================================
# USER INTERFACE
# ==================================================
st.title("Test Chatbot")
st.write("Uji Coba Chatbot tahap 1")

movie_input = st.text_input(
    "Apa yang ingin Anda tonton?",
    placeholder="Ketik genre film (misal: 'film action')"
)

if st.button("Tanya Chatbot"):
    if not movie_input.strip():
        st.warning("Masukkan genre yang tersedia")
    else:
        with st.spinner('Mencari film terbaik untuk Anda...'):
            results = get_recommendations(movie_input)
            
            if results is None or results.empty:
                st.error(f"Maaf, sistem tidak menemukan hasil untuk '{movie_input}'.")
            else:
                st.success(f"Berikut rekomendasi untuk Anda:")
                for _, row in results.iterrows():
                    with st.container():
                        st.markdown(f" {row['title']}")
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write(f" **Rating:** {row['vote_average']}")
                        with col2:
                            st.write(f" **Genre:** {row['genres']}")
                        st.divider()

# ==================================================
# SIDEBAR (UPDATE LIST GENRE OTOMATIS)
# ==================================================
with st.sidebar:
    st.title("Informasi Pencarian")
    st.markdown("Daftar Genre Tersedia:")
    
    # Menampilkan daftar genre dalam bentuk list bullet
    genre_text = ""
    for g in list_genre_display:
        genre_text += f"- {g}\n"
    
    st.markdown(genre_text)