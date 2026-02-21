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

import models.clustering as clustering 

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Train Your ML Model - Listening Sessions Clustering", 
                   page_icon="🧠", layout="wide")

# Check if data exists in session state
if 'df' not in st.session_state:
    st.warning("⚠️ No data loaded. Please return to the home page.")
    st.page_link("0_🎵⏪_Play_Back_Home_Page.py", label='Home', icon="🏠")
    st.stop()  # Stops the page from rendering further
else:
    df = st.session_state['df']

if 'uploaded_file' not in st.session_state:
    uploaded_file = False
else:
    uploaded_file = st.session_state['uploaded_file']

st.session_state['ready_to_configure'] = True
session_state_variables = ['session_stats', 'model_configured', 'model_ready',
                           'train_model', 'year', 'model_trained', 'n_clusters', 'processed_scrobbles']

def clear():
    '''
    reset session state
    '''
    st.session_state['n_clusters'] = None
    st.session_state['year'] = None
    st.session_state['session_stats'] = None
    st.session_state['model_configured'] = False
    st.session_state['model_trained'] = False
    st.session_state['model_ready'] = False
    st.session_state['train_model'] = False

# Initialize session state
def initialize_session_state(vars):
    '''
    iterate through provided variables and initialize them as None if
    they don't exist
    Args:
        vars (list): list of strings with session state variable names
    '''
    for var in vars:
        if var not in st.session_state:
            st.session_state[var] = False

def clear_train_button():
    st.session_state['model_trained'] = False
    st.session_state['model_ready'] = False
    st.session_state['train_model'] = True

initialize_session_state(session_state_variables)

# ============================================================
# DATA LOADING
# ============================================================

st.title("🧠 Train Your ML Model - Listening Sessions Clustering")
st.markdown("Dive deeper into your streaming habits by analyzing your listening sessions. \
            Train your own k-means clustering model, and take a look at the typical types\
            of listening sessions you had over a given year.")

if st.session_state['ready_to_configure']:
    with st.form("configure_model"):
        st.subheader("⚙️ Configure Your Clustering Model")
        n_clusters = st.slider("Choose the number of clusters", min_value=2, max_value=6, 
                value=4, step=1)
        st.session_state['n_clusters'] = n_clusters
        month_counts = df[['year', 'month']].groupby('year').nunique()
        available_full_years = sorted(month_counts[month_counts.month == 12].index.values, reverse=True)
        year = st.radio('Choose the year of streams for training', available_full_years)
        st.session_state['year'] = year 
        if st.form_submit_button("Configure model") or st.session_state['train_model']:
            processed_scrobbles = df.loc[df['year'] == year].copy()
            st.session_state['processed_scrobbles'] = processed_scrobbles
            st.markdown('**Preview Input Data Before Training**')
            st.dataframe(
                processed_scrobbles[['date', 'song_title', 'album_final', 'primary_artist']].head(10),
                hide_index = True
            )
            st.session_state['model_configured'] = True
            st.session_state['model_ready'] = True
            st.session_state['train_model'] = False

if st.session_state['model_ready']:
    with st.form("start_train_model"):
        if st.form_submit_button('Train your K-Means Clustering Model', type = 'primary', 
                                 icon = ':material/model_training:', on_click = clear_train_button):
             st.session_state['train_model'] = True

        if st.session_state['train_model']:
            session_stats = perform_clustering.run_clustering(st.session_state['processed_scrobbles'],
                                                              st.session_state['n_clusters'])
            st.session_state['model_trained'] = True
            st.session_state['session_stats'] = session_stats
            model_trained = True
            st.success('Listening session clusters successfully found', icon="✅")
            display_cols = ['cluster', 'stream_count', 'song_title_nunique', 'primary_artist_nunique', 
                            'album_nunique', 'session_length', 'weekday', 'season', 
                            'time_of_day_start', 'first_listen_ratio', 'artist_diversity', 
                            'album_diversity','song_diversity', 'session_id']
            min_cluster_counts = st.session_state['session_stats'].cluster.value_counts().min()
            if min_cluster_counts > 2:
                n_samples = 2
            else:
                n_samples = 1
            session_stat_examples = (st.session_state['session_stats']
                                     .groupby('cluster')[display_cols]
                                     .apply(lambda x: x.sample(n=n_samples))
                                     .reset_index(drop = True))
            example_ids = session_stat_examples.session_id 
            st.subheader("Example Listening Sessions")
            st.markdown("Take a look at some some of the features used to cluster your listening sessions.")
            st.dataframe(session_stat_examples[display_cols[:-1]], hide_index = True)

