import streamlit as st
import astrapy



### Cached Resources and Data ###

# Initialize connection
@st.cache_resource
def init_connection():
    client = astrapy.DataAPIClient(st.secrets["ASTRA_DB_APPLICATION_TOKEN"])
    database = client.get_database(st.secrets["ASTRA_DB_API_ENDPOINT"])
    print("init connection:", database)
    return database

database = init_connection()

if "database" not in st.session_state:
    st.session_state.database = database

### UI ###
st.title("Vibe Check :musical_note:")

if "attendance" not in st.session_state:
    st.session_state.attendance = set()


def take_attendance():
    if st.session_state.name in st.session_state.attendance:
        st.info(f"{st.session_state.name} has already been counted.")
    else:
        st.session_state.attendance.add(st.session_state.name)


with st.form(key="my_form"):
    st.text_input("Name", key="name")
    st.form_submit_button("I'm here!", on_click=take_attendance)



