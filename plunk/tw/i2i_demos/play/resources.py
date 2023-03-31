from meshed import code_to_dag


def extract_funcs(dag):
    for func_node in dag.func_nodes:
        yield func_node.func


# @code_to_dag
# def _audio_ml():
#     audio, annots = get_audio_and_annots(source)
#     train, test = split(audio, annots)
#     model = mk_model(train)
#     test_results = run_model(model, test)
#
#
# def audio_ml(source):
#     return _audio_ml(source)
#
#
# @code_to_dag
# def _audio_ml():
#     audio, annots = get_audio_and_annots(source)
#     train, test = split(audio, annots)
#     model = mk_model(train)
#     test_results = run_model(model, test)


# import oa.examples.illustrate_stories as ii
#
# func_src = dict(
#     make_it_rhyming=ii.make_it_rhyming,
#     get_illustration=ii.get_illustration,
#     aggregate_story_and_image=ii.aggregate_story_and_image
# )
#
# # func_src = None
#
# @code_to_dag(func_src=func_src)
# def make_children_story():
#     rhyming_story = make_it_rhyming(story)
#     image = get_illustration(rhyming_story, image_style)
#     page = aggregate_story_and_image(image, rhyming_story)
#
#
# def _make_children_story(story, image_style="children's book drawing"):
#     return make_children_story(story, image_style)


# funcs = [audio_ml]

# funcs = [_make_children_story] + list(extract_funcs(make_children_story))


#
# def _make_children_story(story, image_style):
#     return make_children_story(story, image_style)
#
#
# funcs = [audio_ml]
#
# funcs = [_make_children_story] + list(extract_funcs(make_children_story))


# For debugging
def _make_children_story(story, image_style="children's book drawing"):
    return '''<html> <body> <img src="https://oaidalleapiprodscus.blob.core.windows.net/private/org-AY3lr3H3xB9yPQ0HGR498f9M/user-7ZNCDYLWzP0GT48V6DCiTFWt/img-W6rSgzo5Kz3AevLsIm2mRYMf.png?st=2023-03-31T15%3A20%3A08Z&se=2023-03-31T17%3A20%3A08Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-03-30T18%3A05%3A30Z&ske=2023-03-31T18%3A05%3A30Z&sks=b&skv=2021-08-06&sig=ZF/tKVnuuiomcbeTwbXq8tLu01gFs3LfGZBsP60BP5o%3D" /> <p><p>Once there was a boy who cried wolf,<br>Whenever something bad happened to him.<br>His parents scolded him,<br>The other kids made fun of him,<br>But he didn&#x27;t care,<br>Because he knew that they&#x27;d all be there,<br>Whenever he needed them.<br><br>One day, a real wolf came along,<br>And the boy cried out for help.<br>But no one came,<br>Because they thought he was lying,<br>And the wolf ate him up.<br><br>The moral of the story is:<br>Don&#x27;t cry wolf unless you&#x27;re sure,<br>Or you&#x27;ll end up eaten like shrimp in chowder.</p></p> </body> </html>
    '''


funcs = [_make_children_story]
