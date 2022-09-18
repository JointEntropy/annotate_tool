import json
import os


def load_config(config_path: str = None):
    cfg_path = config_path or os.environ.get('CONFIG_PATH') or 'config.json'
    with open(cfg_path) as f:
        config = json.load(f)
    return config
