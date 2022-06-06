from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np


class PseudoPca(BaseEstimator, TransformerMixin):
    """
    A class imitating PCA in the following way:
    """

    def __init__(self, n_components, n_samples=None):
        self.hyper_dim = n_components + 1
        if n_samples is None:
            n_samples = n_components
        self.n_samples = n_samples

    def get_random_hyperplane_unit_matrix(self, X):
        rand_points = X[np.random.choice(X.shape[0], self.hyper_dim)]
        hyper_plane_basis = rand_points - np.tile(rand_points[0, :], (rand_points.shape[0], 1))
        hyper_plane_basis = hyper_plane_basis[1:, :]
        unit_matrix = np.array(
            [vec / norm for vec, norm in zip(hyper_plane_basis, np.sum(hyper_plane_basis ** 2, axis=1) ** 0.5)])
        return unit_matrix

    def fit(self, X, y=None):
        unit_matrices = []
        i = 0
        while i <= self.n_samples:
            rand_hyper = self.get_random_hyperplane_unit_matrix(X)
            # this check is here for the following reason: rand_hyper may have nan's.
            # this can happen when in get_random_hyperplane_unit_matrix the hyper_plane_basis
            # has the first row repeated (requiring X to have repeated vectors), then hyper_plane_basis
            # can have rows of zero, in which case the division by norm in unit matrix yields some nan
            if np.isnan(np.max(rand_hyper)):
                pass
            else:
                unit_matrices.append(rand_hyper)
                i += 1
        self.proj_mat = np.mean(np.array(unit_matrices), axis=0)

    def transform(self, X, y=None):
        return np.dot(X, self.proj_mat.T)
