from meshed import code_to_dag


import oa.examples.illustrate_stories as ii


func_src = {
    'topic_points': ii.topic_points,
    'get_image_description': ii.get_image_description,
    'get_illustration': ii.get_illustration,
    'aggregate_story_and_image': ii.aggregate_story_and_image,
}


@code_to_dag(func_src=func_src, name='slide_maker')
def dag():
    talking_points = topic_points(topic, n_talking_points)
    illustration_description = get_image_description(talking_point, image_style)
    img_url = get_illustration(illustration_description, image_style)
    slide = aggregate_story_and_image(img_url, text)


funcs = list(dag.find_funcs())
