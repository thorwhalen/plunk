import pytest
import numpy as np
from plunk.sb.slabsiter_experiments.utils import (
    extract_edge_indices_from_bool_segment,
)


def test_extract_edges():
    bool_segment_1 = np.array(
        [False, False, False, True, True, True, False, False, False]
    )
    bool_segment_2 = np.array(
        [False, False, False, True, True, True, False, False, False, True]
    )
    result_1 = extract_edge_indices_from_bool_segment(bool_segment_1, False, 'rising')
    result_2 = extract_edge_indices_from_bool_segment(
        bool_segment_2, False, 'descending'
    )
    expected_1 = [3]
    expected_2 = [6]
    assert result_1 == expected_1
    assert result_2 == expected_2
