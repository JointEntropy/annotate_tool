import pandas as pd
import datetime
from pymongo import UpdateOne
import hashlib
from typing import Dict
from utils import load_config
from backend import Backend
from tqdm.auto import tqdm
import os
import glob



def get_id(descr: str) -> str:
    source = descr.encode()
    md5 = hashlib.md5(source).hexdigest()
    return md5


def upload_label_dataset(input_df: pd.DataFrame, final_collection) -> None:
    def prepare_insert_statement(row: pd.Series):
        update_dict = row.to_dict()
        update_dict['update_ts'] = int(datetime.datetime.utcnow().timestamp())
        filter_key = dict(_id=get_id(row['text']))
        update_rule = {'$set': update_dict, '$setOnInsert': {'insert_ts': int(datetime.datetime.utcnow().timestamp())}}
        return UpdateOne(filter_key, update_rule, upsert=True)

    operations = []
    for i, row in tqdm(input_df.iterrows(), total=input_df.shape[0]):
        operations.append(prepare_insert_statement(row))
    final_collection.bulk_write(operations)


if __name__ == '__main__':
    DATA_PATH = '../find_leads_yt/data/scoring_by_model'

    config = load_config()
    backend = Backend(config['mongo'])

    for fp in glob.glob(os.path.join(DATA_PATH, '*')):
        input_df = pd.read_parquet(fp).rename(columns={'description': 'text'})
        mask = (input_df.proba>0.4) & (input_df.proba<0.6)
        input_df = input_df[mask]
        upload_label_dataset(input_df, backend.annotate_collection)
