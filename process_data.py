import sys
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

import src.data.preprocess as preprocess
import src.data.temporal as temporal
import src.data.sessions as sessions 

def process_scrobbles(scrobbles):
    """
    run all scripts to process raw scrobbles data
    Args:
        processed_scrobbles (pandas.DataFrame): dataframe of raw scrobbles 
    Returns:
        pandas.DataFrame: dataframe with completely processed scrobbles and
            additional features 
    """
    processed_scrobbles = preprocess.preprocess_scrobbles_df(scrobbles)
    processed_scrobbles = temporal.process_temporal(processed_scrobbles)
    processed_scrobbles = sessions.process_sessions(processed_scrobbles)
    return processed_scrobbles

def main(targets):
    """
    run all scripts to process raw scrobbles data via command line
    Args:
        targets (list): configuration for processing the raw data 
    Returns:
        pandas.DataFrame: dataframe with processed streams
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
    else:
        scrobbles_fp = Path(DATA_DIR / data_config['scrobbles_fp'])
        processed_scrobbles_filename = f'{date_str}_test_processed_scrobbles.csv'
        processed_scrobbles_fp = Path(OUT_DATA_DIR / processed_scrobbles_filename)
        data_config['processed_scrobbles_fp'] = processed_scrobbles_filename
    processed_scrobbles = preprocess.preprocess_scrobbles_df(scrobbles_fp)
    processed_scrobbles = temporal.process_temporal(processed_scrobbles)
    processed_scrobbles = sessions.process_sessions(processed_scrobbles)
    processed_scrobbles.to_csv(processed_scrobbles_fp, index = False)
    with open(str(BASE_DIR) + '/config/data-params.json', 'w') as file:
        file.write(str(data_config).replace("'", '"'))
    return processed_scrobbles

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
