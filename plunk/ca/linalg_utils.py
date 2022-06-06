import numpy as np


def null_space(A, rcond=None):
    """
    Find an orthonormal matrix whose rows span the nullspace of the matrix A. Put another way, find a maximal
    number of row vectors, each of which has a 0 dot product with all the rows of A, while those row vectors are
    also normal to each other and of unit length

    >>> A = np.array([[1, 0, 0]])
    >>> null_space(A)
    array([[0., 1., 0.],
           [0., 0., 1.]])

    >>> A = np.array([[1, -2, 6, 8], [2.1, 6, 20, -3]])
    >>> B = null_space(A)

    The vectors are normal

    >>> np.sum(B ** 2, axis=1)
    array([1., 1.])
    """

    u, s, vh = np.linalg.svd(A, full_matrices=True)
    M, N = u.shape[0], vh.shape[1]
    if rcond is None:
        rcond = np.finfo(s.dtype).eps * max(M, N)
    tol = np.amax(s) * rcond
    num = np.sum(s > tol, dtype=int)
    Q = vh[num:, :].T.conj()
    return Q.T


def projection(basis, vectors):
    """
    The vectors live in a k dimensional space S and the columns of the basis are vectors of the same
    space spanning a subspace of S. Gives a representation of the projection of vector into the space
    spanned by basis in term of the basis.

    :param basis: an n-by-k array, a matrix whose vertical columns are the vectors of the basis
    :param vectors: an m-by-k array, a vector to be represented in the basis
    :return: an m-by-k array
    """
    # most consistent with math would be np.dot(basis.T, np.dot(basis, vector))
    return np.dot(np.dot(vectors, basis), basis.T)


def make_proj_matrix(span_vectors):
    span_vectors = orth(span_vectors)
    return np.dot(span_vectors.T, span_vectors)


def projection_(proj_mat, vectors):
    return np.dot(vectors, proj_mat)


def residue(span_vectors, vectors):
    """
    find the residue of each of vectors after projection in basis
    :param span_vectors: an n-by-k array, spanning a vector space A
    :param vectors: an n-by-l array
    :return: an n-by-l array, the residues of vectors with the respect of the projection in the space spanned
             by span_vectors

    >>> span_vectors = np.array([[1, 0], [0, 1]])
    >>> vectors = np.array([[2, 3]])
    >>> print(residue(span_vectors, vectors))
    [[0 0]]
    >>> span_vectors = np.array([[1, 0],[0, 0]])
    >>> vectors = np.array([[2, 3]])
    >>> print(residue(span_vectors, vectors))
    [[0 3]]
    """

    return vectors - projection(span_vectors, vectors)





def orth(A):
    """
    Orthonormalize the matrix A, i.e, replace it with another matrix spanning the same subspace but:
    1) with minimal number of rows
    2) rows normal to each other
    3) rows of length 1

    :param A: a n-by-k array
    :return: a n-by-k array whose row spans the same space as the rows of A and with the normal rows

    >>> M = np.array([[1,2,3], [3,4,5]])
    >>> OM = orth(M)
    >>> # checking the product of O and its transpose is the identity
    >>> np.allclose(np.dot(OM, OM.T), np.eye(2))
    True
    """

    u, s, vh = np.linalg.svd(A.T, full_matrices=False)
    N, M = A.shape
    eps = np.finfo(float).eps
    tol = max(np.max(M), np.max(N)) * np.amax(s) * eps
    num = np.sum(s > tol, dtype=int)
    Q = u[:, :num]
    return Q.T

# def relative_orth(A, B):
#     """
#     Compute an orthonormal array B', all of the rows of which are normal to A
#     and spanning the same space as B itself.
#     Note that A is not required to be orthonormal and A is left unchanged.
#
#     :param A: a n-by-k array
#     :param B: a m-by-k array
#     :return: a m-by-k array B' with the property that span(A, B') = span(A, B)
#
#     """
#     residue_B = residue(A, B)
#
#     return orth(residue_B)
