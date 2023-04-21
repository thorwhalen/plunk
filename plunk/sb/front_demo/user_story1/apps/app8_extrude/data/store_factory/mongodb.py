from functools import lru_cache
import ssl
from typing import Mapping
from mongodol import MongoCollectionUniqueDocPersister, MongoClientReader
from mongodol.trans import wrap_kvs
from py2json import Ctor

from platform_poc.config import get_config

MONGODB_ID_FIELD = '_id'


def mk_mongodb_store(*, key_field='key', **kwargs):
    key_field = key_field or MONGODB_ID_FIELD
    if 'iter_projection' not in kwargs:
        kwargs['iter_projection'] = {'_id': False, key_field: True}
    store = MongoStore(**kwargs)
    return wrap_kvs(
        store,
        id_of_key=lambda x: {key_field: x},
        key_of_id=lambda x: x[key_field],
        data_of_obj=_value_input_mapper,
        obj_of_data=_value_output_mapper,
    )


@lru_cache
def get_database():
    conn_str = get_config('MONGODB__CONNECTION_STRING')
    db_name = get_config('MONGODB__DATABASE_NAME')
    client = MongoClientReader(host=conn_str, ssl_cert_reqs=ssl.CERT_NONE)
    return client[db_name].db


@lru_cache
def _get_collection(collection_name: str):
    db = get_database()
    return db[collection_name]


class MongoStore(MongoCollectionUniqueDocPersister):
    def __init__(self, collection_name: str, **kwargs):
        collection = _get_collection(collection_name)
        MongoCollectionUniqueDocPersister.__init__(self, collection, **kwargs)


def _value_input_mapper(v):
    # return dict(value=bytes(v))
    return dict(value=Ctor.deconstruct(v))


def _value_output_mapper(v: Mapping):
    # return Ctor.construct(v['value'].decode('utf-8'))
    return Ctor.construct(v['value'])
