def get_hybrid_thresholds(df):
    q25 = df['hybrid_score'].quantile(0.25)
    q75 = df['hybrid_score'].quantile(0.75)
    return q25, q75


def hybrid_label(score, q25, q75):
    if score >= q75:
        return "Sangat Direkomendasikan"
    elif score >= q25:
        return "Direkomendasikan"
    else:
        return "Cukup Direkomendasikan"


def get_all_genres(df):
    all_genres = set()
    for genres in df['genres'].dropna():
        for g in genres.split(','):
            all_genres.add(g.strip())
    return sorted(all_genres) 

import requests

def get_movie_poster(movie_id, api_key):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": api_key}
        
        response = requests.get(url, params=params)
        data = response.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w300{poster_path}"
    except:
        pass
    return None