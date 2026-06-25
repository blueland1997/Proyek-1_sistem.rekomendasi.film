import re


def get_recommendations(df, cosine_sim, user_input, top_n=5):

    # Preprocessing input pengguna
    cleaned_input = user_input.lower().strip()

    # Hapus kata-kata umum yang tidak menambah konteks
    remove_words = [
        # umum
        "film", "movie", "movies", "rekomendasi", "recommend", "recommendation",
        "tolong", "dong", "yang", "tentang", "mengenai", "bertema",
        "aku", "saya", "gua", "gue", "gw", "lu", "kamu",
        "mau", "ingin", "pengen", "lagi", "sedang",
        "carikan", "kasih", "berikan", "buat", "ada", "cari",

        # konteks nonton
        "nonton", "tonton", "ditonton", "watch", "watching",
        "lihat", "menonton",

        # kata penghubung
        "dan", "atau", "dengan", "sama", "untuk", "ke", "di",
        "dari", "buat", "kaya", "kayak", "seperti",

        # mirip
        "mirip", "similar", "sejenis", "kayak", "seperti"
    ]

    for word in remove_words:
        cleaned_input = re.sub(rf'\b{re.escape(word)}\b', '', cleaned_input)

    # Hapus spasi berlebih
    cleaned_input = ' '.join(cleaned_input.split())

    # Cek input kosong setelah cleaning
    if not cleaned_input:
        return "tidak_terdeteksi"

    # ── Quality keywords → return top hybrid_score ──────────────────────────
    quality_keywords = [
        # Indonesia
        "bagus", "baik", "terbaik", "top", "populer",
        "terkenal", "hits", "keren", "mantap", "berkualitas",
        "bagusan", "seru-seru", "favorit", "favoritku",
        # Inggris
        "good", "best", "great", "popular", "recommended",
        "awesome", "excellent", "quality", "must watch",
        "must see", "worth watching"
    ]

    if any(word in cleaned_input for word in quality_keywords):
        return df.sort_values(by='hybrid_score', ascending=False).head(top_n)

    # ── Bad keywords → return film dengan hybrid_score terendah ─────────────
    bad_keywords = [
        # Indonesia
        "jelek", "buruk", "terburuk", "murahan",
        "sampah", "gak bagus", "tidak bagus",
        # Inggris
        "bad", "worst", "terrible", "awful",
        "boring", "trash", "poor"
    ]

    if any(word in cleaned_input for word in bad_keywords):
        return df.sort_values(by='hybrid_score', ascending=False).tail(top_n)

    # ── Pemetaan keyword ke genre ────────────────────────────────────────────
    genre_keywords = {
        # Action
        "action"          : "Action",
        "aksi"            : "Action",
        "fight"           : "Action",
        "fighting"        : "Action",
        "battle"          : "Action",
        "bertarung"       : "Action",
        "pertarungan"     : "Action",
        "berantem"        : "Action",
        "tembak-tembakan" : "Action",
        "tembakan"        : "Action",
        "kejar-kejaran"   : "Action",
        "ledakan"         : "Action",
        "explosion"       : "Action",
        "superhero"       : "Action",
        "pahlawan"        : "Action",

        # Adventure
        "adventure"       : "Adventure",
        "petualangan"     : "Adventure",
        "jelajah"         : "Adventure",
        "menjelajah"      : "Adventure",
        "perjalanan"      : "Adventure",
        "journey"         : "Adventure",
        "explore"         : "Adventure",
        "survival"        : "Adventure",
        "bertahan hidup"  : "Adventure",

        # Animation
        "animation"       : "Animation",
        "animasi"         : "Animation",
        "anime"           : "Animation",
        "kartun"          : "Animation",
        "cartoon"         : "Animation",
        "cgi"             : "Animation",
        "pixar"           : "Animation",
        "disney"          : "Animation",

        # Comedy
        "comedy"          : "Comedy",
        "komedi"          : "Comedy",
        "lucu"            : "Comedy",
        "funny"           : "Comedy",
        "kocak"           : "Comedy",
        "ngakak"          : "Comedy",
        "humor"           : "Comedy",
        "lawak"           : "Comedy",
        "ringan"          : "Comedy",
        "menghibur"       : "Comedy",
        "sitcom"          : "Comedy",

        # Crime
        "crime"           : "Crime",
        "kriminal"        : "Crime",
        "kejahatan"       : "Crime",
        "pencurian"       : "Crime",
        "perampokan"      : "Crime",
        "mafia"           : "Crime",
        "gangster"        : "Crime",
        "detective"       : "Crime",
        "detektif"        : "Crime",
        "polisi"          : "Crime",
        "investigasi"     : "Crime",
        "murder"          : "Crime",
        "pembunuhan"      : "Crime",

        # Documentary
        "documentary"     : "Documentary",
        "dokumenter"      : "Documentary",
        "nyata"           : "Documentary",
        "kisah nyata"     : "Documentary",
        "real story"      : "Documentary",
        "based on true story": "Documentary",
        "biografi"        : "Documentary",
        "sejarah nyata"   : "Documentary",

        # Drama
        "drama"           : "Drama",
        "kehidupan"       : "Drama",
        "konflik keluarga": "Drama",
        "perjuangan"      : "Drama",
        "inspiratif"      : "Drama",
        "emosional"       : "Drama",
        "menyentuh"       : "Drama",

        # Family
        "family"          : "Family",
        "keluarga"        : "Family",
        "anak"            : "Family",
        "anak-anak"       : "Family",
        "kids"            : "Family",
        "orang tua"       : "Family",

        # Fantasy
        "fantasy"         : "Fantasy",
        "fantasi"         : "Fantasy",
        "magic"           : "Fantasy",
        "sihir"           : "Fantasy",
        "penyihir"        : "Fantasy",
        "dunia sihir"     : "Fantasy",
        "kerajaan"        : "Fantasy",
        "naga"            : "Fantasy",
        "dragon"          : "Fantasy",
        "peri"            : "Fantasy",
        "mitologi"        : "Fantasy",
        "dewa"            : "Fantasy",

        # History
        "history"         : "History",
        "sejarah"         : "History",
        "historical"      : "History",
        "masa lalu"       : "History",
        "peristiwa sejarah": "History",

        # Horror
        "horror"          : "Horror",
        "horor"           : "Horror",
        "seram"           : "Horror",
        "menyeramkan"     : "Horror",
        "hantu"           : "Horror",
        "setan"           : "Horror",
        "iblis"           : "Horror",
        "demon"           : "Horror",
        "ghost"           : "Horror",
        "zombie"          : "Horror",
        "vampire"         : "Horror",
        "kutukan"         : "Horror",
        "rumah hantu"     : "Horror",
        "paranormal"      : "Horror",
        "jumpscare"       : "Horror",

        # Music
        "music"           : "Music",
        "musik"           : "Music",
        "lagu"            : "Music",
        "penyanyi"        : "Music",
        "band"            : "Music",
        "konser"          : "Music",
        "dance"           : "Music",
        "menari"          : "Music",
        "musical"         : "Music",

        # Mystery
        "mystery"         : "Mystery",
        "misteri"         : "Mystery",
        "rahasia"         : "Mystery",
        "teka-teki"       : "Mystery",
        "investigation"   : "Mystery",
        "clue"            : "Mystery",
        "hilang"          : "Mystery",
        "kasus"           : "Mystery",

        # Romance
        "romance"         : "Romance",
        "romantis"        : "Romance",
        "cinta"           : "Romance",
        "percintaan"      : "Romance",
        "love story"      : "Romance",
        "pasangan"        : "Romance",
        "pacaran"         : "Romance",
        "pernikahan"      : "Romance",
        "wedding"         : "Romance",
        "relationship"    : "Romance",

        # Science Fiction
        "science fiction" : "Science Fiction",
        "sci fi"          : "Science Fiction",
        "sci-fi"          : "Science Fiction",
        "scifi"           : "Science Fiction",
        "fiksi ilmiah"    : "Science Fiction",
        "robot"           : "Science Fiction",
        "alien"           : "Science Fiction",
        "luar angkasa"    : "Science Fiction",
        "space"           : "Science Fiction",
        "planet"          : "Science Fiction",
        "galaxy"          : "Science Fiction",
        "masa depan"      : "Science Fiction",
        "future"          : "Science Fiction",
        "time travel"     : "Science Fiction",
        "mesin waktu"     : "Science Fiction",
        "teknologi"       : "Science Fiction",
        "ai"              : "Science Fiction",
        "artificial intelligence": "Science Fiction",

        # Thriller
        "thriller"        : "Thriller",
        "menegangkan"     : "Thriller",
        "tegang"          : "Thriller",
        "suspense"        : "Thriller",
        "psikologis"      : "Thriller",
        "psychological"   : "Thriller",
        "penuh tekanan"   : "Thriller",
        "teror"           : "Thriller",
        "dikejar"         : "Thriller",

        # War
        "war"             : "War",
        "perang"          : "War",
        "militer"         : "War",
        "tentara"         : "War",
        "soldier"         : "War",
        "army"            : "War",
        "battlefield"     : "War",
        "medan perang"    : "War",
        "pertempuran"     : "War",

        # Western
        "western"         : "Western",
        "koboi"           : "Western",
        "cowboy"          : "Western",
        "gurun"           : "Western",
        "sheriff"         : "Western",
        "wild west"       : "Western",
    }

    # ── Pemetaan keyword emosi ───────────────────────────────────────────────
    emotion_keywords = {
        # Joy
        "senang"          : "joy",
        "bahagia"         : "joy",
        "seru"            : "joy",
        "happy"           : "joy",
        "fun"             : "joy",
        "ceria"           : "joy",
        "menghibur"       : "joy",
        "feel good"       : "joy",
        "feel-good"       : "joy",
        "lucu"            : "joy",
        "ngakak"          : "joy",
        "kocak"           : "joy",
        "hangat"          : "joy",
        "heartwarming"    : "joy",
        "inspiratif"      : "joy",

        # Sadness
        "sedih"           : "sadness",
        "menangis"        : "sadness",
        "nangis"          : "sadness",
        "haru"            : "sadness",
        "terharu"         : "sadness",
        "mengharukan"     : "sadness",
        "galau"           : "sadness",
        "patah hati"      : "sadness",
        "heartbreak"      : "sadness",
        "kehilangan"      : "sadness",
        "tragis"          : "sadness",
        "tragedi"         : "sadness",
        "menyedihkan"     : "sadness",
        "suram"           : "sadness",
        "depresi"         : "sadness",
        "kesepian"        : "sadness",
        "lonely"          : "sadness",
        "emosional"       : "sadness",

        # Fear
        "takut"           : "fear",
        "ngeri"           : "fear",
        "seram"           : "fear",
        "menakutkan"      : "fear",
        "menyeramkan"     : "fear",
        "horor"           : "fear",
        "horror"          : "fear",
        "jumpscare"       : "fear",
        "paranormal"      : "fear",
        "gelap"           : "fear",
        "mencekam"        : "fear",
        "teror"           : "fear",
        "panik"           : "fear",
        "panic"           : "fear",

        # Anger
        "marah"           : "anger",
        "dendam"          : "anger",
        "balas dendam"    : "anger",
        "revenge"         : "anger",
        "kesal"           : "anger",
        "benci"           : "anger",
        "brutal"          : "anger",
        "sadis"           : "anger",
        "konflik"         : "anger",
        "kekerasan"       : "anger",
        "violence"        : "anger",

        # Surprise
        "kejutan"         : "surprise",
        "mengejutkan"     : "surprise",
        "plot twist"      : "surprise",
        "twist"           : "surprise",
        "mind blowing"    : "surprise",
        "mind-blowing"    : "surprise",
        "tidak terduga"   : "surprise",
        "tak terduga"     : "surprise",
        "unexpected"      : "surprise",
        "aneh"            : "surprise",
        "unik"            : "surprise",
        "misterius"       : "surprise",
        "ajaib"           : "surprise",
    }

    # ── Deteksi genre (bisa lebih dari 1) ───────────────────────────────────
    detected_genres = []
    for keyword, genre in genre_keywords.items():
        if re.search(rf'\b{re.escape(keyword)}\b', cleaned_input):
            if genre not in detected_genres:
                detected_genres.append(genre)

    # ── Deteksi emosi ────────────────────────────────────────────────────────
    detected_emotion = None
    for keyword, emotion in emotion_keywords.items():
        if re.search(rf'\b{re.escape(keyword)}\b', cleaned_input):
            detected_emotion = emotion
            break

    # ── Filter kombinasi genre + emosi ──────────────────────────────────────
    if detected_genres and detected_emotion and 'dominant_emotion' in df.columns:
        genre_filter = True
        for genre in detected_genres:
            genre_filter = genre_filter & df['genres'].str.contains(
                genre, case=False, na=False
            )
        combined_result = df[
            genre_filter & (df['dominant_emotion'] == detected_emotion)
        ]
        if not combined_result.empty:
            return combined_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # ── Filter genre saja ────────────────────────────────────────────────────
    if detected_genres:
        genre_filter = True
        for genre in detected_genres:
            genre_filter = genre_filter & df['genres'].str.contains(
                genre, case=False, na=False
            )
        genre_result = df[genre_filter]
        if not genre_result.empty:
            return genre_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # ── Filter emosi saja ────────────────────────────────────────────────────
    if detected_emotion is not None and 'dominant_emotion' in df.columns:
        emotion_result = df[df['dominant_emotion'] == detected_emotion]
        if not emotion_result.empty:
            return emotion_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    # ── Cari berdasarkan judul ───────────────────────────────────────────────
    if 'title_lower' in df.columns and cleaned_input != "":

        # Exact match dulu
        # Exact match dulu
        exact_match = df[df['title_lower'] == cleaned_input]
        if not exact_match.empty:
            idx = exact_match.index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = [s for s in sim_scores if s[0] != idx]
            sim_scores = [s for s in sim_scores if s[1] > 0.1]
            sim_scores = sim_scores[:top_n - 1]  # ✅ ambil top N-1 agar ada slot untuk film input

            if sim_scores:
                movie_indices = [idx] + [i[0] for i in sim_scores]  # ✅ film input di posisi pertama
                recommendations = df.iloc[movie_indices].copy()
                recommendations['cosine_score'] = [1.0] + [s[1] for s in sim_scores]  # ✅ skor film input = 1.0
                recommendations['final_score'] = (
                    0.6 * recommendations['cosine_score'] +
                    0.4 * recommendations['hybrid_score']
                )
                return recommendations.sort_values(
                    by='final_score', ascending=False
                ).drop(columns=['cosine_score', 'final_score'])

        # Partial match — minimal 3 karakter
        if len(cleaned_input) >= 3:
            partial_match = df[
                df['title_lower'].str.contains(
                    cleaned_input, case=False, na=False, regex=False
                )
            ]
            if not partial_match.empty:
                idx = partial_match.index[0]
                sim_scores = list(enumerate(cosine_sim[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                sim_scores = [s for s in sim_scores if s[0] != idx]
                sim_scores = [s for s in sim_scores if s[1] > 0.1]
                sim_scores = sim_scores[:top_n]

                if sim_scores:
                    movie_indices = [i[0] for i in sim_scores]
                    recommendations = df.iloc[movie_indices].copy()
                    recommendations['cosine_score'] = [s[1] for s in sim_scores]
                    recommendations['final_score'] = (
                        0.6 * recommendations['cosine_score'] +
                        0.4 * recommendations['hybrid_score']
                    )
                    return recommendations.sort_values(
                        by='final_score', ascending=False
                    ).drop(columns=['cosine_score', 'final_score'])

    # ── Tidak terdeteksi ─────────────────────────────────────────────────────
    return "tidak_terdeteksi"