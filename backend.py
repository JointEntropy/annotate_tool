from catchblogger_tools.mongo import spawn_mongo_db_conn
from utils import load_config


class Backend:
    def __init__(self, config):
        self.config = config
        self.annotate_collection = spawn_mongo_db_conn(config).get_collection(config['table_name'])

    def get_sample(self):
        return self.annotate_collection.find_one({'label': {"$exists": False}})

    def label_sample(self, sample_id, label):
        self.annotate_collection.update_one({'_id': sample_id} ,
                                            {'$set': {'label': label}}, upsert=True)


if __name__ == '__main__':
    config = load_config()
    backend = Backend(config['mongo'])
    sample = backend.get_sample()
    if sample is not None:
        backend.label_sample(sample['_id'], label=1)
