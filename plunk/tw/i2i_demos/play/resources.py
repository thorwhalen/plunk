from meshed import code_to_dag


def extract_funcs(dag):
    for func_node in dag.func_nodes:
        yield func_node.func


@code_to_dag
def _audio_ml():
    audio, annots = get_audio_and_annots(source)
    train, test = split(audio, annots)
    model = mk_model(train)
    test_results = run_model(model, test)


def audio_ml(source):
    return _audio_ml(source)


@code_to_dag
def make_children_story():
    rhyming_story = make_it_rhyming(story)
    image = get_illustration(rhyming_story, image_style)
    page = aggregate_story_and_image(image, rhyming_story)


def _make_children_story(story, image_style):
    return make_children_story(story, image_style)


funcs = [audio_ml]

funcs = [_make_children_story] + list(extract_funcs(make_children_story))
