from meshed import code_to_dag

# import oa.examples.illustrate_stories as ii

# func_src = {
#     'get_talking_points': ii.topic_points,
#     'make_illustration_description': ii.get_image_description,
#     'make_illustration': ii.get_illustration,
#     'aggregate_story_and_image': ii.aggregate_story_and_image,
# }
#
#
# @code_to_dag(
#     func_src=func_src,
#     name='slide_maker'
# )
@code_to_dag
def dag():
    talking_points = get_talking_points(topic, n_talking_points)
    illustration_description = make_illustration_description(talking_point, image_style)
    img_url = make_illustration(illustration_description, image_style)
    slide = aggregate_story_and_image(img_url, story_text)


funcs = list(dag.find_funcs())

# ------------------------------------------------------------------------------
# Adding persistence


q, f, g, r = funcs

from front.crude import prepare_for_crude_dispatch, Crudifier
from functools import partial


mall = {'illustration_description_store': dict()}
crudifier = partial(Crudifier, mall=mall)


def f(talking_point):
    return f"image of {talking_point}"


def g(illustration_description):
    return illustration_description.upper()


ff = crudifier(
    output_store='illustration_description_store',
)(f)
gg = crudifier(
    param_to_mall_map={'illustration_description': 'illustration_description_store'},
)(g)


# ff = prepare_for_crude_dispatch(
#     f,
#     mall=mall,
#     output_store='illustration_description_store',
# )
# gg = prepare_for_crude_dispatch(
#     g,
#     mall=mall,
#     param_to_mall_map={'illustration_description': 'illustration_description_store'}
# )

# import streamlit as st


def debug(x):
    return mall


funcs = [ff, gg, debug]

# from front.dag import crudify_func_nodes
#
# cdag = crudify_func_nodes(
#     'illustration_description', dag
# )
# funcs = list(cdag.find_funcs())

import i2
# print(*map(lambda x: f"{x.__name__}: {i2.Sig(x)}", funcs), sep='\n')
#
# print('-----------------------------------------------')
# _, f, g, _ = list(cdag.find_funcs())
print(f"{ff.__name__}: {i2.Sig(ff)}")
print(f"{gg.__name__}: {i2.Sig(gg)}")
