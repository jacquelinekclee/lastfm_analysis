import pandas as pd
import numpy as np
import pytz

def process_temporal(processed_scrobbles, timezone = 'America/Los_Angeles'):
    """
    add time related columns to scrobbles dataframe 
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of processed scrobbles 
    Returns:
        pandas.DataFrame: dataframe with added temporal features
    """
    processed_scrobbles = add_temporal_features(processed_scrobbles, timezone)
    processed_scrobbles.sort_values('uts', inplace=True)
    processed_scrobbles = add_first_listen_flags(processed_scrobbles)
    return processed_scrobbles

def add_temporal_features(processed_scrobbles, timezone = 'America/Los_Angeles'):
    """
    add columns for time of day, year, month, season, and day of week 
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of processed scrobbles 
    Returns:
        pandas.DataFrame: dataframe with added temporal features
    """
    # Assume your primary timezone
    curr_timezone = pytz.timezone(timezone) 
    dates = pd.to_datetime(processed_scrobbles.utc_time, utc = True)
    processed_scrobbles['time_of_day'] = dates.dt.time
    processed_scrobbles['year'] = dates.dt.year
    processed_scrobbles['month'] = dates.dt.month
    # add season column
    seasons = {
        1:'winter', 2:'winter', 3:'spring', 4:'spring', 5:'spring',
        6:'summer', 7:'summer', 8:'summer', 9:'fall', 10:'fall',
        11:'fall', 12:'winter'
    }
    processed_scrobbles['season'] = processed_scrobbles['month'].map(seasons)
    processed_scrobbles['day'] = dates.dt.day
    # add weekday column
    weekdays = {0:'monday', 1:'tuesday', 2:'wednesday', 
        3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'
    }
    processed_scrobbles['weekday'] = dates.dt.dayofweek.map(weekdays)
    processed_scrobbles['date'] = dates.dt.date
    processed_scrobbles['datetime'] = dates
    processed_scrobbles['datetime_local'] = dates.dt.tz_convert(curr_timezone)
    processed_scrobbles['hour'] = processed_scrobbles['datetime_local'].dt.hour
    processed_scrobbles['time_of_day'] = pd.cut(
        processed_scrobbles['hour'],
        bins=[0, 5, 12, 17, 21, 24],
        labels=['late night', 'morning', 'afternoon', 'evening', 'night'],
        include_lowest=True
    ).astype(str)
    return processed_scrobbles

def add_first_listen_flags(processed_scrobbles):
    """
    designate whether stream was a first listen of that artist, song, and/or album
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of sorted, processed scrobbles 
    Returns:
        pandas.DataFrame: dataframe with added first listen flags 
    """
    # For artists
    processed_scrobbles['first_artist_listen'] = ~processed_scrobbles['primary_artist'].duplicated(keep='first')
    
    # For songs (combine artist + song to handle duplicates)
    processed_scrobbles['song_key'] = processed_scrobbles['primary_artist'] + ' - ' + processed_scrobbles['song_title']
    processed_scrobbles['first_song_listen'] = ~processed_scrobbles['song_key'].duplicated(keep='first')
    processed_scrobbles.drop('song_key', axis=1, inplace=True)
    
    # For albums (combine artist + album)
    processed_scrobbles['album_key'] = processed_scrobbles['primary_artist'] + ' - ' + processed_scrobbles['album_final']
    processed_scrobbles['first_album_listen'] = ~processed_scrobbles['album_key'].duplicated(keep='first')
    processed_scrobbles.drop('album_key', axis=1, inplace=True)

    processed_scrobbles['first_listen_any'] = (processed_scrobbles.first_artist_listen | 
                                               processed_scrobbles.first_album_listen | 
                                               processed_scrobbles.first_song_listen)
    
    return processed_scrobbles
