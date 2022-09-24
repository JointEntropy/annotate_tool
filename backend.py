from catchblogger_tools.mongo import spawn_mongo_db_conn
from utils import load_config
import random


class Backend:
    def __init__(self, config):
        self.config = config
        self.annotate_collection = spawn_mongo_db_conn(config).get_collection(config['table_name'])

    def get_sample(self):
        items_iter = self.annotate_collection.find({'label': {"$exists": False}}).limit(20)
        items_lst = list(items_iter)
        return random.choice(items_lst)

    def label_sample(self, sample_id, label):
        self.annotate_collection.update_one({'_id': sample_id} ,
                                            {'$set': {'label': label}}, upsert=True)


if __name__ == '__main__':
    config = load_config()
    backend = Backend(config['mongo'])
    sample = backend.get_sample()
    if sample is not None:
        backend.label_sample(sample['_id'], label=1)
