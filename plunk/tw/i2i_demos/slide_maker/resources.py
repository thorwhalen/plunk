from meshed import code_to_dag


import oa.examples.illustrate_stories as ii


# def topic_points(topic, n_talking_points=3):
#     return 'Blah blah blah\nbloo bloo'


func_src = {
    'get_talking_points': ii.topic_points,
    'make_illustration_description': ii.get_image_description,
    'make_illustration': ii.get_illustration,
    'aggregate_story_and_image': ii.aggregate_story_and_image,
}


@code_to_dag(func_src=func_src, name='slide_maker')
def dag():
    talking_points = get_talking_points(topic, n_talking_points)
    illustration_description = make_illustration_description(talking_point, image_style)
    img_url = make_illustration(illustration_description, image_style)
    slide = aggregate_story_and_image(img_url, story_text)


funcs = list(dag.find_funcs())
