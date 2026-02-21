import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import utils
import src.visualize as visualize  
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

BASE_DIR = Path(__file__).parent.parent  
VIZ_DIR = BASE_DIR / 'src'

st.set_page_config(
    page_title="2025 Streaming Calendar",
    page_icon="🗓️",
    layout="wide"
)

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

available_years = sorted(df.year.unique(), reverse=True)
month_counts = df[['year', 'month']].groupby('year').nunique()
available_full_years = sorted(month_counts[month_counts.month == 12].index.values, reverse=True)
if len(available_full_years) > 0:
    year = st.sidebar.selectbox(
        "Select Year",
        options=available_full_years,
        index=0 
    )
else:
    year = st.sidebar.selectbox(
        "Select Year",
        options=available_years,
        index=0 
    )

if uploaded_file:
    st.title(f"🗓️ Your {year} Streaming Heat Map")
    st.markdown(f"Check out this streaming calendar to see your streaming habits over the course of {year}.")
else: 
    st.title(f"🗓️ Streaming Heat Map")
    st.markdown(f"Check out the streaming calendars to see music streaming habits over the course of {year}. \
                Be sure to click through the tabs to view listening activity quarter-over-quarter.")
st.markdown("Hover over each cell to get a summary of your streaming activity for that day. ")    

quarter_labels = [f"{year}"] + [f"Q{q} {year}" for q in range(1, 5)]
full_year, q1, q2, q3, q4 = st.tabs(quarter_labels)

with full_year:
    # yearly calendar
    processed_scrobbles_filt, fig = visualize.create_scrobbles_heatmap(df, year)
    st.plotly_chart(fig, width='stretch')
    first_session_id = processed_scrobbles_filt.session_id.min()
    last_session_id = processed_scrobbles_filt.session_id.max()
    first_session = processed_scrobbles_filt.loc[
        processed_scrobbles_filt.session_id == first_session_id
    ][['artist', 'album_final', 'song_title']].reset_index(drop = True).rename(
        columns = {
            'artist':'Artist',
            'album_final': 'Album',
            'song_title': 'Song Title'
        }
    )
    last_session = processed_scrobbles_filt.loc[
        processed_scrobbles_filt.session_id == last_session_id
    ][['artist', 'album_final', 'song_title']].reset_index(drop = True).rename(
        columns = {
            'artist':'Artist',
            'album_final': 'Album',
            'song_title': 'Song Title'
        }
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'First Listening Session of {year}')
        st.dataframe(first_session, hide_index = True)
    with col2:
        st.subheader(f'Last Listening Session of {year}')
        col2.dataframe(last_session, hide_index = True)

with q1:
    utils.render_calendar(df, year, 1)
with q2:
    utils.render_calendar(df, year, 2)
with q3:
    utils.render_calendar(df, year, 3)
with q4:
    utils.render_calendar(df, year, 4)
st.divider()
st.subheader("Check out the other pages:")
st.page_link("pages/1_📊_Overview.py", label='Overview', icon="📊")
st.page_link("pages/3_🎧_Listening_Sessions.py", label='Listening Sessions', icon="🎧")
st.page_link("pages/4_🧠_Train_Your_ML_Model_-_Listening_Sessions.py", label='Train Your Listening Sessions Model', icon="🧠")

with st.sidebar:
    st.divider()
    st.markdown("""
    Created by [Jacqueline Lee](https://www.linkedin.com/in/jacqueline-kc-lee/)
    
    [🐙 GitHub](https://github.com/jacquelinekclee)
                
    [🤝 LinkedIn](https://www.linkedin.com/in/jacqueline-kc-lee/)
                
    [📧 Email](mailto:jacquelinekclee@yahoo.com)
    """)