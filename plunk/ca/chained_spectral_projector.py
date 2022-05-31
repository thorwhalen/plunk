import importlib
import numpy as np
import warnings

from sklearn.neighbors import NeighborhoodComponentsAnalysis as NCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn import random_projection

from plunk.ca.pseudo_pca import PseudoPca
from plunk.ca.pseudo_lda import PseudoLda
from plunk.ca.pair_wise_lda import PairwiseLda
from plunk.ca.linalg_utils import residue, orth
from plunk.ca.band_projection_matrix import make_band_matrix, make_buckets, hertz_to_mel

CLUSTERING_OPTIONS = ('KMeans', 'SpectralClustering', 'AffinityPropagation',
                      'AgglomerativeClustering', 'Birch', 'MeanShift')


def learn_spect_proj(X, y=None, spectral_proj_name='pca',
                     clustering_meth='KMeans',
                     clustering_options=CLUSTERING_OPTIONS,
                     kwargs_feat=None,
                     kwargs_clust=None):
    """
    Function to learn each of the important spectral projection

    :param X: the fvs, an array of size n*k
    :param y: the classes, an array of size n
    :param spectral_proj_name: a string of the name of the featurizer
    :param args: extra argument to be passed to the featurizer class
    :return: a matrix in the form of a numpy array
    """

    clustering_options = set(clustering_options)
    kwargs_feat = kwargs_feat or {'n_components': 10}
    kwargs_clust = kwargs_clust or {}

    assert clustering_meth in clustering_options, 'clustering options must one of {}'.format(
        ', '.join(map(str, clustering_options)))
    clusterer_m = getattr(importlib.import_module('sklearn.cluster'), clustering_meth)

    if spectral_proj_name == 'random_gaussian':
        rand_proj = random_projection.GaussianRandomProjection(**kwargs_feat)
        rand_proj.fit(X)
        proj_matrix = rand_proj.components_.T

    elif spectral_proj_name == 'keep_features':
        indices = kwargs_feat['indices']
        proj_matrix = np.zeros((X.shape[1], len(indices)))
        for idx in range(len(indices)):
            proj_matrix[indices[idx], idx] = 1

    elif spectral_proj_name == 'pca':
        pca = PCA(**kwargs_feat)
        pca.fit(X)
        proj_matrix = pca.components_.T

    elif spectral_proj_name == 'pseudo_pca':
        # make the pseudo pca proj matrix
        ppca = PseudoPca(**kwargs_feat)
        ppca.fit(X)
        proj_matrix = ppca.proj_mat.T

    elif spectral_proj_name == 'lda':
        lda = LDA(**kwargs_feat)
        lda.fit(X, y)
        n_components = kwargs_feat['n_components']
        proj_matrix = lda.scalings_[:, :n_components]

    elif spectral_proj_name == 'pseudo_lda':
        plda = PseudoLda(**kwargs_feat)
        plda.fit(X, y)
        proj_matrix = plda.proj_mat

    elif spectral_proj_name == 'pairwise_lda':
        plda = PairwiseLda(**kwargs_feat)
        classes = kwargs_feat.get('classes', None)
        normal = kwargs_feat.get('normal', False)
        plda.fit(X, y, classes=classes, normal=normal)
        proj_matrix = plda.proj_mat

    elif spectral_proj_name == 'unsupervised_lda':
        n_components = kwargs_feat['n_components']
        if y is not None:
            warning = 'Warning: y will be replaced by classes found by the chosen clusterer'
            warnings.warn(warning)
        if 'n_clusters' in clusterer_m.__init__.__code__.co_varnames:
            y = clusterer_m(n_clusters=n_components + 1, **kwargs_clust).fit_predict(X)
        else:
            y = clusterer_m(**kwargs_clust).fit_predict(X)
        lda = LDA(**kwargs_feat)
        lda.fit(X, y)
        proj_matrix = lda.scalings_[:, :n_components]

    elif spectral_proj_name == 'unsupervised_pseudo_lda':
        n_components = kwargs_feat['n_components']
        if y is not None:
            warning = 'Warning: y will be replaced by classes found by the chosen clusterer'
            warnings.warn(warning)
        if 'n_clusters' in clusterer_m.__init__.__code__.co_varnames:
            y = clusterer_m(n_clusters=n_components + 1, **kwargs_clust).fit_predict(X)
        else:
            y = clusterer_m(**kwargs_clust).fit_predict(X)
        pseudo_lda = PseudoLda(**kwargs_feat)
        pseudo_lda.fit(X, y)
        proj_matrix = pseudo_lda.proj_mat[:, :n_components]

    elif spectral_proj_name == 'nca':
        nca = NCA(**kwargs_feat)
        nca.fit(X, y)
        proj_matrix = nca.components_.T

    elif spectral_proj_name == 'unsupervised_nca':
        n_components = kwargs_feat['n_components']
        if y is not None:
            print('y will be replaced by classes found by the chosen clusterer')
        if 'n_clusters' in clusterer_m.__init__.__code__.co_varnames:
            y = clusterer_m(n_clusters=n_components + 1, **kwargs_clust).fit_predict(X)
        else:
            y = clusterer_m(**kwargs_clust).fit_predict(X)
        nca = NCA(**kwargs_feat)
        nca.fit(X, y)
        proj_matrix = nca.components_.T

    elif spectral_proj_name == 'linear_regression':
        lr = LinearRegression()
        lr.fit(X, y)
        proj_matrix = lr.coef_.T

    elif spectral_proj_name == 'default':
        n_components = kwargs_feat['n_components']
        X = np.array(X)
        n_freq = X.shape[1]
        freqs_weighting = kwargs_feat.get('freqs_weighting', hertz_to_mel)
        buckets = make_buckets(n_buckets=n_components,
                               reverse=False,
                               freqs_weighting=freqs_weighting,
                               freq_range=(0, n_freq))
        default_matrix = make_band_matrix(buckets, n_freq=n_freq)
        proj_matrix = default_matrix.T


    else:
        all_spectral_proj = ', '.join(['keep_features', 'pca',
                                       'lda', 'pseudo_pca',
                                       'unsupervised_lda',
                                       'unsupervised_nca',
                                       'nca',
                                       'linear_regression',
                                       'unsupervised_pseudo_lda',
                                       'pseudo_lda',
                                       'pairwise_lda',
                                       'random_gaussian',
                                       'default'])
        raise ValueError(f'the spectral projector must be one of: {all_spectral_proj}')

    return proj_matrix


