import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import json 

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Overview | last.fm Analysis",
    page_icon="🎵",
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

# ============================================================
# SIDEBAR - YEAR SELECTOR
# ============================================================

available_years = sorted(df.year.unique(), reverse=True)
selected_year = st.sidebar.selectbox(
    "Select Year",
    options=available_years,
    index=0 
)

# Filter data for selected year
df_year = df[df['datetime'].dt.year == selected_year].copy()

# ============================================================
# HEADER
# ============================================================

if uploaded_file:
    st.title(f"🎵 Your {selected_year} in Music")
    st.markdown("A high-level overview of your listening habits.")    
else: 
    st.title(f"🎵 Your {selected_year} in Music")
    st.markdown("A high-level overview of your listening habits.")    
st.divider()

# ============================================================
# SECTION 1: KEY METRICS
# ============================================================

st.subheader("At a Glance")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label="Total Streams",
    value=f"{len(df_year):,}"
)

col2.metric(
    label="Unique Artists",
    value=f"{df_year['primary_artist'].nunique():,}"
)

col3.metric(
    label="Unique Albums",
    value=f"{df_year['album'].nunique():,}"
)

col4.metric(
    label="Unique Songs",
    value=f"{df_year['song_title'].nunique():,}"
)

col5.metric(
    label="New Artists Discovered",
    value=f"{df_year['first_artist_listen'].sum():,}"
    # TODO: Ensure first_artist_listen flag is calculated across full history
    # not just within the selected year
)

st.divider()

# ============================================================
# SECTION 2: TOP 10 CHARTS
# ============================================================

st.subheader("Your Top 10s")

N = 10  # Number of top items to display

tab_artists, tab_albums, tab_songs = st.tabs(["🎤 Artists", "💿 Albums", "🎵 Songs"])

