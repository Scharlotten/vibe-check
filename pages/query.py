import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

vertexai.init(project=st.secrets["GCP_PROJECT"])
model = GenerativeModel("gemini-1.5-pro-001")

prompt = """
    You are an AI agent that helps users determine what songs to play to match their setting. Based on the included image and/or text describing the setting, write up a description of what kind of music would be appropriate to listen to.
"""

if 'setting_description' not in st.session_state:
    st.session_state.setting_description = ''


def handleSubmit():
    print('submit!')
    image = Image.from_bytes(st.session_state.photo_input.getvalue())
    image_part = Part.from_image(image)
    print("image_part", image_part)
    contents = [image_part, prompt]
    setting_description = model.generate_content(contents)
    st.session_state.setting_description = setting_description


### UI ###
st.title("Vibe Check :musical_note:")

with st.form(key="query_form"):
    photo_input = st.camera_input("Take a picture of your setting:", key="photo_input")
    # text = st.text_input(
    #     "Describe the vibe:"
    # )
    st.form_submit_button(on_click=handleSubmit)

if st.session_state.setting_description:
    st.write(st.session_state.setting_description)