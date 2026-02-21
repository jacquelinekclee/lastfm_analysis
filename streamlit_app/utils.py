import streamlit as st
import pandas as pd 
import numpy as np
import sys
import os
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_dir, 'src'))

import src.visualize as visualize  
import models.clustering as clustering 

def render_calendar(df, year, quarter):
    """
    Render a scrobble heatmap with top artist, song, album, and most active day metrics.
    Args:
        df (pandas.DataFrame): processed scrobbles dataframe
        year (int): year to filter the heatmap by
        quarter (int): quarter to filter the heatmap by
    Returns:
        None
    """
    processed_scrobbles_filt, fig = visualize.create_scrobbles_heatmap(df, year, quarter)
    cols = ['primary_artist', 'song_title', 'album_final', 'date']
    counts = {
        col:processed_scrobbles_filt[col].value_counts()
        for col in cols
    }
    top_cols = {
        col:series.idxmax()
        for col, series in counts.items()
    }
    top_date = top_cols['date']
    top_artist = top_cols['primary_artist']
    top_song = top_cols['song_title']
    top_album = top_cols['album_final']
    top_song_artist = processed_scrobbles_filt.loc[processed_scrobbles_filt.song_title == top_song].artist.iloc[0]
    top_album_artist = processed_scrobbles_filt.loc[processed_scrobbles_filt.album_final == top_album].artist.iloc[0]
    st.plotly_chart(fig, width='stretch')
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(
            label="🔥 Most Active Day",
            value=str(pd.to_datetime(top_date).strftime("%-d %B")),
            delta=f"{counts['date'][top_date]} streams",
            delta_color = 'violet',
            delta_arrow = 'off'
        )
        st.metric(
            label="🎤 Most Streamed Artist",
            value=top_artist,
            delta=f"{counts['primary_artist'][top_artist]} streams",
            delta_color = 'violet',
            delta_arrow = 'off'
        )
    with col2:
        st.metric(
            label="🎵 Most Streamed Song",
            value=f'{top_song} by {top_song_artist}',
            delta=f"{counts['song_title'][top_song]} streams",
            delta_color = 'violet',
            delta_arrow = 'off'
        )
        st.metric(
            label="💿 Most Streamed Album",
            value=f'{top_album} by {top_album_artist}',
            delta=f"{counts['album_final'][top_album]} streams",
            delta_color = 'violet',
            delta_arrow = 'off',
            width = 'content'
        )

def create_example_insight(cluster, index, example_labels, 
                           example_session_ids, processed_scrobbles):
    """
    Build an insight dict for a single example session within a cluster.
    Args:
        cluster (int): cluster ID to retrieve the example from
        index (int): index of the example within the cluster
        example_labels (dict): mapping of cluster ID to list of display labels
        example_session_ids (dict): mapping of cluster ID to list of session IDs
        processed_scrobbles (pandas.DataFrame): full scrobble-level dataframe
    Returns:
        dict: dict with keys 'label' (str) and 'insights' (dict from session_insights)
    """
    ex = {}
    ex['label'] = example_labels[cluster][index]
    example_id = example_session_ids[cluster][index]
    ex['insights'] = clustering.session_insights(processed_scrobbles, example_id)
    return ex 

def render_cluster_tab(example_insights, ex_num):
    """
    Render a cluster example tab with session duration, date, counts, and tracklist.
    Args:
        example_insights (dict): output of create_example_insight, with keys 'label' and 'insights'
        ex_num (int): example number displayed in the tab subheader badge
    Returns:
        None
    """
    insights = example_insights['insights']
    st.subheader(f"{example_insights['label']}\
                 :violet-badge[:material/music_history: Example {ex_num}]",
                 divider = 'violet')
    col1, col2, = st.columns([1, 1.5])
    with col1:
        st.metric(
            label="⏱️ Session duration",
            value=f"{insights['duration']}"
        )
        st.metric(
            label=f"📆 {insights['start_date_description']}",
            value=f"{insights['time_description']}"
        )
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        sub_col1.metric(
            label="🎵 # Unique Songs",
            value=f"{insights['song_title']:,}"
        )
        sub_col2.metric(
            label="🎤 # Unique Artists",
            value=f"{insights['primary_artist']:,}"
        )
        sub_col3.metric(
            label="💿 # Unique Albums",
            value=f"{insights['album_final']:,}"
        )
    with col2:
        st.dataframe(
            insights['session_df'].reset_index(drop = True).rename(
                columns = {
                    'artist':'Artist',
                    'album_final': 'Album',
                    'song_title': 'Song Title'
                }
            ),
            hide_index = True
        )
    
def cluster_example_tab(cluster, session_stats, processed_scrobbles):
    session_ids = session_stats.loc[
        (session_stats.stream_count > 1) & 
        (session_stats.cluster == cluster)
    ].session_id.unique()
    choose_session_id = st.button(f"Generate random listening session for Cluster {cluster + 1}")
    if choose_session_id:
        example_id = np.random.choice(session_ids, 1)[0]
        insights = clustering.session_insights(processed_scrobbles, example_id)  
        col1, col2, = st.columns([1, 1.5])
        with col1:
            if insights['duration'][0] != '0':
                st.metric(
                    label="⏱️ Session duration",
                    value=f"{insights['duration']}"
                )
            st.metric(
                label=f"📆 {insights['start_date_description']}",
                value=f"{insights['time_description']}"
            )
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            sub_col1.metric(
                label="🎵 # Unique Songs",
                value=f"{insights['song_title']:,}"
            )
            sub_col2.metric(
                label="🎤 # Unique Artists",
                value=f"{insights['primary_artist']:,}"
            )
            sub_col3.metric(
                label="💿 # Unique Albums",
                value=f"{insights['album_final']:,}"
            )
        with col2:
            st.dataframe(
                insights['session_df'].reset_index(drop = True).rename(
                    columns = {
                        'artist':'Artist',
                        'album_final': 'Album',
                        'song_title': 'Song Title'
                    }
                ),
                hide_index = True
            )