# --- Top Artists ---
with tab_artists:
    top_artists = (
        df_year.groupby('primary_artist')
        .agg(streams=('uts', 'count'))
        .sort_values('streams', ascending=False)
        .head(N)
        .reset_index()
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(
            top_artists.rename(columns={'primary_artist': 'Artist', 'streams': 'Streams'}),
            hide_index=True,
            width='stretch'
        )

    with col2:
        fig = px.bar(
            top_artists,
            x='streams',
            y='primary_artist',
            orientation='h',
            labels={'streams': 'Streams', 'primary_artist': 'Artist'},
            title=f'Top {N} Most Streamed Artists ({selected_year})',
            color='streams',
            color_continuous_scale='purpor'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, width='stretch')

# --- Top Albums ---
with tab_albums:
    top_albums = (
        df_year.groupby(['album_final', 'primary_artist'])
        .agg(streams=('uts', 'count'))
        .sort_values('streams', ascending=False)
        .head(N)
        .reset_index()
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(
            top_albums.rename(columns={
                'album_final': 'Album',
                'primary_artist': 'Artist',
                'streams': 'Streams'
            }),
            hide_index=True,
            width='stretch'
        )

    with col2:
        top_albums['label'] = top_albums['album_final'] + ' - ' + top_albums['primary_artist']
        fig = px.bar(
            top_albums,
            x='streams',
            y='label',
            orientation='h',
            labels={'streams': 'Streams', 'label': 'Album'},
            title=f'Top {N} Most Streamed Albums ({selected_year})',
            color='streams',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, width='stretch')

# --- Top Songs ---
with tab_songs:
    top_songs = (
        df_year.groupby(['song_title', 'primary_artist'])
        .agg(streams=('uts', 'count'))
        .sort_values('streams', ascending=False)
        .head(N)
        .reset_index()
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(
            top_songs.rename(columns={
                'song_title': 'Song',
                'primary_artist': 'Artist',
                'streams': 'Streams'
            }),
            hide_index=True,
            width='stretch'
        )

    with col2:
        top_songs['label'] = top_songs['song_title'] + ' - ' + top_songs['primary_artist']
        fig = px.bar(
            top_songs,
            x='streams',
            y='label',
            orientation='h',
            labels={'streams': 'Streams', 'label': 'Song'},
            title=f'Top {N} Most Streamed Songs ({selected_year})',
            color='streams',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, width='stretch')

st.divider()

# ============================================================
# SECTION 3: LISTENING BEHAVIOR INSIGHTS
# ============================================================

st.subheader("Listening Behavior")

col1, col2 = st.columns(2)

# --- Streams by Day of Week ---
with col1:
    dow_counts = (
        df_year.groupby('weekday')
        .agg(streams=('song_title', 'count'))
        .reset_index()
    )

    # e.g. 'Monday', 'Tuesday', etc. in preprocessing
    day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    dow_counts['day_of_week'] = pd.Categorical(dow_counts['weekday'], categories=day_order, ordered=True)
    dow_counts = dow_counts.sort_values('day_of_week')

    fig = px.bar(
        dow_counts,
        x='day_of_week',
        y='streams',
        labels={'day_of_week': 'Day of Week', 'streams': 'Streams'},
        title='Streams by Day of Week',
        color='streams',
        color_continuous_scale='Greens'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

# --- Streams by Time of Day ---
with col2:
    tod_counts = (
        df_year.groupby('time_of_day')
        .agg(streams=('song_title', 'count'))
        .reset_index()
    )

    # TODO: Ensure time_of_day is stored as ordered categorical in preprocessing
    tod_order = ['morning', 'afternoon', 'evening', 'night', 'late  night']
    tod_counts['time_of_day'] = pd.Categorical(tod_counts['time_of_day'], categories=tod_order, ordered=True)
    tod_counts = tod_counts.sort_values('time_of_day')

    fig = px.bar(
        tod_counts,
        x='time_of_day',
        y='streams',
        labels={'time_of_day': 'Time of Day', 'streams': 'Streams'},
        title='Streams by Time of Day',
        color='streams',
        color_continuous_scale='Blues'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

st.divider()

# ============================================================
# SECTION 4: DISCOVERY INSIGHTS
# ============================================================

st.subheader("Discovery Highlights")

col1, col2 = st.columns(2)

# --- New Artist Discoveries by Month ---
with col1:
    new_artists = df_year[df_year['first_artist_listen'] == True].copy()
    new_artists['month'] = new_artists['datetime'].dt.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    monthly_discoveries = (
        new_artists.groupby('month')
        .agg(new_artists=('primary_artist', 'count'))
        .reset_index()
    )
    monthly_discoveries['month'] = pd.Categorical(
        monthly_discoveries['month'],
        categories=month_order,
        ordered=True
    )
    monthly_discoveries = monthly_discoveries.sort_values('month')

    fig = px.bar(
        monthly_discoveries,
        x='month',
        y='new_artists',
        labels={'month': 'Month', 'new_artists': 'New Artists'},
        title='New Artist Discoveries by Month',
        color='new_artists',
        color_continuous_scale='Purples'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

# --- Top Discovered Artists ---
with col2:
    new_artists_streams = df_year.loc[df_year.primary_artist.isin(new_artists.primary_artist.unique())]
    top_discovered = (
        new_artists_streams.groupby('primary_artist')
        .agg(streams=('song_title', 'count'))
        .sort_values('streams', ascending=False)
        .head(10)
        .reset_index()
    )

    st.markdown(f"**Top Newly Discovered Artists in {selected_year}**")
    st.markdown(f"*Artists you listened to for the first time in {selected_year}, ranked by total streams.*")
    st.dataframe(
        top_discovered.rename(columns={
            'primary_artist': 'Artist',
            'streams': f'Streams in {selected_year}'
        }),
        hide_index=True,
        width='stretch'
    )

st.divider()

col1, col2 = st.columns(2)

# --- New Album Discoveries by Month ---
with col1:
    new_albums = df_year[df_year['first_album_listen'] == True].copy()
    new_albums['month'] = new_albums['datetime'].dt.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    monthly_discoveries = (
        new_albums.groupby('month')
        .agg(new_albums=('album_final', 'count'))
        .reset_index()
    )
    monthly_discoveries['month'] = pd.Categorical(
        monthly_discoveries['month'],
        categories=month_order,
        ordered=True
    )
    monthly_discoveries = monthly_discoveries.sort_values('month')

    fig = px.bar(
        monthly_discoveries,
        x='month',
        y='new_albums',
        labels={'month': 'Month', 'new_albums': 'New Albums'},
        title='New Album Discoveries by Month',
        color='new_albums',
        color_continuous_scale='Purples'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

# --- Top Discovered Albums ---
with col2:
    new_albums_streams = df_year.loc[df_year.album_final.isin(new_albums.album_final.unique())]
    top_discovered = (
        new_albums_streams.groupby('album_final')
        .agg(streams=('song_title', 'count'))
        .sort_values('streams', ascending=False)
        .head(10)
        .reset_index()
    )

    st.markdown(f"**Top Newly Discovered Albums in {selected_year}**")
    st.markdown(f"*Albums you listened to for the first time in {selected_year}, ranked by total streams.*")
    st.dataframe(
        top_discovered.rename(columns={
            'album_final': 'Album',
            'streams': f'Streams in {selected_year}'
        }),
        hide_index=True,
        width='stretch'
    )

st.divider()

# ============================================================
# SECTION 5: YEAR-OVER-YEAR COMPARISON (if multiple years exist)
# ============================================================

if len(available_years) > 1:
    st.subheader("Year-over-Year Comparison")

    # Compare key metrics across years
    yoy_stats = (
        df.groupby(df['datetime'].dt.year)
        .agg(
            total_streams=('song_title', 'count'),
            unique_artists=('primary_artist', 'nunique'),
            unique_albums=('album_final', 'nunique'),
            unique_songs=('song_title', 'nunique')
        )
        .reset_index()
        .rename(columns={'datetime': 'year'})
    )

    # Metric selector
    yoy_metric = st.selectbox(
        "Compare metric across years:",
        options={
            'total_streams': 'Total Streams',
            'unique_artists': 'Unique Artists',
            'unique_albums': 'Unique Albums',
            'unique_songs': 'Unique Songs'
        }.keys(),
        format_func=lambda x: {
            'total_streams': 'Total Streams',
            'unique_artists': 'Unique Artists',
            'unique_albums': 'Unique Albums',
            'unique_songs': 'Unique Songs'
        }[x]
    )

    fig = px.bar(
        yoy_stats,
        x='year',
        y=yoy_metric,
        labels={'year': 'Year', yoy_metric: yoy_metric.replace('_', ' ').title()},
        title=f'{yoy_metric.replace("_", " ").title()} by Year',
        color='year',
        color_continuous_scale='purpor'
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')

    st.divider()


st.subheader("Check out the other pages:")
st.page_link("pages/2_🗓️_Streaming_Calendar.py", label='Streaming Calendar', icon="🗓️")
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