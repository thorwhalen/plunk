import copyreg
import pickle
import types


import copyreg
import dill


def pickle_function(func):
    return dill._dill.save_function, (func,)


copyreg.pickle(types.FunctionType, pickle_function)

if __name__ == '__main__':
    # copyreg.pickle(type(lambda: None), save_function)
    func = lambda x: x + 1
    func.__name__ = 'ggg'
    func.__qualname__ = 'fff'
    print(func)
    # locals()['__main__']['fff']=func
    d = pickle.dumps(scratch_pickle.func)
