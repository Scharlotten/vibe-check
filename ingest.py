import streamlit as st
import astrapy
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel
import requests
from openai import OpenAI


@st.cache_resource
def get_collection(collection_name):
    client = astrapy.DataAPIClient(st.secrets["ASTRA_DB_APPLICATION_TOKEN"])
    database = client.get_database_by_api_endpoint(st.secrets["ASTRA_DB_API_ENDPOINT"])
    collection = database.get_collection(collection_name)
    print("collection:", collection)
    return collection

if "song_collection" not in st.session_state:
    st.session_state["song_collection"] = get_collection(st.secrets["ASTRA_DB_COLLECTION_NAME"])

if "pid_collection" not in st.session_state:
    st.session_state["pid_collection"] = get_collection(st.secrets["ASTRA_DB_PID_COLLECTION_NAME"])

@st.cache_resource
def load_vertexai_model():

    credentials = service_account.Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"])
    vertexai.init(
        project=st.secrets["GCP_SERVICE_ACCOUNT"]["project_id"],
        credentials=credentials
    )
    model = GenerativeModel("gemini-1.5-pro-001")
    print("model:", model)
    return model

def load_gpt_model():
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    return client


if "vertexai_model" not in st.session_state:
    st.session_state["vertexai_model"] = load_vertexai_model()

if "gpt_model" not in st.session_state:
    st.session_state["gpt_model"] = load_gpt_model()
    

@st.cache_data
def get_current_pid():
    pid_document = st.session_state.pid_collection.find_one({})
    if pid_document:
        return pid_document["pid"]
    else:
        return

if "current_pid" not in st.session_state:
    st.session_state.current_pid = get_current_pid()

@st.cache_data
def get_spotify_auth_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': st.secrets["SPOTIFY_CLIENT_ID"],
        'client_secret': st.secrets["SPOTIFY_CLIENT_SECRET"],
    })
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    return access_token

@st.cache_data
def get_tracks_from_spotify(playlist_id):
    access_token = get_spotify_auth_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    response = requests.get(playlist_url, headers=headers)
    playlist_tracks = response.json()
    return playlist_tracks

@st.cache_data
def get_song_description(song_name, artist_name):
    prompt = f"""
        You are an AI agent that helps users determine what songs to play to match
        their setting. Based on the included song name and artist, '{song_name}' by '{artist_name}', write up a description of what
        kind of setting would be appropriate to listen to. Do not make assumptions based purely on the song name, you should
        try to use real information about the song to come up with your setting description.
    """
    #contents = [prompt]
    #response = st.session_state.model.generate_content(contents)
    #return response.text
    response = st.session_state.gpt_model.chat.completions.create(
        model="gpt-4o",
        messages=
        [
            {"role": "system", "content": prompt},
        ]
    )
    return response.choices[0].message.content.strip()

def load_tracks_to_astra(new_playlist_id):
    playlist_tracks = get_tracks_from_spotify(new_playlist_id)
    for item in playlist_tracks['items']:
        track = item['track']
        song = track["name"]
        artist = track['artists'][0]['name']
        song_url = track['external_urls']['spotify']

        print(f"Song Name: {song} | Artist Name: {artist} | Song URL: {song_url}")

        existing_document = st.session_state.song_collection.find_one({"Song_URL": song_url})
        if existing_document:
            print("Skipping this song - already in DB")
            pass
        else:
            description = get_song_description(song, artist)
            print(description)
            document = {
                "Song_Name": song,
                "Artist": artist,
                "Song_URL": song_url,
                "$vectorize": description
            }
            st.session_state.song_collection.insert_one(document)
    st.session_state.pid_collection.insert_one({"pid": new_playlist_id})
    st.session_state.current_pid = new_playlist_id

def clear_playlist():
    print("clear playlist called")
    # st.session_state.song_collection.delete_many({})
    st.session_state.pid_collection.delete_many({})

def load_playlist():
    print("load playlist called")
    clear_playlist()
    load_tracks_to_astra(st.session_state.pid_input)


### UI ###
st.title("Vibe Check :musical_note:")

with st.container(border=True):
    st.write("**Current Playlist ID:** ", st.session_state.current_pid)
    st.link_button("Open in Spotify", "https://open.spotify.com/user/spotify/playlist/%s" % st.session_state.current_pid)
    st.button("Clear")

with st.form(key="new_playlist_form"):
    st.markdown(
    """
    Copy/paste a Spotify playlist ID into the box below and click "Load to Astra DB". 
    
    This application will:
    1. Retrieve the songs from that playlist using the Spotify API
    1. Generate descriptions of those songs using an LLM
    1. Upload the song information and descriptions to the Astra DB Vector Store
    """
    )
    new_pid = st.text_input(
        "Sample Playlist ID: 3C5CqRlEoisNEusrgg7kEX",
        key="pid_input"
    )
    
    st.form_submit_button("Load to Astra DB", on_click=load_playlist)
