import streamlitfront.tools as t

configs = None

render_image_url = t.Pipe(t.html_img_wrap, t.render_html,)
render_bullet = t.Pipe(t.lines_to_html_paragraphs, t.text_to_html, t.render_html,)

from front import APP_KEY
from streamlitfront.tools import trans_output, dynamic_trans


# THIS WORKS:
working_config = {APP_KEY: {'title': 'Illustrating concepts'}}
trans_output(working_config, 'topic_points', render_bullet)
trans_output(working_config, 'get_illustration', render_image_url)
trans_output(working_config, 'aggregate_story_and_image', t.dynamic_trans)

# SOMETHING LIKE THIS SHOULD WORK (when defined)
# mult_trans_output(config, {
#     'topic_points': render_bullet,
#     'get_illustration': render_image_url,
#     'aggregate_story_and_image', t.dynamic_trans,
# })


# THIS is meant to be more general and eventually plugin-able
# THis DOES NOT YET:
from dol.paths import path_edit
from streamlitfront.tools import render_edits

edits = list(
    render_edits(
        {
            # Renderer obj for output_trans
            'topic_points': dict(output_trans=render_bullet),
            # multiple edits needed: use dict
            'get_illustration': dict(
                # description_content='Generate an image',
                output_trans=render_image_url,
            ),
            # just a function (will be wrapped in an OutputBase, for output_trans)
            'aggregate_story_and_image': t.dynamic_trans,
        }
    )
)

config = {APP_KEY: {'title': 'Illustrating concepts'}}

from front import RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from dol import path_set

config = path_edit(config, edits)


# SCRAP for DEBUG
# import copy
# before = copy.deepcopy(config)
#
#
# for _path, _val in edits:
#     print(f"Setting {_path} to {_val}")
#     path_set(config, _path, _val)
#
#
# from pprint import pprint
# pprint(before)
# pprint(config)
#
#
# def print_dict_diff(dict1, dict2, key_path='', indent=0):
#     for key in dict1:
#         if key not in dict2:
#             print(' ' * indent + f'Key "{key_path}.{key}" not found in dict2')
#         elif type(dict1[key]) != type(dict2[key]):
#             print(' ' * indent + f'Value of key "{key_path}.{key}" has different type: {type(dict1[key])} vs {type(dict2[key])}')
#         elif isinstance(dict1[key], dict):
#             print_dict_diff(dict1[key], dict2[key], f"{key_path}.{key}", indent+2)
#         elif dict1[key] != dict2[key]:
#             print(' ' * indent + f'Value of key "{key_path}.{key}" differs: {dict1[key]} vs {dict2[key]}')
#
#     for key in dict2:
#         if key not in dict1:
#             print(' ' * indent + f'Key "{key_path}.{key}" not found in dict1')
#
#
# print_dict_diff(before, config)
#
# print(f"{render_bullet == render_bullet}")
# print(f"{render_bullet == copy.deepcopy(render_bullet)}")
