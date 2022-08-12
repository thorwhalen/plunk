from functools import partial

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from front import Crudifier

mall = dict(
    func=dict(StandardScaler=StandardScaler, KMeans=KMeans, linreg=LinearRegression),
    parametrized_funcs=dict(),
)

crudify = partial(Crudifier, mall=mall)


def str_to_dict(string):
    import json
    return json.loads(string)


def dict_maker(**kwargs):
    return dict(**kwargs)


@crudify('func', output_store='parametrized_funcs')
def factory(func, kwargs='()'):
    kwargs = str_to_dict(kwargs)
    return partial(func, **kwargs)


def foo(x):
    return x + 1


if __name__ == '__main__':
    from streamlitfront import mk_app
    from streamlitfront import dispatch_funcs

    # app = dispatch_funcs([factory])

    import front as f
    import streamlitfront.elements as sf

    config = {
        # f.APP_KEY: {'title': 'apply_func_to_wf'},
        f.RENDERING_KEY: {
            'factory': {
                'execution': {
                    'inputs': {
                        'func': {
                            f.ELEMENT_KEY: sf.SelectBox,
                            'options': list(mall['func'])
                        },
                    },
                }
            },
        }
    }
    app = mk_app([factory], config)
    app()

    import streamlit as st
    st.write(mall)
