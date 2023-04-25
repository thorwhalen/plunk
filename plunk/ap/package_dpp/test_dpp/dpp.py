import pickle
from pathlib import Path
from time import time

pickle_path = Path(__file__).parent / 'helloworld.pkl'


def pickle_dump(obj, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def pickle_load(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def mk_pickle():
    pickle_dump(f'hello world {time()}', pickle_path)


def pickle_print():
    print(pickle_load(pickle_path))


if __name__ == '__main__':
    # mk_pickle()
    pickle_print()