def keep_only_indices(indices, n_freq=1025):
    """
    Makes a matrix which when a spectra is multiplied with it, only the entires in the list indices are kept
    :param indices: a list of indices to keep
    :param n_freq: the total number of frequencies in the spectra
    :return: a matrix of size (n_freq, len(indices))
    """

    proj_matrix = np.zeros((n_freq, len(indices)))
    for idx in range(len(indices)):
        proj_matrix[indices[idx], idx] = 1
    return proj_matrix


def learn_chain_proj_matrix(X, y=None, chain=({'type': 'pca', 'args': {'n_components': 5}},),
                            indices=None, n_freq=1025):
    """
    A function successively learning a projections matrix on the residue of the previous one. The projections
    matrices are then concatenated and return as one single projection matrix. Note that the final projection
    matrix may not produce fvs of the size the sum of the components of each part, i.e., care must be taken
    to ensure each classes called must be able to produce the required number of components. For example,
    if the number of classes is 10, then lda can only produce 9 dimensions. To obtain say 12 dimension, the user
    will need to chain two lda's, for example with size 9 and 3 respectively.

    :param X: the fvs, an array of size n*k
    :param y: the classes, an array of size n
    :param chain: a tuple of dictionaries each containing the type of projection along with its parameters
    :param indices: the indices of the spectra to work with, anything else is discarded
    :param n_freq: the total number of entries from the spectra. Only needed if n_freq is not None, in order to
                   determine the size of the freq_selection_matrix
    :return: a single projection matrix
    """

    from oplot.plot_data_set import scatter_and_color_according_to_y

    freq_selection_matrix = None
    if indices is not None:
        freq_selection_matrix = keep_only_indices(indices, n_freq=n_freq)
        X = np.dot(X, freq_selection_matrix)

    all_proj_matrices = []
    for idx, mat_dict in enumerate(chain):
        kwargs_feat = mat_dict['args']
        proj_matrix = learn_spect_proj(X, y,
                                       spectral_proj_name=mat_dict['type'],
                                       kwargs_feat=kwargs_feat)
        all_proj_matrices.append(proj_matrix)
        #if idx < len(chain) - 1:
        X = residue(proj_matrix, X)
        # # scatter_and_color_according_to_y(X, y)
        # print(X[:3])

    proj_matrix = np.hstack(tuple(all_proj_matrices))
    if indices is not None:
        proj_matrix = np.dot(freq_selection_matrix, proj_matrix)
    return np.array(proj_matrix)


