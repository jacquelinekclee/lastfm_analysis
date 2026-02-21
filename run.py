import sys
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

import perform_clustering as clustering
import process_data as process 

def main(targets):
    """
    run all scripts to process raw scrobbles data and train and make predictions
    with listening sessions clustering model via command line
    Args:
        targets (list): configuration
    Returns:
        list: list of filepaths for output
    """
    BASE_DIR = Path(__file__).parent  
    CONFIG_DIR = BASE_DIR / 'config'
    DATA_DIR = BASE_DIR / 'data/raw'
    OUT_DATA_DIR = BASE_DIR / 'data/processed'
    TEST_DATA_DIR = BASE_DIR / 'test/testdata'
    TEST_OUT_DATA_DIR = BASE_DIR / 'test/processed'

    data_config = json.load(open(Path(CONFIG_DIR / 'data-params.json')))
    
    date = datetime.now()
    date_str = date.strftime("%m_%d")

    if 'test' in targets:
        scrobbles_fp = Path(TEST_DATA_DIR / data_config['test_scrobbles_fp'])
        processed_scrobbles_filename = f'{date_str}_test_processed_scrobbles.csv'
        processed_scrobbles_fp = Path(TEST_OUT_DATA_DIR / processed_scrobbles_filename)
        data_config['test_processed_scrobbles_fp'] = processed_scrobbles_filename
        session_stats_filename = f'{date_str}_test_session_stats.csv'
        session_stats_fp = Path(TEST_OUT_DATA_DIR / session_stats_filename)
        data_config['test_session_stats_fp'] = session_stats_filename
    else:
        scrobbles_fp = Path(DATA_DIR / data_config['scrobbles_fp'])
        processed_scrobbles_filename = f'{date_str}_test_processed_scrobbles.csv'
        processed_scrobbles_fp = Path(OUT_DATA_DIR / processed_scrobbles_filename)
        data_config['processed_scrobbles_fp'] = processed_scrobbles_filename
        session_stats_filename = f'{date_str}_session_stats.csv'
        session_stats_fp = Path(OUT_DATA_DIR / session_stats_filename)
        data_config['test_session_stats_fp'] = session_stats_filename
    processed_scrobbles = process.process_scrobbles(scrobbles_fp)
    processed_scrobbles.to_csv(processed_scrobbles_fp, index = False)
    if len(targets) == 2:
        n_clusters = int(targets[-1]) 
    else: 
        n_clusters = 4
    session_stats = clustering.run_clustering(processed_scrobbles, session_stats_fp, n_clusters = n_clusters)
    with open(str(BASE_DIR) + '/config/data-params.json', 'w') as file:
        file.write(str(data_config).replace("'", '"'))
    return processed_scrobbles_filename, session_stats_filename

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
