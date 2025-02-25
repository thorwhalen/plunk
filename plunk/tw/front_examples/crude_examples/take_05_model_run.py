"""
Same as take_04_model_run, but where the dispatch is not as manual.
"""
from front.crude import KT, StoreName, Mall
from crude.extrude_crude.extrude_crude_util import mall, np, apply_model

# ---------------------------------------------------------------------------------------
# dispatchable function:
from front.crude import prepare_for_crude_dispatch

f = prepare_for_crude_dispatch(apply_model, param_to_mall_map=mall)
assert all(
    f('fitted_model_1', 'test_fvs') == np.array([[0.0], [1.0], [0.5], [2.25], [-1.5]])
)


def simple_mall_dispatch_core_func(
    key: KT, action: str, store_name: StoreName, mall: Mall
):
    if not store_name:
        # if store_name empty, list the store names (i.e. the mall keys)
        return list(mall)
    else:  # if not, get the store
        store = mall[store_name]

    if action == 'list':
        key = key.strip()  # to handle some invisible whitespace that would screw things
        return list(filter(lambda k: key in k, store))
    elif action == 'get':
        return store[key]


# TODO: the function doesn't see updates made to mall. Fix.
# Just the partial (with mall set), but without mall arg visible (or will be dispatched)
def explore_mall(key: KT, action: str, store_name: StoreName):
    return simple_mall_dispatch_core_func(key, action, store_name, mall=mall)


# Attempt to do this wit i2.wrapper
# from functools import partial
# from i2.wrapper import rm_params_ingress_factory, wrap
#
# without_mall_param = partial(
#     wrap, ingress=partial(rm_params_ingress_factory, params_to_remove="mall")
# )
# mall_exploration_func = without_mall_param(
#     partial(simple_mall_dispatch_core_func, mall=mall)
# )
# mall_exploration_func.__name__ = "explore_mall"

if __name__ == '__main__':
    from crude.util import ignore_import_problems

    with ignore_import_problems:
        from streamlitfront.base import dispatch_funcs
        from functools import partial

        dispatchable_apply_model = prepare_for_crude_dispatch(
            apply_model, output_store='model_results'
        )
        # extra, to get some defaults in:
        dispatchable_apply_model = partial(
            dispatchable_apply_model, fitted_model='fitted_model_1', fvs='test_fvs',
        )
        app = dispatch_funcs([dispatchable_apply_model, explore_mall])
        app()
