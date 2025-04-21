import pickle
import streamlit as st
import requests
import pandas as pd

# Load movie list and similarity matrix
movies = pickle.load(open('model/movie_list.pkl', 'rb'))  # movies should be a DataFrame
similarity = pickle.load(open('model/similarity.pkl', 'rb'))  # similarity matrix


# Function to fetch movie posters from TMDB API
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


# Recommendation function based on movie or survey data
def recommend(movie=None, survey_data=None):
    recommended_movie_names = []
    recommended_movie_posters = []

    if movie:
        # Get index of the selected movie
        index = movies[movies['title'] == movie].index[0]

        # Get distances based on cosine similarity
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

        # Start from index 1 to skip the selected movie itself
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movieId  # Ensure this matches the column name in your DataFrame
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_movie_posters.append(fetch_poster(movie_id))
    elif survey_data:
        # Use survey data to recommend movies
        preferred_genres = survey_data.get("preferred_genres", [])

        # Filter movies based on the user's preferred genres
        filtered_movies = movies[movies['genres'].apply(lambda x: any(genre in x for genre in preferred_genres))]

        for _, movie in filtered_movies.head(5).iterrows():
            movie_id = movie.movieId
            recommended_movie_names.append(movie.title)
            recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters


# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

# Create Profile Section
st.subheader("Create Your Profile")

# Dropdown for selecting a contact method
contact_method = st.selectbox("How would you like to be contacted?", ["Email", "Phone", "None"])

if contact_method == "Email":
    email = st.text_input("Enter your email address:")
elif contact_method == "Phone":
    phone = st.text_input("Enter your phone number:")

# Movie Recommendation Survey
st.subheader("Movie Recommendation Survey")

# Age Question
age = st.selectbox("Age*", ["Under 18", "18 to 24", "25 to 34", "35 to 44", "45 to 55", "65 and over"])

# Importance of Storyline
storyline_importance = st.selectbox(
    "How important is a strong storyline or plot to you in a movie?*",
    ["1 - Not Important", "2", "3", "4", "5 - Most Important"]
)

# Importance of Complex Characters
complex_characters = st.selectbox(
    "How much do you enjoy movies with complex characters or deep emotional themes?*",
    ["1 - Not Important", "2", "3", "4", "5 - Most Important"]
)

# Movie Watching Frequency
movie_frequency = st.selectbox(
    "How often do you watch movies?*",
    ["1 - Rarely", "2", "3", "4", "5 - Almost every day"]
)

# Movie Genre Preferences (Multiple Dropdowns)
genres = st.multiselect(
    "Choose 5 movie genres that you prefer*",
    ["Action", "Adventure", "Animation", "Comedy", "Drama", "Fantasy", "Horror", "Mystery", "Romance",
     "Sci-Fi (Science Fiction)", "Thriller", "Crime", "Documentary", "Musical", "Family", "History",
     "Biography", "War", "Western", "Sport"],
    max_selections=5
)

# Option to create a profile and save the survey data
create_profile = st.checkbox("Create Profile")

if create_profile:
    # Create a dictionary to store the user's profile information
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

    # Display confirmation message
    st.write("Profile created successfully! You can now receive personalized recommendations.")
    st.write("Your Profile Data:")
    st.json(user_profile)  # Display the profile data

    # Optionally, save the profile information into a CSV file
    df = pd.DataFrame([user_profile])
    df.to_csv("user_profiles.csv", mode='a', header=False, index=False)

# Movie Selection Section
st.subheader("Select a Movie for Recommendations")

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Get Recommendations'):
    # If a movie is selected, show recommendations based on similarity
    if selected_movie:
        names, posters = recommend(movie=selected_movie)  # Recommendations based on movie selection
    else:
        # If no movie is selected, use survey data to recommend movies
        if create_profile:  # Ensure that the profile is created before recommending
            names, posters = recommend(survey_data=user_profile)
        else:
            st.write("Please complete the survey to get recommendations.")

    # Display the recommendations in a grid layout
    if names and posters:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])  # Movie title
                st.image(posters[i])  # Movie poster
