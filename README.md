# Vibe Check - Multimodal Music Search Application

todo: insert text describing the project and motivation

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vibe-check.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Get your credentials and put them in secrets.toml

3. Set up your collections using Astra Vectorize
- Connect the DB to OpenAI Integration in Astra Portal
- Either run create_collections.py or create collections through the UI

4. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
