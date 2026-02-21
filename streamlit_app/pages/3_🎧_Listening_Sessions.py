import streamlit as st
import json
import pandas as pd
from pathlib import Path
import os 
import sys
import utils
import perform_clustering

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_dir, 'src'))

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Listening Sessions Analysis", page_icon="🎧", layout="wide")

BASE_DIR = Path(__file__).parent.parent.parent  

# ============================================================
# DATA LOADING
# ============================================================

st.title("🎧 Listening Session Analysis")
st.markdown("To gain a deeper understanding of my streaming habits, I've taken my streaming data, identified listening sessions \
            (consecutive streams with no more than 10 minutes in between each stream), and trained a k-means clustering model. \
            This ML model identified 4 distinc types of listening sessions in my listening history.")
st.markdown("Explore the tabs below to see examples of each type of listening session k-means clustering identified.")
st.markdown("Then, navigate to the next page to run train your own k-means clustering model.")
st.subheader("🔎 My (user jqlistens') 2025 Listening Session Analysis")

DATA_DIR = BASE_DIR / 'data/processed'
CONFIG_DIR = BASE_DIR / 'config'
data_config = json.load(open(Path(CONFIG_DIR / 'data-params.json')))
session_stats_2025 = pd.read_csv(Path(DATA_DIR / data_config['default_session_stats_fp']))
df = pd.read_csv(Path(DATA_DIR / data_config['default_processed_scrobbles_fp']))
processed_scrobbles = df.loc[df.year == 2025].copy()

session_tab_labels = ["🧘 Weekend Wind Down - Cluster 1",
                      "💡 New Discovery - Cluster 2", 
                      "⏳ Deep Dive Marathon - Cluster 3",
                      "🌙 Late Night Faves - Cluster 4"
                      ]

example_labels = {
    0:['Go-to Artists',
       'My Favorite Tracks'],
    1:['Catching Up on New Music Friday',
       'New Discoveries Spanning Eras and Genres'],
    2:['1st Listen of the 2026 AOTY - DeBÍ TiRAR MáS FOToS by Bad Bunny',
       'Playlist Sesh - West Coast Rap Exploration'],
    3:['R&B Hits Old and New',
       'Saturday Night R&B']
}

example_session_ids = {
    0:[5243,5488],
    1:[5032,5361],
    2:[4970,5111],
    3:[5503,4964]
}

example_insights = {
    cluster:[utils.create_example_insight(cluster, index, example_labels, 
                                 example_session_ids, processed_scrobbles) 
            for index in range(2)]
    for cluster in example_session_ids
}

cluster_descriptions = [
    "This cluster represents moderate-length afternoon and evening\
    sessions where I typically listened to my favorite artists, cycling through 7-8 songs over 20-25 minutes.\
    The familiarity of most songs, with the occasional new discovery, \
    suggests comfortable background listening or focused work sessions.",
    "Sessions in this cluster are typically brief 10-minute sessions for exploration, \
    during which I dip into new artists, albums, and songs across just 3-4 tracks. \
    Happening primarily on weekend afternoons during summer, \
    these sessions reflect active music discovery, quickly sampling new content before moving on.",
    "These sessions are my longest at 80+ minutes, typically on Saturday afternoon. \
    This cluster's sessions are most diverse, consisting of 22-23 different songs across 8-10 different artists and a dozen albums. \
    These spring sessions represent active, engaged listening where I'm exploring variety but also discovering new music, \
    likely during leisure time, long workouts, or creative work.",
    "This last cluster consists of my shortest sessions at 5-10 minutes, happening late at night or in the early morning hours, \
    predominantly on Mondays during winter. These quick hits play 3-4 songs I \
    already know well across 2-3 artists, \
    suggesting brief mood-setting moments or transitions between activities."
]

tabs = st.tabs(session_tab_labels)
cluster = 0
for tab in tabs:
    example1 = example_insights[cluster][0]
    example2 = example_insights[cluster][1]
    with tab:
        st.markdown(cluster_descriptions[cluster])
        utils.render_cluster_tab(example1, 1)
        st.divider()
        utils.render_cluster_tab(example2, 2)
    cluster += 1
st.divider()
st.subheader("Check out the other pages:")
st.page_link("pages/1_📊_Overview.py", label='Overview', icon="📊")
st.page_link("pages/2_🗓️_Streaming_Calendar.py", label='Streaming Calendar', icon="🗓️")
st.page_link("pages/4_🧠_Train_Your_ML_Model_-_Listening_Sessions.py", label='Train Your Listening Sessions Model', icon="🧠")
 
with st.sidebar:
    st.markdown("""
    Created by [Jacqueline Lee](https://www.linkedin.com/in/jacqueline-kc-lee/)
    
    [🐙 GitHub](https://github.com/jacquelinekclee)
                
    [🤝 LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/)
                
    [📧 Email](mailto:jacquelinekclee@yahoo.com)
    """)