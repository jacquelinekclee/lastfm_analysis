import sys
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

import src.models.clustering as clustering
import src.data.sessions as sessions 

def run_clustering(processed_scrobbles, n_clusters = 4):
    """
    run all scripts necessary to run the clusters 
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of processed scrobbles 
        n_clusters (int, default 4): number of clusters for model to create 
    Returns:
        pandas.DataFrame: dataframe with insights for each listening session
    """
    session_stats = sessions.create_session_stats(processed_scrobbles)
    session_stats_transformed, cluster_predictions = clustering.run_clustering_model(session_stats, n_clusters)
    session_stats['cluster'] = cluster_predictions
    return session_stats

def main(targets):
    """
    run all scripts necessary to run the clusters. this script is intended for 
    command line usage
    Args:
        targets (list): configuration for the training and running the clustering model
    Returns:
        pandas.DataFrame: dataframe with insights for each listening session
    """
    BASE_DIR = Path(__file__).parent  
    CONFIG_DIR = BASE_DIR / 'config'
    OUT_DATA_DIR = BASE_DIR / 'data/processed'
    TEST_OUT_DATA_DIR = BASE_DIR / 'test/processed'

    data_config = json.load(open(Path(CONFIG_DIR / 'data-params.json')))
    
    date = datetime.now()
    date_str = date.strftime("%m_%d")

    if 'test' in targets:
        processed_scrobbles_fp = Path(TEST_OUT_DATA_DIR / data_config['test_processed_scrobbles_fp'])
        session_stats_filename = f'{date_str}_test_session_stats.csv'
        session_stats_fp = Path(TEST_OUT_DATA_DIR / session_stats_filename)
        data_config['test_session_stats_fp'] = session_stats_filename
    else:
        processed_scrobbles_fp = Path(OUT_DATA_DIR / data_config['processed_scrobbles_fp'])
        session_stats_filename = f'{date_str}_session_stats.csv'
        session_stats_fp = Path(OUT_DATA_DIR / session_stats_filename)
        data_config['test_session_stats_fp'] = session_stats_filename
    processed_scrobbles = pd.read_csv(processed_scrobbles_fp)
    if len(targets) == 2:
        n_clusters = int(targets[-1]) 
    else: 
        n_clusters = 4
    session_stats = run_clustering(processed_scrobbles, session_stats_fp, n_clusters)
    session_stats.to_csv(session_stats_fp, index = False)
    with open(str(BASE_DIR) + '/config/data-params.json', 'w') as file:
        file.write(str(data_config).replace("'", '"'))
    return session_stats

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
