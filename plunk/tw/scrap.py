
from meshed import code_to_dag

import oa.examples.illustrate_stories as ii  # https://pypi.org/project/oa/

func_src = {
    'get_talking_points': ii.topic_points,
    'make_illustration_description': ii.get_image_description,
    'make_illustration': ii.get_illustration,
    'aggregate_story_and_image': ii.aggregate_story_and_image,
}

@code_to_dag(func_src=func_src)
def dag():
    talking_points = get_talking_points(topic, n_talking_points)
    illustration_description = make_illustration_description(talking_point, image_style)
    img_url = make_illustration(illustration_description, image_style)
    slide = aggregate_story_and_image(img_url, story_text)


import oa.examples.illustrate_stories as ii  # https://pypi.org/project/oa/

get_talking_points = ii.topic_points
make_illustration_description = ii.get_image_description
make_illustration = ii.get_illustration
aggregate_story_and_image = ii.aggregate_story_and_image

@code_to_dag(func_src=locals(), name='slide_maker')
def dag():
    talking_points = get_talking_points(topic, n_talking_points)
    illustration_description = make_illustration_description(talking_point, image_style)
    img_url = make_illustration(illustration_description, image_style)
    slide = aggregate_story_and_image(img_url, story_text)


funcs = list(dag.find_funcs())

# # ------------------------------------------------------------------------------
# # Adding persistence
#
#
# q, f, g, r = funcs
#
# from front.crude import prepare_for_crude_dispatch, Crudifier
# from functools import partial
#
#
# mall = {'illustration_description_store': dict()}
# crudifier = partial(Crudifier, mall=mall)
#
#
# def f(talking_point):
#     return f"image of {talking_point}"
#
#
# def g(illustration_description):
#     return illustration_description.upper()
#
#
# ff = crudifier(
#     output_store='illustration_description_store',
# )(f)
# gg = crudifier(
#     param_to_mall_map={'illustration_description': 'illustration_description_store'},
# )(g)


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

#
# def debug(x):
#     return mall
#
#
# funcs = [ff, gg, debug]
#
# # from front.dag import crudify_func_nodes
# #
# # cdag = crudify_func_nodes(
# #     'illustration_description', dag
# # )
# # funcs = list(cdag.find_funcs())
#
# import i2
# # print(*map(lambda x: f"{x.__name__}: {i2.Sig(x)}", funcs), sep='\n')
# #
# # print('-----------------------------------------------')
# # _, f, g, _ = list(cdag.find_funcs())
# print(f"{ff.__name__}: {i2.Sig(ff)}")
# print(f"{gg.__name__}: {i2.Sig(gg)}")



import streamlitfront.tools as t

config = {}

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from streamlitfront.elements import SelectBox

config = {APP_KEY: {'title': 'Illustrating concepts'}}

render_image_url = t.Pipe(
    t.html_img_wrap, t.render_html,
)
render_bullet = t.Pipe(
    t.lines_to_html_paragraphs, t.text_to_html, t.render_html,
)

from front import APP_KEY
from streamlitfront.tools import trans_output, dynamic_trans

# THIS WORKS:
config = {APP_KEY: {'title': 'Illustrating concepts'}}
trans_output(config, 'topic_points', render_bullet)
trans_output(config, 'get_illustration', render_image_url)
trans_output(config, 'aggregate_story_and_image', t.dynamic_trans)






# from meshed import code_to_dag
#
#
# @code_to_dag
# def audio_ml():
#     audio, annots = get_audio_and_annots(source)
#     train, test = split(audio, annots)
#     model = mk_model(train)
#     test_results = run_model(model, test)
#
#
# # audio_ml.dot_digraph()
#
# # @code_to_dag
# # def make_children_story():
# #     rhyming_story = make_it_rhyming(story)
# #     image = get_illustration(rhyming_story, image_style)
# #     page = aggregate_story_and_image(image, rhyming_story)
# #
# #
# # import extrude
# # from extrude import mk_api, run_api
# #
# # def _make_children_story(story, image_style):
# #     return make_children_story(story, image_style)
#
# # app = mk_api([_make_children_story])
# # run_api(app, server='wsgiref')
#
# _func = audio_ml
#
#
# def _func(source):
#     return audio_ml(source)
#
#
# from extrude import mk_web_app
#
#
# if __name__ == '__main__':
#     app = mk_web_app([_func], api_url='http://localhost:3030/openapi')
#     app()
#
#
# # import os
# # import re
# #
# # from config2py import get_configs_local_store, get_config, ask_user_for_input
# #
# # # can specify a name of a subdirectory as an argument. By default, will be config2py'
# #
# # configs_local_store = get_configs_local_store()
# #
# # api_key = get_config(
# #     'NAME_OF_CONFIG_KEY',
# #     sources=[
# #         # Try to find it in oa config
# #         configs_local_store,
# #         # Try to find it in os.environ (environmental variables)
# #         os.environ,
# #         # If not, ask the user to input it
# #         lambda k: ask_user_for_input(
# #             f"Please set your OpenAI API key and press enter to continue. "
# #             "If you don't have one, you can get one at "
# #             "https://platform.openai.com/account/api-keys. ",
# #             mask_input=True,
# #             masking_toggle_str='',
# #             egress=lambda v: configs_local_store.__setitem__(k, v),
# #         )
# #     ],
# # )
# #
# # from typing import Union, ModuleType
# # import openapi_python_client as opc
# #
# #
# # def get_python_module_from_openapi_specs(
# #         openapi_specs: Union[str, dict],
# #         python_module_name: str,
# # ) -> ModuleType:
# #     """Get a python module from openapi specs
# #
# #     Args:
# #         openapi_specs: The openapi specs in either a string or a dict
# #         python_module_name: The name of the python module to create
# #
# #     Returns:
# #         The python module
# #     """
# #     if isinstance(openapi_specs, str):
# #         import yaml
# #         openapi_specs = yaml.safe_load(openapi_specs)
# #
# #     return opc.generate_module(
# #         openapi_specs=openapi_specs,
# #         module_name=python_module_name,
# #     )
