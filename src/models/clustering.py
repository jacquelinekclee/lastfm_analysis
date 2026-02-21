import pandas as pd
import numpy as np

import sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from scipy.spatial.distance import cdist

from sklearn.decomposition import PCA

from sklearn.metrics.pairwise import euclidean_distances

import plotly.express as px

def run_clustering_model(session_stats, n_clusters = 4):
    """
    run all scripts necessary to run the clusters 
    Args:
        session_stats (pandas.DataFrame): dataframe with details on each session
        n_clusters (int, default 4): number of clusters for model to create 
    Returns:
        tuple: (pandas.DataFrame with transformed features for the model, numpy.ndarray with cluster label for each session)
    """
    X_transformed, X_transformed_df = prepare_data(session_stats)
    new_cols = {og:og.split('__')[1] for og in X_transformed_df.columns}
    X_transformed_df.rename(columns = new_cols, inplace = True)    
    cluster_predictions = predict_listening_sessions_clusters(X_transformed, n_clusters)
    X_transformed_df['cluster'] = cluster_predictions
    return X_transformed_df, cluster_predictions

def prepare_data(session_stats):
    """
    Preprocess session data by scaling numeric features and one-hot encoding categorical features.
    Args:
        session_stats (pandas.DataFrame): dataframe with raw session-level features
    Returns:
        tuple: (numpy.ndarray of transformed features, pandas.DataFrame of transformed features with column names)
    """
    num_feat_filt = ['session_length','artist_diversity', 'song_diversity', 'first_listen_ratio']
    categ_feat = ['weekday', 'season', 'time_of_day_start']
    X_session_stats = session_stats[num_feat_filt + categ_feat]
    scalar = StandardScaler()
    pl_standardize = Pipeline([
        ('standardize', scalar)
    ])
    pl_ohe = Pipeline([
        ('pos', OneHotEncoder())
    ])
    preproc_filt = ColumnTransformer(
        transformers=[
            ('scaling', pl_standardize, num_feat_filt),
            ('step_name', pl_ohe, categ_feat)
        ]
    )
    X_transformed = preproc_filt.fit_transform(X_session_stats)
    X_transformed_df = pd.DataFrame(X_transformed, columns = preproc_filt.get_feature_names_out())
    return X_transformed, X_transformed_df

def predict_listening_sessions_clusters(X_transformed, n_clusters = 4):
    """
    Fit a KMeans model and return cluster assignments for each session.
    Args:
        X_transformed (numpy.ndarray): preprocessed feature matrix
        n_clusters (int, default 4): number of clusters to generate
    Returns:
        numpy.ndarray: cluster label for each session
    """
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42, n_init='auto')
    y_kmeans = kmeans.fit_predict(X_transformed)
    return y_kmeans

def inter_cluster_distributions(col, session_stats):
    """
    Plot an overlapping percent histogram of a feature across clusters.
    Args:
        col (str): column name to plot
        session_stats (pandas.DataFrame): dataframe of listening session details
    Returns:
        plotly.graph_objects.Figure: histogram figure
    """
    dimension = ' '.join(col.split('_')).title()
    # pastel1
    fig = px.histogram(session_stats, x=col, color="cluster", 
                       barmode="group", histnorm='percent', 
                       color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_layout(
        title_text=f'{dimension} Across Listening Session Clusters', 
        xaxis_title_text=dimension,
        yaxis_title_text='Percent of Sessions', 
    )
    return fig 

def create_readable_time(time):
    """
    Convert a time object to a human-readable 12-hour AM/PM string.
    Args:
        time (datetime.time): time to format
    Returns:
        str: formatted time string (e.g. '9:05 AM')
    """
    hour = time.hour
    minutes = time.minute
    if minutes <= 9:
        minutes = f'0{minutes}'
    if hour < 12:
        return f"{hour}:{minutes} AM"
    elif hour == 12:
        return f"{hour}:{minutes} PM"
    else:
        return f"{hour - 12}:{minutes} PM"

def session_insights(processed_scrobbles, session_id):
    """
    Extract summary statistics and metadata for a single listening session.
    Args:
        processed_scrobbles (pandas.DataFrame): full scrobble-level dataframe with a 'session_id' column
        session_id (int): ID of the session to summarize
    Returns:
        dict: session metrics including unique artist/album/song counts, discoveries, duration,
              time description, date description, and a filtered session dataframe
    """
    session = processed_scrobbles.loc[processed_scrobbles.session_id == session_id].copy()
    session['datetime_local'] = pd.to_datetime(session['datetime_local'])
    listening_session_cols = ['artist', 'album_final', 'song_title']
    total_discoveries = session.first_listen_any.sum()
    agg_cols = ['primary_artist', 'album_final', 'song_title']
    insights_dict = session[agg_cols].nunique().to_dict()
    insights_dict['discoveries'] = total_discoveries
    start_time = pd.to_datetime(session.datetime_local.min())
    start_time_str = create_readable_time(start_time.time())
    end_time =  pd.to_datetime(session.datetime_local.max())
    end_time_str = create_readable_time(end_time.time())
    day_of_week = session.weekday.iloc[0].capitalize()
    start_date = start_time.date()
    start_date_str = start_date.strftime("%B %d")
    end_date = end_time.date()
    duration = end_time - start_time 
    seconds = duration.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        duration = '{} hour{}, {} minute{}'.format(hours, 's' if hours != 1 else '',
                                      minutes, 's' if minutes != 1 else '')
    else: 
        duration = '{} minute{}'.format(minutes, 's' if minutes != 1 else '')
    insights_dict['duration'] = duration
    start_date_description = f"{day_of_week}, {start_date_str}"
    time_description = f"{start_time_str} till "
    if end_date > start_date:
        end_date_str = end_date.strftime("%B %d")
        end_day_of_week = session.weekday.iloc[-1].capitalize()
        time_description += f"{end_day_of_week}, {end_date_str} {end_time_str}"
    else:
        time_description += f"{end_time_str}"
    insights_dict['time_description'] = time_description
    insights_dict['start_date_description'] = start_date_description
    insights_dict['session_df'] = session[listening_session_cols]
    return insights_dict
