import streamlit as st
# # Pull data from the collection
# # Reruns only when the query changes or after 10 min.
# @st.cache_data(ttl=600)
# def get_data():
#     collection = database.get_collection("vibe_check_ingestion")
#     print(collection)

# get_data()

ingest_page = st.Page("./pages/ingest.py", title="Connect to Your Playlist", icon=":material/add_circle:")
query_page = st.Page("./pages/query.py", title="Find Songs", icon=":material/delete:")

pg = st.navigation([ingest_page, query_page])
st.set_page_config(page_title="Vibe Check", page_icon=":musical_note:")
pg.run()
