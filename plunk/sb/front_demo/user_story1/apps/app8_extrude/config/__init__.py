import os
from config2py import ConfigStore, get_config as _get_config


def _get_config_from_file(key: str):
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.ini'
    )
    config_store = ConfigStore(config_file_path)
    try:
        section, sub_key = tuple(key.split('__'))
    except ValueError:
        raise ValueError(
            f"Invalid key: '{key}', must be in the format of 'SECTION__SUB_KEY'"
        )
    section = config_store.get(section.lower())
    if section:
        return section.get(sub_key.lower())


def get_config(key: str):
    return _get_config(key, sources=[os.environ, _get_config_from_file])
