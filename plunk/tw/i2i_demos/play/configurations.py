import streamlitfront.tools as t

config = {}

from front import APP_KEY, RENDERING_KEY, NAME_KEY, ELEMENT_KEY
from streamlitfront.elements import SelectBox

# config = {APP_KEY: {'title': 'Illustrating concepts'}}

# render_image_url = t.Pipe(
#     t.html_img_wrap, t.render_html,
# )
# render_bullet = t.Pipe(
#     t.lines_to_html_paragraphs, t.text_to_html, t.render_html,
# )
#
# from front import APP_KEY
# from streamlitfront.tools import trans_output, dynamic_trans
#
#
# # THIS WORKS:
# config = {APP_KEY: {'title': 'Illustrating concepts'}}
# trans_output(config, 'topic_points', render_bullet)
# trans_output(config, 'get_illustration', render_image_url)
# trans_output(config, 'aggregate_story_and_image', t.dynamic_trans)
