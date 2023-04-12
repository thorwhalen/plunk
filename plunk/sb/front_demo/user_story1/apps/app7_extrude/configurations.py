import streamlitfront.tools as t
from front import APP_KEY, RENDERING_KEY
from streamlitfront.tools import trans_output

config = {APP_KEY: {"title": "OtoSense Studio"}, RENDERING_KEY: {}}

# render_image_url = t.Pipe(t.html_img_wrap, t.render_html,)
# render_bullet = t.Pipe(t.lines_to_html_paragraphs, t.text_to_html, t.render_html,)


# trans_output(config, 'topic_points', render_bullet)
# trans_output(config, 'get_illustration', render_image_url)
# trans_output(config, 'aggregate_story_and_image', t.dynamic_trans)