if st.session_state['model_trained']:
    st.subheader("Analyze the Clustering Results")
    st.markdown("Use the menu below and select a feature to analyze your clusters over.")
    features = ['first_listen_ratio', 'artist_diversity', 
                'album_diversity','song_diversity', 'weekday', 'season',
                'stream_count', 'song_title_nunique', 'primary_artist_nunique', 
                'album_nunique', 'session_length', ]
    feat_captions = ['Proportion of streams that was a first listen/new discovery',
                     'Proportion of streams that were of unique artists', 
                     'Proportion of streams that were of unique albums', 
                     'Proportion of streams that were of unique songs', 
                     'Day of the week', 'Season', 'Number of streams', 
                     'Number of unique songs', 'Number of unique artists',
                     'Number of unique albums', 'Length of session (hours)'
                     ]
    selected_feature = st.radio("Choose a feature", options = features, horizontal = True,
             captions = feat_captions)
    hist = clustering.inter_cluster_distributions(selected_feature, st.session_state['session_stats'])
    st.plotly_chart(hist, width = 'stretch')
    session_cluster_aggs = st.session_state['session_stats'].groupby('cluster').agg({
        'stream_count': ['count','median','mean'],
        'primary_artist_nunique': ['median','mean'],
        'album_nunique': ['median','mean'],
        'session_length':['median','mean'],
        'weekday':pd.Series.mode,
        'season':pd.Series.mode,
        'first_listen_ratio':['median','mean'],
        'artist_diversity':['median','mean'],
        'album_diversity':['median','mean'],
        'song_diversity':['median','mean']
    })
    st.dataframe(session_cluster_aggs[[selected_feature]])
    st.subheader('Investigate Your Listening Sessions by Cluster')
    st.markdown("Click through the tabs to look at example listening sessions of each cluster.")
    clusters = sorted(st.session_state['session_stats'].cluster.unique())
    cluster_tab_labels = [f"🔎 Cluster {c+1}" for c in clusters]
    cluster_tabs = st.tabs(cluster_tab_labels)
    cluster = 0
    for tab in cluster_tabs:
        with tab: 
            try:
                utils.cluster_example_tab(cluster, st.session_state['session_stats'],
                                        st.session_state['processed_scrobbles'])
            except:
                pass
        cluster += 1

if st.session_state['model_trained']:
    st.download_button("Download your istening sessions data (.csv)", 
                       st.session_state['session_stats'].to_csv(index = False), 
                       file_name="listening_sessions.csv", 
                       help="This .csv includes all features used to train your ML model \
                       and the cluster predictions that were made for each listening session \
                        identified in your streaming data.", 
                       on_click="ignore", icon=":material/csv:")
    st.divider()
    clear_page = st.button("Train a new clustering model", on_click=clear, icon = ":material/reset_settings:")
    st.divider()
    st.subheader("Check out the other pages:")
    st.page_link("pages/1_📊_Overview.py", label='Overview', icon="📊")
    st.page_link("pages/2_🗓️_Streaming_Calendar.py", label='Streaming Calendar', icon="🗓️")
    st.page_link("pages/3_🎧_Listening_Sessions.py", label='Listening Sessions', icon="🎧")

with st.sidebar:
    st.markdown("""
    Created by [Jacqueline Lee](https://www.linkedin.com/in/jacqueline-kc-lee/)
    
    [🐙 GitHub](https://github.com/jacquelinekclee)
                
    [🤝 LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/)
                
    [📧 Email](mailto:jacquelinekclee@yahoo.com)
    """)