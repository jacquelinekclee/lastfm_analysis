import streamlit as st
import json
import pandas as pd
from pathlib import Path
import process_data

st.set_page_config(page_title="Streaming Analysis", page_icon="🎵", layout="wide")

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data(uploaded_file=None):
    """Load scrobble data from file upload or default path."""
    if uploaded_file is not None:
        uploaded_file.seek(0)
        raw_scrobbles = pd.read_csv(uploaded_file)
        processed_scrobbles = process_data.process_scrobbles(raw_scrobbles)
    else:
        BASE_DIR = Path(__file__).parent  
        DATA_DIR = BASE_DIR / 'data/processed'
        CONFIG_DIR = BASE_DIR / 'config'
        data_config = json.load(open(Path(CONFIG_DIR / 'data-params.json')))
        processed_scrobbles = pd.read_csv(Path(DATA_DIR / data_config['default_processed_scrobbles_fp']))
    processed_scrobbles['datetime'] = pd.to_datetime(processed_scrobbles['datetime'])
    return processed_scrobbles

st.title("🎵⏪ Play Back - Music Streaming History Deep Dive")
st.markdown("No matter which music streaming service you use, Play Back unlocks \
            personalized insights into your listening habits.")
st.markdown("Explore your streaming history with interactive charts and graphs, \
            from high-level streaming patterns to detailed yearly and quarterly heatmaps. \
            Take your analysis to the next level by using Machine Learning to uncover your \
            unique listening session types. Get started with your last.fm data, or explore \
            my own music streaming history to get an idea of what you can uncover.")
col1, col2 = st.columns([1.5, 1], vertical_alignment="center")
col1.info('To get started, upload your raw streaming data from last.fm \nThen, use the sidebar to navigate through the app.')
col2.link_button("Download your last.fm data here", "https://mainstream.ghan.nl/export.html",
               help = "Opens a new tab to https://mainstream.ghan.nl/export.html",
               type = 'primary', icon = ":material/download:", width = 'stretch')
st.markdown("If you don't want to upload your data, you will still be able to interact with Play Back using my streaming data!")
# --- File Upload ---
st.subheader("📂 Upload Your Raw Data (optional)")
st.markdown("Upload your raw streaming data downloaded from last.fm below for processing.")
st.markdown("Skip this step to view my (user jqlisten) streaming insights!")

uploaded_file = st.file_uploader(
    label="Upload your CSV of raw streams",
    type=['csv'],
    help="Upload your streaming data as a CSV file. Required columns:\
        'uts', 'utc_time', 'artist', 'album', 'track'"
)
if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")
    df = load_data(uploaded_file)
    st.success("✅ Streams processed successfully!")
    st.download_button("Download your processed music streaming data (.csv)", 
                       df.to_csv(index = False), file_name="processed_streams.csv", 
                       help="This .csv includes your processed streams, including \
                        standardized album and artist columns, listening session IDs, \
                        and more.", type = 'primary',
                       on_click="ignore", icon=":material/csv:")
else:
    st.info("Using default data. Upload a CSV to use your own.")
    df = load_data()

# app overview
st.subheader("👩🏻‍💻 App Overview")
st.text("Use the sidebar to navigate through the app. Get a preview of each page in the tabs below.")
pages = ['📊 Overview', '🗓️ Streaming Calendar', 
         '🎧 Listening Sessions', '🧠 Train Your Listening Sessions Model']

page1, page2, page3, page4 = st.tabs(pages)

with page1:
    st.text('Get a high-level overview of your listening habits.')
    st.markdown('Focus: :violet-badge[:material/analytics: Data Analysis]')
    st.page_link("pages/1_📊_Overview.py", label='Overview', icon="📊")
with page2:
    st.text('Dive deeper into your streaming history with yearly and quarterly heatmaps.')
    st.markdown('Focus: :violet-badge[:material/full_stacked_bar_chart: Data Visualization]')
    st.page_link("pages/2_🗓️_Streaming_Calendar.py", label='Streaming Calendar', icon="🗓️")
with page3:
    st.markdown('Investigate exactly *how* you listen to music by using \
                unsupervised machine learning to uncover your different types of listening sessions.\
                Analyze my results of using ML to group together my listening sessions \
                to get an idea of what kinds of insights you can pull with ML.')
    st.markdown('Focus: :violet-badge[:material/model_training: Machine Learning - K-Means Clustering]')
    st.page_link("pages/3_🎧_Listening_Sessions.py", label='Listening Sessions', icon="🎧")
with page4:
    st.markdown('Investigate exactly *how* you listen to music by using \
                unsupervised machine learning to uncover your different types of listening sessions.\
                Train your own clustering model with your streaming data, and analyze the results to see \
                what kind of insights into your listening habits are revealed with ML.')
    st.markdown('Focus: :violet-badge[:material/model_training: Machine Learning - K-Means Clustering]')
    st.page_link("pages/4_🧠_Train_Your_ML_Model_-_Listening_Sessions.py", label='Train Your Listening Sessions Model', icon="🧠")

with st.sidebar:
    st.markdown("""
    Created by [Jacqueline Lee](https://www.linkedin.com/in/jacqueline-kc-lee/)
    
    [🐙 GitHub](https://github.com/jacquelinekclee)
                
    [🤝 LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/)
                
    [📧 Email](mailto:jacquelinekclee@yahoo.com)
    """)

# Load and store in session state
st.session_state['df'] = df
st.session_state['uploaded_file'] = uploaded_file
