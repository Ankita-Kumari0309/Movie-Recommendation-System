import pickle
import streamlit as st
import requests
import pandas as pd

# ----------- Fetch movie details from TMDB API ------------
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={your_API_kEY}b&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster_path = data.get('poster_path', '')
    overview = data.get('overview', 'No description available.')
    rating = data.get('vote_average', 'N/A')
    release_date = data.get('release_date', 'N/A')
    genres = [genre['name'] for genre in data.get('genres', [])]
    trailer = fetch_trailer(movie_id)

    full_poster_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
    return full_poster_path, overview, rating, release_date, genres, trailer

# ----------- Fetch movie trailer link from TMDB API ------------
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=20a69b5d630370cf25cc05f8da975d1b&language=en-US"
    response = requests.get(url)
    data = response.json()
    trailers = [video for video in data.get('results', []) if video['type'] == 'Trailer']
    if trailers:
        return f"https://www.youtube.com/watch?v={trailers[0]['key']}"
    else:
        return None

# ----------- Recommendation logic ------------
def recommend(movie):
    index = movies[movies['title'].str.lower() == movie.lower()].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    movie_names = []
    movie_posters = []
    movie_overviews = []
    movie_ratings = []
    movie_release_dates = []
    movie_genres = []
    movie_trailers = []

    added_ids = set()

    # First: Add selected movie itself
    selected_movie_id = movies.iloc[index].id
    poster, overview, rating, release_date, genres, trailer = fetch_movie_details(selected_movie_id)

    movie_names.append(movies.iloc[index].title)
    movie_posters.append(poster)
    movie_overviews.append(overview)
    movie_ratings.append(rating)
    movie_release_dates.append(release_date)
    movie_genres.append(genres)
    movie_trailers.append(trailer)
    added_ids.add(selected_movie_id)

    # Then: Add 7 similar movies
    for i in distances:
        movie_id = movies.iloc[i[0]].id
        if movie_id in added_ids:
            continue
        poster, overview, rating, release_date, genres, trailer = fetch_movie_details(movie_id)

        movie_names.append(movies.iloc[i[0]].title)
        movie_posters.append(poster)
        movie_overviews.append(overview)
        movie_ratings.append(rating)
        movie_release_dates.append(release_date)
        movie_genres.append(genres)
        movie_trailers.append(trailer)
        added_ids.add(movie_id)

        if len(movie_names) == 8:
            break

    return movie_names, movie_posters, movie_overviews, movie_ratings, movie_release_dates, movie_genres, movie_trailers

# ----------- Streamlit UI ------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title('🎥 Movie Recommender System')

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Movie selection dropdown
movie_list = movies['title'].values
selected_movie_dropdown = st.selectbox("🎞️ Select a movie from the dropdown", ["Select a movie..."] + list(movie_list))
selected_movie = selected_movie_dropdown if selected_movie_dropdown != "Select a movie..." else None

# Show recommendations
if st.button('🍿 Show Recommendations') and selected_movie:
    names, posters, overviews, ratings, release_dates, genres, trailers = recommend(selected_movie)

    for row in range(2):
        cols = st.columns(4)
        for i in range(4):
            idx = row * 4 + i
            if idx < len(names):
                with cols[i]:
                    st.image(posters[idx], use_container_width=True)
                    st.markdown(f"**🎬 {names[idx]}**")
                    st.markdown(f"⭐ **Rating**: {ratings[idx]} | 📅 **Release Date**: {release_dates[idx]}")
                    st.markdown(f"🎭 **Genres**: {', '.join(genres[idx])}")

                    short_overview = ' '.join(overviews[idx].split()[:20]) + "..."
                    st.markdown("📝 **Overview:** " + short_overview)
                    with st.expander("Read more"):
                        st.write(overviews[idx])

                    if trailers[idx]:
                        st.markdown(f"[🎬 Watch Trailer]({trailers[idx]})", unsafe_allow_html=True)
                    else:
                        st.markdown("🚫 **No trailer available**")
