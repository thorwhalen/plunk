from plunk.ca.linalg_utils import null_space, projection, residue
import numpy as np
import pytest


@pytest.mark.parametrize('basis',
                         [[[1, 0, 0]],
                          [[1, 0, 0], [0, 1, 0]],
                          (2, 3),
                          (100, 200)])
def test_null_space(basis):
    if isinstance(basis, tuple):
        basis = np.random.random(basis)
    basis = np.array(basis)
    normal = null_space(basis)
    prod = np.dot(normal, basis.T)
    zero_as_prod = np.zeros(prod.shape)
    assert np.allclose(prod, zero_as_prod), "The null space is not normal to the original space"


@pytest.mark.parametrize('basis, vector',
                          [([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [1, 2, 3]),
                           ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 1, 2], [3, 4, 5]])])
def test_projection(basis, vector):
    basis = np.array(basis)
    vector = np.array(vector)
    vect_proj = projection(basis, vector)
    assert np.allclose(vector, vect_proj), "The projection differs from the original vector, something is not right"


@pytest.mark.parametrize('X, span',
                         [(np.random.random((100, 3)), np.array([[1, 0, 0], [0, 1, 0]])),
                          (np.random.random((100, 4)), np.array([[1, 0, 0, 0]]))])
def test_proj_plus_res(X, span):
    assert np.allclose(projection(span.T, X) + residue(span.T, X), X)


@pytest.mark.parametrize('span_vectors, vectors',
                         [([[1, 0], [0, 1]], [[2, 3]]),
                          ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[2, 3, 4]])])
def test_residue(span_vectors, vectors):
    span_vectors = np.array(span_vectors)
    vectors = np.array(vectors)
    assert np.allclose(residue(span_vectors, vectors), np.zeros(vectors.shape))