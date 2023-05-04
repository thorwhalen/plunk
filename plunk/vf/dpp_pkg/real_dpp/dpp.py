
from functools import lru_cache
from pathlib import Path
from typing import List, TypedDict
from olab import simple_chunker, simple_featurizer
from py2store import LocalPickleStore
from omodel.outliers.pystroll import OutlierModel as Stroll


AGGR_BT_ATTR = '_aggregation_bt'
AGGR_SESSION_ATTR = '_outlier_detected_in_session'
THRESHOLD = 2

Annotation = TypedDict(
	'Annotation',
    name=str,
    kind=str,
    bt=int,
    tt=int,
)

TimestampedData = TypedDict(
    'TimestampedData',
    data=bytes,
    bt=int,
)


class DPP():
    def run(self, timestamped_data: TimestampedData, aggregate: bool = False) -> List[Annotation]:
        # return _dpp(self, timestamped_data, aggregate)
        chks = simple_chunker(timestamped_data['data'])
        fvs = simple_featurizer(chks)
        scores = _apply_model(fvs)
        return _interpret_scores(timestamped_data, scores, self, aggregate)

    __call__ = run


@lru_cache
def get_fitted_model():
    store = LocalPickleStore(str(Path(__file__).parent))
    model_dict = store['fitted_model.pkl']
    return Stroll.from_dpp_jdict(model_dict)


def _apply_model(fvs):
    fitted_model = get_fitted_model()
    scores = fitted_model.score_samples(X=fvs)
    return scores


def _interpret_scores(timestamped_data, scores, scope, aggregate):
    def _generate_annotations():
        if aggregate and not hasattr(scope, AGGR_BT_ATTR):
            setattr(scope, AGGR_BT_ATTR, timestamped_data['bt'])

        max_score = max(scores)
        if max_score > THRESHOLD:
            result = Annotation(
                name='Outlier detected in block!',
                kind='DPP',
                bt=timestamped_data['bt'],
                tt=timestamped_data['tt'],
		    )
            yield result
            if aggregate:
                setattr(scope, AGGR_SESSION_ATTR, True)
        if not aggregate:
            if getattr(scope, AGGR_SESSION_ATTR, False):
                yield Annotation(
                    name='Outlier detected in session!',
                    kind='DPP',
                    bt=getattr(scope, AGGR_BT_ATTR),
                    tt=timestamped_data['tt'],
                )
	    else:
		yield Annotation(
                    name='No outlier detected in session.',
                    kind='DPP',
                    bt=getattr(scope, AGGR_BT_ATTR),
                    tt=timestamped_data['tt'],
                )
            if hasattr(scope, AGGR_BT_ATTR):
                delattr(scope, AGGR_BT_ATTR)
            if hasattr(scope, AGGR_SESSION_ATTR):
                delattr(scope, AGGR_SESSION_ATTR)

    return list(_generate_annotations())


# _dpp_impl = {
#     # "bytes_to_wf": bytes_to_wf,
#     'chunker': simple_chunker,
#     'simple_featurizer': simple_featurizer,
#     'apply_model': _apply_model,
#     'interpret_scores': _interpret_scores,
# }


# @code_to_dag(func_src=_dpp_impl)
# def _dpp(scope, timestamped_data: TimestampedData, aggregate: bool = False):
#     chks = chunker(timestamped_data['data'])
#     fvs = featurizer(chks)
#     scores = apply_model(fvs)
#     result = interpret_scores(timestamped_data, scores, scope, aggregate)
