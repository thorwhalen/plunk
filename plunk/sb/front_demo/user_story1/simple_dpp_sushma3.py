# Simple dpp using AudioSegments
# AudioSegment(
#         start_date=0,
#         end_date=1e6 * frames_per_buffer / rate,
#         waveform=mock_pcm_bytes(),
#         frame_count=frames_per_buffer,
#         status_flags=PaStatusFlags.paNoError,
#     )

import numpy as np

from olab.base import simple_chunker, simple_featurizer
from olab.types import WaveForm
from omodel.outliers.pystroll import OutlierModel as Stroll
from meshed import code_to_dag
from recode import decode_wav_bytes
from audiostream2py import AudioSegment


def bytes_to_wf(wav_bytes: bytes) -> WaveForm:
    wf, sr = decode_wav_bytes(wav_bytes)
    return np.array(wf)


# ML steps
def learn_model(fvs, n_centroids=5):
    model = Stroll(n_centroids=n_centroids)
    model.fit(X=fvs)

    return model


def apply_model(fvs, fitted_model):
    scores = fitted_model.score_samples(X=fvs)
    return scores


def segment_to_wf(segment: AudioSegment) -> WaveForm:
    wf = segment.waveform
    return wf


def segment_to_bt_tt(segment: AudioSegment) -> tuple:
    bt = segment.start_date
    tt = segment.end_date
    return bt, tt


def aggregate_scores(scores, aggregation_method):
    if aggregation_method == "max":
        return max(scores)

    elif aggregation_method == "mean":
        return np.mean(scores)

    else:
        raise ValueError(f"Aggregation method {aggregation_method} not supported")


def decision(score, threshold: float):
    if score > threshold:
        return True
    else:
        return False


def format_output(decision, bt_tt):
    bt, tt = bt_tt
    if decision:
        return {"output": "outlier", "bt": bt, "tt": tt}
    else:
        return {"output": "normal", "bt": bt, "tt": tt}


d = {
    # "bytes_to_wf": bytes_to_wf,
    "segment_to_wf": segment_to_wf,
    "simple_chunker": simple_chunker,
    "simple_featurizer": simple_featurizer,
    "learn_model": learn_model,
    "apply_model": apply_model,
    "aggregate_scores": aggregate_scores,
    "decision": decision,
}

# simple DPP in form of a DAG
@code_to_dag(func_src=d)
def simple_dpp(block: AudioSegment, aggregation_method: str):
    wf = segment_to_wf(block)
    chks = simple_chunker(wf)
    fvs = simple_featurizer(chks)
    model = learn_model(fvs)
    # scores = apply_model(fvs, model)
    # aggregated_scores = aggregate_scores(scores, aggregation_method)
    # result = decision(aggregated_scores, threshold=2.0)
    

def apply_trained_model(block: AudioSegment, fitted_model, preprocessing_pipeline):
    wf = segment_to_wf(block)

    fvs = simple_featurizer(wf)
    scores = apply_model(fvs, fitted_model)
    
    return scores


if __name__ == "__main__":
    # make input data for testing purposes
    from pyckup import grab

    # make a wf as a bytes object
    wf = grab("https://www.dropbox.com/s/yueb7mn6mo6abxh/0_0.wav?dl=0")
    block = AudioSegment(waveform=wf, start_date=0, end_date=1e6 * len(wf) / 16000)

    # check the type
    # print(f"{type(wf)=}")

    # # run the experiment
    result = simple_dpp(block, "max")

    # print(scores[:10])
