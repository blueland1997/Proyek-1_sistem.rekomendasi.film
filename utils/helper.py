def hybrid_label(score):
    if score >= 0.75:
        return "Sangat Direkomendasikan"
    elif score >= 0.5:
        return "Direkomendasikan"
    else:
        return "Cukup Direkomendasikan"

def get_all_genres(df):
    all_genres = set()
    for genres in df['genres'].dropna():
        for g in genres.split(','):
            all_genres.add(g.strip())
    return sorted(all_genres)