import streamlit as st
from utils.loader import load_data, load_similarity
from utils.recommender import get_recommendations
from utils.helper import hybrid_label, get_all_genres, get_hybrid_thresholds, get_movie_poster

st.set_page_config(
    page_title="Sistem Rekomendasi Film",
    layout="centered"
)

TMDB_API_KEY = "___"

df = load_data()
cosine_sim = load_similarity()

df['title_lower'] = df['title'].str.lower()

# Hitung threshold sekali saja di luar loop
q25, q75 = get_hybrid_thresholds(df)

# =========================================
# WEB INTERFACE
# =========================================

st.title("CineMatch")

with st.form(key='search_form'):
    movie_input = st.text_input(
        "Mau nonton apa hari ini?",
        placeholder="Contoh: film action bagus, film mirip avatar, film lucu, thriller seram"
    )
    submit = st.form_submit_button("Cari Rekomendasi")

if submit:
    if movie_input.strip() == "":
        st.warning("Masukkan judul film terlebih dahulu.")
    else:
        with st.spinner("Mencari rekomendasi..."):
            results = get_recommendations(df, cosine_sim, movie_input)
            # kondisi untuk hasil tidak terdeteksi
            if isinstance(results, str) and results == "tidak_terdeteksi":
                st.warning("Input tidak terdeteksi. Coba masukkan judul, genre, atau emosi film.")
            elif results is None:
                st.error("Film tidak ditemukan.")
            else:
                for _, row in results.iterrows():
                    col1, col2 = st.columns([1, 3])

                    #  Kolom kiri — poster
                    with col1:
                        poster_url = get_movie_poster(row['id'], TMDB_API_KEY)
                        if poster_url:
                            st.image(poster_url, width=120)
                        else:
                            st.write("🎬")

                    #  Kolom kanan — info film
                    with col2:
                        st.subheader(row['title'])
                        st.write(f"Genre      : {row['genres']}")
                        st.write(f"Rating     : {row['vote_average']}")
                        st.write(f"Popularitas: {int(row['vote_count'])} suara")
                        st.write(f"Emosi Film : {row['dominant_emotion'].capitalize()}"
                                 if 'dominant_emotion' in row else "")
                        label = hybrid_label(row['hybrid_score'], q25, q75)
                        st.write(f"Rekomendasi: **{label}**")

                    st.divider()
with st.sidebar:
    st.title("Katalog Genre Film")
    st.write("Daftar seluruh genre yang tersedia:")
    sorted_genres = get_all_genres(df)
    for genre in sorted_genres:
        total_movies = len(
            df[df['genres'].str.contains(genre, case=False, na=False)]
        )
        st.write(f"• {genre} ({total_movies} film)")