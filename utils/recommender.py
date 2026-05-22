def get_recommendations(df, cosine_sim, user_input, top_n=5):

    cleaned_input = user_input.lower().strip()

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

    if detected_emotion is not None and 'dominant_emotion' in df.columns:
        emotion_result = df[df['dominant_emotion'] == detected_emotion]
        if not emotion_result.empty:
            return emotion_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    if detected_genre is not None:
        genre_result = df[
            df['genres'].str.contains(detected_genre, case=False, na=False)
        ]
        if not genre_result.empty:
            return genre_result.sort_values(
                by='hybrid_score', ascending=False
            ).head(top_n)

    for title in df['title_lower']:
        if cleaned_input in title:
            idx = df[df['title_lower'] == title].index[0]

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:top_n + 1]

            movie_indices = [i[0] for i in sim_scores]
            recommendations = df.iloc[movie_indices]

            return recommendations.sort_values(
                by='hybrid_score', ascending=False
            )

    return None