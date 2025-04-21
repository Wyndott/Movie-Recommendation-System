import pickle
import streamlit as st
import requests
import pandas as pd

# --- Load Saved Files ---
movies = pickle.load(open('model/movie_list.pkl', 'rb'))  # movies should be a DataFrame
# similarity = pickle.load(open('model/similarity.pkl', 'rb'))  # Removed since not used

# --- Function to fetch movie posters ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=Error"

# --- Recommendation Function (Only survey-based for now) ---
def recommend(movie=None, survey_data=None):
    recommended_movie_names = []
    recommended_movie_posters = []

    if survey_data:
        preferred_genres = survey_data.get("preferred_genres", [])
        filtered_movies = movies[movies['genres'].apply(lambda x: any(genre in x for genre in preferred_genres))]

        for _, movie in filtered_movies.head(5).iterrows():
            movie_id = movie.movieId
            recommended_movie_names.append(movie.title)
            recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters

# --- Streamlit UI ---
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

# --- Create Profile Section ---
st.subheader("Create Your Profile")

contact_method = st.selectbox("How would you like to be contacted?", ["Email", "Phone", "None"])
email, phone = None, None
if contact_method == "Email":
    email = st.text_input("Enter your email address:")
elif contact_method == "Phone":
    phone = st.text_input("Enter your phone number:")

# --- Survey Section ---
st.subheader("Movie Recommendation Survey")

age = st.selectbox("Age*", ["Under 18", "18 to 24", "25 to 34", "35 to 44", "45 to 55", "65 and over"])
storyline_importance = st.selectbox("How important is a strong storyline or plot to you in a movie?*",
                                    ["1 - Not Important", "2", "3", "4", "5 - Most Important"])
complex_characters = st.selectbox("How much do you enjoy movies with complex characters or deep emotional themes?*",
                                  ["1 - Not Important", "2", "3", "4", "5 - Most Important"])
movie_frequency = st.selectbox("How often do you watch movies?*",
                               ["1 - Rarely", "2", "3", "4", "5 - Almost every day"])
genres = st.multiselect("Choose 5 movie genres that you prefer*",
                        ["Action", "Adventure", "Animation", "Comedy", "Drama", "Fantasy", "Horror", "Mystery",
                         "Romance", "Sci-Fi (Science Fiction)", "Thriller", "Crime", "Documentary", "Musical",
                         "Family", "History", "Biography", "War", "Western", "Sport"], max_selections=5)

create_profile = st.checkbox("Create Profile")

if create_profile:
    user_profile = {
        "contact_method": contact_method,
        "email": email if contact_method == "Email" else None,
        "phone": phone if contact_method == "Phone" else None,
        "age": age,
        "storyline_importance": storyline_importance,
        "complex_characters": complex_characters,
        "movie_frequency": movie_frequency,
        "preferred_genres": genres
    }

    st.write("Profile created successfully! You can now receive personalized recommendations.")
    st.write("Your Profile Data:")
    st.json(user_profile)

    df = pd.DataFrame([user_profile])
    df.to_csv("user_profiles.csv", mode='a', header=False, index=False)

# --- Movie Selection Section (not used without similarity.pkl) ---
st.subheader("Recommendations Based on Your Survey")

# ✅ Initialize empty lists to avoid runtime errors
names, posters = [], []

if st.button('Get Recommendations'):
    if create_profile:
        names, posters = recommend(survey_data=user_profile)
    else:
        st.write("Please complete the survey to get recommendations.")

# ✅ Display recommendations safely
if names and posters:
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
