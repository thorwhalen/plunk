import numpy as np


def extract_edge_indices_from_bool_segment(
    bool_segment: np.ndarray, last_sample_of_previous_segment: bool, edge_type: str
) -> list:
    int_segment = bool_segment.astype(int)
    prepend = int(last_sample_of_previous_segment)
    edges = np.diff(int_segment, prepend=prepend)
    if edge_type == 'rising':
        edge_value = 1
    elif edge_type == 'descending':
        edge_value = -1
    return (edges == edge_value).nonzero()[0].tolist()
