import streamlit as st
from vertexai.generative_models import GenerativeModel, Part, Image


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
        response = st.session_state.model.generate_content(contents)
        setting_description = response.candidates[0].content.parts[0].text
        st.session_state.user_feedback = setting_description
        if st.session_state.text_input:
            # Photo and text input
            st.session_state.user_feedback += text_input
        # Photo input only
        findSongs(st.session_state.user_feedback)
    else:
        if st.session_state.text_input:
            # Text input only
            findSongs(st.session_state.text_input)
            st.session_state.user_feedback = st.session_state.text_input
        else:
            # No input
            st.session_state.user_feedback = None

def findSongs(setting_description):
    print("findSongs called")
    top_songs = list(st.session_state.song_collection.find(
        sort={"$vectorize": setting_description},
        projection={"_id": 0, "$vectorize": 1, "$vector": 0},
        limit=5,
        include_similarity=True
    ))
    # print(top_songs)
    st.session_state.top_songs = top_songs
    return


### UI ###
st.title("Vibe Check :musical_note:")

photo_method = st.radio(
    "Select an image upload method:",
    ["Camera", "Upload"],
)

with st.form(key="query_form"):
    st.header("Multimodal Inputs")
    if photo_method == "Camera":
        photo_input = st.camera_input(
            "Take a picture of your setting:", 
            key="photo_input",
        )
    elif photo_method == "Upload":
        photo_input = st.file_uploader(
            "Upload a photo:",
            key="photo_input",
        )
    text_input = st.text_input(
        "Write a description of your setting:",
        key="text_input"
    )
    st.form_submit_button(on_click=handleSubmit)

with st.container(border=True):
    st.header("Outputs")
    show_prompt = st.checkbox("Show prompt sent to the LLM")
    show_df = st.checkbox("Show data retrieved from Astra DB")
    if st.session_state.user_feedback:
        if show_prompt:
            st.subheader("Prompt")
            with st.container(border=True):
                st.write(st.session_state.user_feedback)
        if show_df:
            st.subheader("Best Matches Retrieved from Astra DB")
            st.dataframe(
                st.session_state.top_songs,
                column_config={
                    "Song_URL": st.column_config.LinkColumn()
                }
            )
        st.subheader("Top Recommended Songs")
        for song in st.session_state.top_songs:
            name = song.get("Song_Name", "N/A")
            artist = song.get("Artist", "N/A")
            url = song.get("Song_URL", "")
            st.write("- [%s - %s](%s)" % (name, artist, url))
    else:
        st.info("No photo or text input uploaded.")
    