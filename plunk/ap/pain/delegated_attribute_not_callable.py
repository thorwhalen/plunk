from dol import Files, wrap_kvs


def returnx(x):
    return x


@wrap_kvs(data_of_obj=returnx, obj_of_data=returnx)
class MyFiles(Files):
    @classmethod
    def hello(cls):
        print('hello')

    @staticmethod
    def hi():
        print('hi')


try:
    MyFiles.hello()
except Exception as e:
    print('classmethod hello is broken by wrap_kvs decorator')
    print(f'{type(e).__name__}: {e}')


try:
    MyFiles.hi()
except Exception as e:
    print('staticmethod hi is broken by wrap_kvs decorator')
    print(f'{type(e).__name__}: {e}')

try:
    MyFiles(rootdir='.').hello()
except Exception as e:
    print('classmethod hello is broken by wrap_kvs decorator')
    print(f'{type(e).__name__}: {e}')


try:
    MyFiles(rootdir='.').hi()
except Exception as e:
    print('staticmethod hi is broken by wrap_kvs decorator')
    print(f'{type(e).__name__}: {e}')
