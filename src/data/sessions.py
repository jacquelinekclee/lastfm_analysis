import pandas as pd
import numpy as np

def process_sessions(processed_scrobbles):
    """
    add listening session features to processed_scrobbles 
     Args:
        processed_scrobbles (pandas.DataFrame): dataframe of sorted, processed scrobbles 
    Returns:
        pandas.DataFrame: dataframe with added session details 
    """
    sessions, session_rows = create_sessions(processed_scrobbles)
    seconds_to_hours = 3600
    sessions_diffs = {session_id:(v[1] - v[0])/seconds_to_hours 
                      for session_id,v in sessions.items()}
    session_diffs_df = (
        pd.Series(sessions_diffs)
        .to_frame(name = 'session_length')
        .reset_index(drop=False)
        .rename(columns={'index':'session_id'})
    )
    processed_scrobbles['session_id'] = session_rows
    processed_scrobbles = pd.merge(processed_scrobbles, session_diffs_df, on = 'session_id')
    return processed_scrobbles

def create_session_stats(processed_scrobbles):
    """
    calculate aggregates and statistics on each listening session 
    Args:
        scrobbles_df (pandas.DataFrame): dataframe of scrobbles with session details 
    Returns:
        pandas.DataFrame: dataframe with aggregates and stats for each session
    """
    session_stats = processed_scrobbles.groupby('session_id').agg({
        'song_title': ['count', 'nunique'],
        'primary_artist': ['nunique'], 
        'album': ['nunique'],
        'session_length':['first'],
        'weekday':['first'],
        'season':['first'],
        'time_of_day':['first'],
        'first_artist_listen':['sum'],
        'first_song_listen':['sum'],
        'first_album_listen':['sum'],
        'first_listen_any':['sum']
    })
    session_stats.columns = ['_'.join(col) for col in session_stats.columns]
    # higher values = higher diversity
    session_stats['artist_diversity'] = session_stats.primary_artist_nunique / session_stats.song_title_count
    session_stats['album_diversity'] = session_stats.album_nunique / session_stats.song_title_count
    session_stats['song_diversity'] = session_stats.song_title_nunique / session_stats.song_title_count
    session_stats.rename(columns = {
        'session_length_first':'session_length',
        'weekday_first':'weekday',
        'season_first':'season',
        'song_title_count':'stream_count',
        'time_of_day_first':'time_of_day_start',
    }, inplace = True)
    session_stats['first_listen_ratio'] = (session_stats['first_listen_any_sum'] /
                                           session_stats['stream_count'])
    session_stats.reset_index(inplace=True)
    session_stats.fillna(0, inplace=True)
    return session_stats

def create_sessions(processed_scrobbles):
    """
    extract listening sessions from the scrobbles, where a listening session
    is any consecutive streaming where a break is only 10 minutes or less.
    this threshold tries to accommodate longer song lengths. 
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of sorted, processed scrobbles 
    Returns:
        dict: {session id:[start uts, end uts]}
        dict: {row index:session id}
    """
    session_id = 0
    sessions = {} # session id : [starting uts, end uts]
    current_session = [] 
    threshold = 600
    session_rows = {} # row index:session id 
    for i, row in processed_scrobbles.iterrows():
        if len(current_session) == 0: 
            current_session = row
            sessions[session_id] = [row.uts, np.nan]
        else:
            if row.uts - current_session.uts <= threshold:
                sessions[session_id][1] = row.uts
                current_session = row
            else:
                current_session = row
                session_id += 1
                sessions[session_id] = [row.uts, np.nan]
        session_rows[i] = session_id
    return sessions, session_rows 

