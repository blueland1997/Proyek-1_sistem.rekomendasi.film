import streamlit as st
from utils.loader import load_data, load_similarity
from utils.recommender import get_recommendations
from utils.helper import hybrid_label, get_all_genres


st.set_page_config(
    page_title="Sistem Rekomendasi Film",
    layout="centered"
)


df = load_data()
cosine_sim = load_similarity()

df['title_lower'] = df['title'].str.lower()

# =========================================
# WEB INTERFACE
# =========================================

st.title("Sistem Rekomendasi Film")

movie_input = st.text_input(
    "Mau nonton apa hari ini?",
    placeholder="Contoh: film action bagus, film mirip avatar, film lucu, thriller seram"
)

if st.button("Cari Rekomendasi"):

    if movie_input.strip() == "":
        st.warning("Masukkan judul film terlebih dahulu.")

    else:
        with st.spinner("Mencari rekomendasi..."):

            results = get_recommendations(df, cosine_sim, movie_input)

            if results is None:
                st.error("Film tidak ditemukan.")

            else:
                st.success("Berikut rekomendasi film untuk Anda:")

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

with st.sidebar:

    st.title("Katalog Genre Film")
    st.write("Daftar seluruh genre yang tersedia:")

    sorted_genres = get_all_genres(df)

    for genre in sorted_genres:
        total_movies = len(
            df[df['genres'].str.contains(genre, case=False, na=False)]
        )
        st.write(f"• {genre} ({total_movies} film)")