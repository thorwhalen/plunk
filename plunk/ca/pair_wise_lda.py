from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from itertools import combinations
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA


class PairwiseLda(BaseEstimator, TransformerMixin):
    """
    A class finding the hyperplane spanning the lines found by LDA when trying to separate the pair of classes
    """

    def __init__(self, n_components=None):
        self.n_components = n_components

    # if normal is set to True, the projection vectors are taken in the residue of the previously found ones
    def fit(self, X, y, classes=None, normal=False):
        if classes is None:
            classes = set(y)
        scalings_ = []
        for pair_classes in combinations(classes, 2):
            pair_mask = np.isin(y, pair_classes)
            X_pair = X[pair_mask]
            y_pair = y[pair_mask]
            lda = LDA()
            lda.fit(X_pair, y_pair)
            scalings_.append(lda.scalings_.flatten())
            if normal:
                X = residue(lda.scalings_, X)
        self.proj_mat = np.array(scalings_).T

    def transform(self, X, y=None):
        return np.dot(X, self.proj_mat.T)
