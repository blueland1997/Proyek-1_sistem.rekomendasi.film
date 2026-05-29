import re


def get_recommendations(df, cosine_sim, user_input, top_n=5):

    # Preprocessing input pengguna
    cleaned_input = user_input.lower().strip()
    
    # Hapus tanda baca
    remove_words = [
        "film", "rekomendasi", "recommend",
        "tolong", "dong", "yang", "tentang",
        "aku", "saya", "mau", "ingin",
        "carikan", "kasih", "berikan",
        "buat", "ada", "mirip"
    ]
    
    # Hapus kata-kata umum yang tidak menambah konteks
    for word in remove_words:
        cleaned_input = re.sub(rf'\b{word}\b', '', cleaned_input)
    # Hapus spasi ekstra yang mungkin muncul setelah penghapusan kata
    cleaned_input = ' '.join(cleaned_input.split())

    # Pemetaan keyword ke genre dan emosi
    genre_keywords = {
        "action"          : "Action",
        "aksi"            : "Action",
        "fight"           : "Action",
        "battle"          : "Action",
        "adventure"       : "Adventure",
        "petualangan"     : "Adventure",
        "animation"       : "Animation",
        "anime"           : "Animation",
        "kartun"          : "Animation",
        "comedy"          : "Comedy",
        "komedi"          : "Comedy",
        "lucu"            : "Comedy",
        "funny"           : "Comedy",
        "crime"           : "Crime",
        "kriminal"        : "Crime",
        "documentary"     : "Documentary",
        "dokumenter"      : "Documentary",
        "drama"           : "Drama",
        "sedih"           : "Drama",
        "family"          : "Family",
        "keluarga"        : "Family",
        "fantasy"         : "Fantasy",
        "magic"           : "Fantasy",
        "history"         : "History",
        "sejarah"         : "History",
        "horror"          : "Horror",
        "horor"           : "Horror",
        "seram"           : "Horror",
        "hantu"           : "Horror",
        "music"           : "Music",
        "musik"           : "Music",
        "mystery"         : "Mystery",
        "misteri"         : "Mystery",
        "romance"         : "Romance",
        "romantis"        : "Romance",
        "cinta"           : "Romance",
        "science fiction" : "Science Fiction",
        "sci fi"          : "Science Fiction",
        "robot"           : "Science Fiction",
        "thriller"        : "Thriller",
        "menegangkan"     : "Thriller",
        "tegang"          : "Thriller",
        "war"             : "War",
        "militer"         : "War",
        "western"         : "Western",
        "koboi"           : "Western",
    }

    # Pemetaan keyword emosi
    emotion_keywords = {
        "senang"       : "joy",
        "bahagia"      : "joy",
        "seru"         : "joy",
        "happy"        : "joy",
        "sedih"        : "sadness",
        "menangis"     : "sadness",
        "haru"         : "sadness",
        "takut"        : "fear",
        "ngeri"        : "fear",
        "marah"        : "anger",
        "dendam"       : "anger",
        "perang"       : "anger",
        "kejutan"      : "surprise",
        "mengejutkan"  : "surprise",
    }

    # Deteksi genre dan emosi dari input pengguna 
    detected_genre = None
    for keyword, genre in genre_keywords.items():
        if keyword in cleaned_input:
            detected_genre = genre
            break
    
    # Deteksi emosi
    detected_emotion = None
    for keyword, emotion in emotion_keywords.items():
        if keyword in cleaned_input:
            detected_emotion = emotion
            break

    # Filter kombinasi genre + emosi (jika keduanya terdeteksi)
    if detected_genre and detected_emotion and 'dominant_emotion' in df.columns:
        combined_result = df[
            df['genres'].str.contains(detected_genre, case=False, na=False) &
            (df['dominant_emotion'] == detected_emotion)
        ]
        if not combined_result.empty:
            return combined_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # Filter emosi saja
    if detected_emotion is not None and 'dominant_emotion' in df.columns:
        emotion_result = df[df['dominant_emotion'] == detected_emotion]
        if not emotion_result.empty:
            return emotion_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # Filter genre saja
    if detected_genre is not None:
        genre_result = df[
            df['genres'].str.contains(detected_genre, case=False, na=False)
        ]
        if not genre_result.empty:
            return genre_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # Cari berdasarkan judul
    if 'title_lower' in df.columns:
        for title in df['title_lower']:
            if cleaned_input in title:
                idx = df[df['title_lower'] == title].index[0]

                # Dapatkan skor similarity untuk semua film dibandingkan dengan film input
                sim_scores = list(enumerate(cosine_sim[idx]))
                # Urutkan berdasarkan skor similarity tertinggi
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                # Skip film input itu sendiri berdasarkan index, bukan posisi
                sim_scores = [s for s in sim_scores if s[0] != idx]

                # Filter similarity terlalu rendah
                sim_scores = [s for s in sim_scores if s[1] > 0.1]
                sim_scores = sim_scores[:top_n]

                if sim_scores:
                    movie_indices = [i[0] for i in sim_scores]
                    recommendations = df.iloc[movie_indices].copy()
                    
                    # Gabungkan cosine similarity + hybrid_score
                    # agar hasil relevan secara konten DAN kualitas
                    recommendations['cosine_score'] = [s[1] for s in sim_scores]
                    recommendations['final_score'] = (
                        0.6 * recommendations['cosine_score'] +
                        0.4 * recommendations['hybrid_score']
                    )

                    return recommendations.sort_values(
                        by='final_score', ascending=False
                    ).drop(columns=['cosine_score', 'final_score'])

    # Top hybrid_score 
    return df.sort_values(by='hybrid_score', ascending=False).head(top_n)