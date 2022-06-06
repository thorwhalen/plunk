from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np


class PseudoLda(BaseEstimator, TransformerMixin):
    """
    A class finding the hyperplane passing the centers of the classes in y and projecting the vectors in X
    onto that hyperplane. The number of components is fixed to n_classes - 1, no more no less. If the classes form
    well separated spherical clusters, the class will work as well as LDA but be much faster.
    Trouble will arise if the clusters are parallel ellipsoides, close enough that there centers will be relatively
    close in the hyperplane chosen by PseudoLda.
    """

    def __init__(self, n_components):
        self.hyper_dim = n_components + 1

    def fit(self, X, y):
        y = np.array(y)
        X = np.array(X)
        centers = []
        for class_ in set(y):
            cluster = X[y == class_]
            centers.append(np.mean(cluster, axis=0))
        centers = np.array(centers)
        hyper_plane_basis = centers - np.tile(centers[0, :], (centers.shape[0], 1))
        hyper_plane_basis = hyper_plane_basis[1:, :]
        unit_matrix = np.array(
            [vec / norm for vec, norm in zip(hyper_plane_basis, np.sum(hyper_plane_basis ** 2, axis=1) ** 0.5)])
        self.proj_mat = unit_matrix.T

    def transform(self, X, y=None):
        return np.dot(X, self.proj_mat)
