from meshed import code_to_dag


@code_to_dag
def audio_ml():
    audio, annots = get_audio_and_annots(source)
    train, test = split(audio, annots)
    model = mk_model(train)
    test_results = run_model(model, test)


# audio_ml.dot_digraph()

# @code_to_dag
# def make_children_story():
#     rhyming_story = make_it_rhyming(story)
#     image = get_illustration(rhyming_story, image_style)
#     page = aggregate_story_and_image(image, rhyming_story)
#
#
# import extrude
# from extrude import mk_api, run_api
#
# def _make_children_story(story, image_style):
#     return make_children_story(story, image_style)

# app = mk_api([_make_children_story])
# run_api(app, server='wsgiref')

_func = audio_ml


def _func(source):
    return audio_ml(source)


from extrude import mk_web_app


if __name__ == '__main__':
    app = mk_web_app([_func], api_url='http://localhost:3030/openapi')
    app()


# import os
# import re
#
# from config2py import get_configs_local_store, get_config, ask_user_for_input
#
# # can specify a name of a subdirectory as an argument. By default, will be config2py'
#
# configs_local_store = get_configs_local_store()
#
# api_key = get_config(
#     'NAME_OF_CONFIG_KEY',
#     sources=[
#         # Try to find it in oa configs
#         configs_local_store,
#         # Try to find it in os.environ (environmental variables)
#         os.environ,
#         # If not, ask the user to input it
#         lambda k: ask_user_for_input(
#             f"Please set your OpenAI API key and press enter to continue. "
#             "If you don't have one, you can get one at "
#             "https://platform.openai.com/account/api-keys. ",
#             mask_input=True,
#             masking_toggle_str='',
#             egress=lambda v: configs_local_store.__setitem__(k, v),
#         )
#     ],
# )
#
# from typing import Union, ModuleType
# import openapi_python_client as opc
#
#
# def get_python_module_from_openapi_specs(
#         openapi_specs: Union[str, dict],
#         python_module_name: str,
# ) -> ModuleType:
#     """Get a python module from openapi specs
#
#     Args:
#         openapi_specs: The openapi specs in either a string or a dict
#         python_module_name: The name of the python module to create
#
#     Returns:
#         The python module
#     """
#     if isinstance(openapi_specs, str):
#         import yaml
#         openapi_specs = yaml.safe_load(openapi_specs)
#
#     return opc.generate_module(
#         openapi_specs=openapi_specs,
#         module_name=python_module_name,
#     )
