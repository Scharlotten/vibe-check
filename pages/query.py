import streamlit as st
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image
import astrapy

@st.cache_resource
def load_model():
    credentials = service_account.Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"])
    vertexai.init(
        project=st.secrets["GCP_SERVICE_ACCOUNT"]["project_id"],
        credentials=credentials
    )
    model = GenerativeModel("gemini-1.5-pro-001")
    print("model:", model)
    return model

model = load_model()

@st.cache_resource
def get_collection():
    client = astrapy.DataAPIClient(st.secrets["ASTRA_DB_APPLICATION_TOKEN"])
    database = client.get_database_by_api_endpoint(st.secrets["ASTRA_DB_API_ENDPOINT"])
    collection = database.get_collection(st.secrets["ASTRA_DB_COLLECTION_NAME"])
    print("collection:", collection)
    return collection

collection = get_collection()

prompt = """
    You are an AI agent that helps users determine what songs to play to match their setting. Based on the included image and/or text describing the setting, write up a description of what kind of music would be appropriate to listen to.
"""

if 'user_feedback' not in st.session_state:
    st.session_state.user_feedback = ''
if 'top_songs' not in st.session_state:
    st.session_state.top_songs = ''


def handleSubmit():
    print('submit!')
    if st.session_state.photo_input:
        image = Image.from_bytes(st.session_state.photo_input.getvalue())
        image_part = Part.from_image(image)
        contents = [image_part, prompt]
        response = model.generate_content(contents)
        setting_description = response.candidates[0].content.parts[0].text
        st.session_state.user_feedback = setting_description
        findSongs(setting_description)
    else:
        st.session_state.user_feedback = None

def findSongs(setting_description):
    print("findSongs called")
    top_songs = list(collection.find(
        sort={"$vectorize": setting_description},
        projection={"_id": 0, "$vectorize": 1, "$vector": 0},
        limit=5,
        include_similarity=True
    ))
    st.session_state.top_songs = top_songs
    return


### UI ###
st.title("Vibe Check :musical_note:")

photo_method = st.radio(
    "Select an image upload method:",
    ["Camera", "Upload"],
)

with st.form(key="query_form"):
    if photo_method == "Camera":
        photo_input = st.camera_input(
            "Take a picture of your setting:", 
            key="photo_input",
        )
    elif photo_method == "Upload":
        st.write("The photo upload function is not yet implemented.")
        photo_input = st.file_uploader(
            "Upload a photo:",
            key="photo_input",
        )
    st.form_submit_button(on_click=handleSubmit)

if st.session_state.user_feedback:
    st.write(st.session_state.user_feedback)
    st.dataframe(st.session_state.top_songs)
else:
    st.write("No image uploaded.")
    