from sklearn.base import TransformerMixin, BaseEstimator


class GeneralProjectionLearner(BaseEstimator, TransformerMixin):
    def __init__(self, chain=({'type': 'pca', 'args': {'n_components': 5}},), indices=None, n_freq=1025):
        self.chain = chain
        self.indices = indices
        self.n_freq = n_freq

    def fit(self, X, y=None, ortho=True):
        """
        Ortho set to True will make it so that the projection into the subspace will be "direction agnostic", which
        makes sense in terms of pure dimension reduction. But for some model, like lda, the length of the vectors onto
        which we will project represent the relative importance of those directions. In that case it may make sense to
        set ortho to False

        :param X: array of vectors
        :param y: array of tags
        :param ortho: boolean, whether or not to orthonormalize the vector onto which to project
        :return:
        """

        self.scalings = learn_chain_proj_matrix(X, y, self.chain, indices=self.indices, n_freq=self.n_freq)
        if ortho:
            self.scalings = orth(self.scalings.T).T
            self.projection_ = np.dot(self.scalings, self.scalings.T)
        else:
            self.projection_ = np.dot(self.scalings, self.scalings.T)
        return self

    def transform(self, X):
        # lower the dimension of the vectors by projecting in the subspace
        return np.dot(X, self.scalings)

    def project(self, X):
        # projects in the SAME space, the dimension is unchanged
        return np.dot(X, self.projection_)

    def space_residue(self, X):
        return X - np.dot(X, self.projection_)


if __name__ == '__main__':
    # PCA's components seems to be orthonormal
    from omodel.fv.chained_spectral_projector import GeneralProjectionLearner
    from sklearn.datasets import load_iris
    #
    # data = load_iris()
    # X = data['data']
    # y = data['target']

    # chain = ({'type': 'pca', 'args': {'n_components': 1}}, {'type': 'pca', 'args': {'n_components': 1}})
    #
    # gpl = GeneralProjectionLearner(chain=chain)
    # XX = gpl.fit_transform(X=X, y=y, ortho=True)
    # XXX = gpl.project(X)
    # XXXX = gpl.space_residue(X)
    #
    # from oplot.plot_data_set import scatter_and_color_according_to_y
    #
    # print(gpl.scalings)
    # scatter_and_color_according_to_y(XX, y)
    # scatter_and_color_according_to_y(XXX, y)
    # scatter_and_color_according_to_y(XXXX, y)

    chain = ({'type': 'log_spaced', 'args': {'n_components': 8, 'chunk_size': 64}},)
    X = np.random.random((100, 33))
    X = None
    gpl = GeneralProjectionLearner(chain=chain)
    gpl.fit(X=X, ortho=False)

    print(gpl.scalings)

