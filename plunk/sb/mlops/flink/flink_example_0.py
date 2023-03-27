import json
import logging
import sys

from pyflink.datastream import StreamExecutionEnvironment
from more_itertools import windowed
from functools import partial

DFLT_CHK_SIZE = 3


def process_json_data():
    env = StreamExecutionEnvironment.get_execution_environment()

    # define the source
    ds = env.from_collection(
        collection=[
            (0, '{"deviceId": "00000781O", "flux": [1,2,3,4,5,6]}'),
            (1, '{"deviceId": "00000700O", "flux": [7,8,9,10,11,12]}'),
            (2, '{"deviceId": "00000781O", "flux": [8,8,8,10,10,10]}'),
        ]
    )

    def chunker(data):
        # parse the json
        json_data = json.loads(data[1])
        chks = list(windowed(json_data["flux"], DFLT_CHK_SIZE))
        return (data[0], {"chks": chks})

    def filter_by_index(data):

        return data[0] % 2 == 0

    ds.map(chunker).filter(filter_by_index).print()

    # submit for execution
    env.execute()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    process_json_data()
