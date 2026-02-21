import pandas as pd
import re
import numpy as np
import pathlib

def preprocess_scrobbles_df(scrobbles):
    """
    preprocess scrobbles to standardize album names for tracks
    and create new columns for primary artist and any featured artists
    Args:
        scrobbles (str or pandasDataFrame): raw scrobbles 
    Returns:
        pandas.DataFrame: dataframe of scrobbles with 
        standardized album column ('album_final'),
        column for track's primary artist ('primary_artist'),
        and column for any featured artists of track ('featured_artists')
    """
    assert type(scrobbles) == str or \
        isinstance(scrobbles, pd.DataFrame) or \
        isinstance(scrobbles, pathlib._local.PosixPath)
    if type(scrobbles) == pd.DataFrame:
        scrobbles_df = scrobbles.copy()
    else:
        scrobbles_df = pd.read_csv(scrobbles)
    columns = ['uts', 'utc_time', 'artist', 'album', 'track']
    df_cols = scrobbles_df.columns.values 
    check_cols = [col in df_cols for col in columns]
    if not all(check_cols):
        return f'column names do not match.\nexpected column names: {columns}.loaded column names: {df_cols}'
    # replace nan albums with track name
    scrobbles_df['album'] = scrobbles_df['album'].fillna(scrobbles_df['track'])

    scrobbles_df['album'] = scrobbles_df['album'].fillna('track')
    # create cols for unsorted and sorted tups for artists
    scrobbles_df['artist_list'] = scrobbles_df.artist.str.split(', ')
    scrobbles_df['artist_sorted'] = scrobbles_df.artist_list.apply(sorted).apply(tuple)
    # get scrobbles df with final album col
    processed_scrobbles = process_albums(scrobbles_df)
    # process artists col
    processed_scrobbles['featured_artists'] =  (
        np.select(
            condlist=[
            processed_scrobbles.artist_list.str.len() == 1, 
            processed_scrobbles.artist_list.str.len() == 2, 
            processed_scrobbles.artist_list.str.len() > 2
            ],
            choicelist=[
            '', # empty string for songs with no featured artists
            processed_scrobbles.artist_list.str[1],
            processed_scrobbles.artist_list.str[1:]
            ],
            default=processed_scrobbles.artist_list
            )
        )
    processed_scrobbles['primary_artist'] = processed_scrobbles.artist_list.str[0]    
    processed_scrobbles.rename(columns = {'track':'song_title'}, inplace=True)
    return processed_scrobbles

def process_albums(scrobbles_df):
    """
    create standardized albums column for each track 
    Args:
        scrobbles_df (pandas.DataFrame): df of scrobbles with
        nan album names filled and column for sorted artists
    Returns:
        pandas.DataFrame: dataframe of scrobbles with 
        standardized album column ('album_final')
    """
    scrobbles_unique_tracks = scrobbles_df[['artist_sorted', 'track']].drop_duplicates().copy(deep = True)
    scrobbles_unique_tracks_and_albums = scrobbles_df[['artist_sorted', 'track', 'album']].drop_duplicates().copy(deep = True)
    # only keep unique tracks for album processing
    merged_tracks = pd.merge(scrobbles_unique_tracks, 
        scrobbles_unique_tracks_and_albums, 
        on = ['artist_sorted', 'track'], 
        how='left'
    )
    # get all unique album names for each track 
    tracks_with_unique_albums = merged_tracks.groupby(by = ['artist_sorted','track'])\
    ['album'].unique().reset_index().rename(columns = {'album':'unique_albums'})                                                                     
    # get final album name 
    tracks_with_unique_albums['album_final'] = tracks_with_unique_albums.apply(lambda row:
        choose_final_album_name(row, scrobbles_df), axis = 1
    )
    scrobbles_df_album_final = pd.merge(scrobbles_df, 
        tracks_with_unique_albums, 
        on = ['artist_sorted', 'track'], 
        how = 'left'
    )
    return scrobbles_df_album_final    

def catch_special_editions(album_name):
    """
    detects whether album name contains common words associated with
    special editions of albums
    Args:
        album_name (str): name of track's album
    Returns:
        bool: whether album name likely refers to a special edition. True if
        album does not. False if it does. 
    """
    name_cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', album_name.lower())
    return not (('deluxe' in name_cleaned) or ('edition' in name_cleaned)\
    or ('expanded' in name_cleaned)\
    or ('anniversary' in name_cleaned)) 

def find_most_popular_album(row, albums_filt, scrobbles_df):
    """
    find album name most scrobbled for a given track 
    Args:
        row (pandas.Series): single track (scrobble)
        albums_filt (list[str]): list of filtered album names 
        scrobbles_df (pandas.DataFrame): original dataframe of scrobbles
    Returns:
        str: most popular album name for a given track 
    """
    # finally choose most popular 
    all_scrobbles = scrobbles_df.loc[(scrobbles_df.artist_sorted == \
        row.artist_sorted) & (scrobbles_df.track == row.track)].copy()
    # remove parenthetical text
    # all_scrobbles['album_filtered'] = all_scrobbles.album.str.replace(r' ?[\(\[][^\)\]]*[\)\]]', '', regex=True)
    album_counts = all_scrobbles.album.value_counts()
    # only look at cleaned album names
    album_counts_filtered = album_counts.filter(albums_filt, axis=0)
    if len(album_counts_filtered) == 0:
        return album_counts.idxmax()
    else:
        return album_counts_filtered.idxmax()

def choose_final_album_name(row, scrobbles_df):
    """
    determines final album name for a given track by removing album names
    that match the track name and special edition albums. if needed, then
    the most popular album name is chosen for the track
    Args:
        row (pandas.Series): single track (scrobble)
        scrobbles_df (pandas.DataFrame): original dataframe of scrobbles
    Returns:
        str: most popular album name for a given track 
    """
    album_arr = row.unique_albums.copy()
    # return album name if only 1 unique one exists 
    if len(album_arr) == 1:
        return album_arr[0]
    else:
        alphanum_pattern = r'[^a-zA-Z0-9 ]'
        track_cleaned = re.sub(alphanum_pattern, '', row.track.lower())
        # remove single names
        albums_filt_no_singles = list(filter(lambda album: 
            re.sub(alphanum_pattern, '', album.lower()) != track_cleaned, 
            album_arr
        ))
        if len(albums_filt_no_singles) == 1:
            return albums_filt_no_singles[0]
        elif len(albums_filt_no_singles) == 0:
            return find_most_popular_album(row)
        else:
            # prioritize non special edition albums 
            albums_filt_no_spec_eds = list(filter(
                catch_special_editions, albums_filt_no_singles
            ))
            if len(albums_filt_no_spec_eds) == 1:
                return albums_filt_no_spec_eds[0]
            else:
                if len(albums_filt_no_spec_eds) == 0:
                    albums_filt_penult = albums_filt_no_singles
                else:
                    albums_filt_penult = albums_filt_no_spec_eds
                # remove parenthetical text 
                pattern = r' ?[\(\[][^\)\]]*[\)\]]'
                albums_filt_no_paren = list(map(lambda album: re.sub(pattern, '', album), 
                    albums_filt_penult
                ))
                final_albums_filt = tuple(set(albums_filt_no_paren))
                if len(final_albums_filt) == 1:
                    return final_albums_filt[0]
                elif len(final_albums_filt) == 0:
                    return find_most_popular_album(row, albums_filt_penult, scrobbles_df)
                else:
                    # finally choose most popular 
                    return find_most_popular_album(row, final_albums_filt, scrobbles_df)
                