# License: Apache 2.0

import warnings
from functools import partial

import numpy as np
from scipy.sparse import SparseEfficiencyWarning
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.neighbors import kneighbors_graph
from joblib import Parallel, delayed
from sklearn.utils.validation import check_array, check_is_fitted


class KNeighborsGraph(BaseEstimator, TransformerMixin):
    """Adjacency matrices of k-nearest neighbor graphs.

    Given a two-dimensional array of row vectors seen as points in
    high-dimensional space, the corresponding kNN graph is a simple,
    undirected and unweighted graph with a vertex for every vector in the
    array, and an edge between two vertices whenever either the first
    corresponding vector is among the k nearest neighbors of the
    second, or vice-versa.

    :obj:`sklearn.neighbors.kneighbors_graph` is used to compute the
    adjacency matrices of kNN graphs.

    Parameters
    ----------
    n_neighbors : int, optional, default: ``4``
        Number of neighbors to use.

    metric : string or callable, default ``'minkowski'``
        Metric to use for distance computation. Any metric from scikit-learn
        or :obj:`scipy.spatial.distance` can be used.
        If metric is a callable function, it is called on each
        pair of instances (rows) and the resulting value recorded. The callable
        should take two arrays as input and return one value indicating the
        distance between them. This works for Scipy's metrics, but is less
        efficient than passing the metric name as a string.
        Distance matrices are not supported.
        Valid values for `metric` are:

        - from scikit-learn: [``'cityblock'``, ``'cosine'``, ``'euclidean'``,
          ``'l1'``, ``'l2'``, ``'manhattan'``]
        - from :obj:`scipy.spatial.distance`: [``'braycurtis'``,
          ``'canberra'``, ``'chebyshev'``, ``'correlation'``, ``'dice'``,
          ``'hamming'``, ``'jaccard'``, ``'kulsinski'``, ``'mahalanobis'``,
          ``'minkowski'``, ``'rogerstanimoto'``, ``'russellrao'``,
          ``'seuclidean'``, ``'sokalmichener'``, ``'sokalsneath'``,
          ``'sqeuclidean'``, ``'yule'``]

        See the documentation for :obj:`scipy.spatial.distance` for details on
        these metrics.

    p : int, optional, default: ``2``
        Parameter for the Minkowski (i.e. :math:`\\ell^p`) metric from
        :obj:`sklearn.metrics.pairwise.pairwise_distances`. `p` = 1 is the
        Manhattan distance and `p` = 2 is the Euclidean distance.

    metric_params : dict, optional, default: ``{}``
        Additional keyword arguments for the metric function.

    n_jobs : int or None, optional, default: ``None``
        The number of jobs to use for the computation. ``None`` means 1
        unless in a :obj:`joblib.parallel_backend` context. ``-1`` means
        using all processors.

    Examples
    --------
    >>> import numpy as np
    >>> from giotto.graphs import KNeighborsGraph
    >>> X = np.array([[[0, 1, 3, 0, 0],
    ...                [1, 0, 5, 0, 0],
    ...                [3, 5, 0, 4, 0],
    ...                [0, 0, 4, 0, 0]]])
    >>> kng = KNeighborsGraph(n_neighbors=2)
    >>> Xg = kng.fit_transform(X)
    >>> print(Xg[0].toarray())
    [[0. 1. 1. 1.]
     [1. 0. 0. 1.]
     [1. 0. 0. 1.]
     [1. 1. 1. 0.]]

    """

    def __init__(self, n_neighbors=4, metric='euclidean',
                 p=2, metric_params={}, n_jobs=None):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.p = p
        self.metric_params = metric_params
        self.n_jobs = n_jobs

    def _make_adjacency_matrix(self, X):
        A = self._nearest_neighbors(X)
        rows, cols = A.nonzero()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', SparseEfficiencyWarning)
            A[cols, rows] = 1
        return A

    def fit(self, X, y=None):
        """Do nothing and return the estimator unchanged.

        This method is there to implement the usual scikit-learn API and hence
        work in pipelines.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_points, n_dimensions)
            Input data. Each entry in `X` along axis 0 is an array of
            ``n_points`` row vectors in ``n_dimensions``-dimensional space.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        self : object

        """
        check_array(X, allow_nd=True)

        self._nearest_neighbors = partial(
            kneighbors_graph, n_neighbors=self.n_neighbors, metric=self.metric,
            p=self.p, metric_params=self.metric_params, mode='connectivity',
            include_self=False)

        return self

    def transform(self, X, y=None):
        """Compute kNN graphs and return their adjacency matrices as
        sparse matrices.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_points, n_dimensions)
            Input data. Each entry in `X` along axis 0 is an array of
            ``n_points`` row vectors in ``n_dimensions``-dimensional space.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        Xt : ndarray of sparse matrices in CSR format, shape (n_samples,)
            Adjacency matrices of kNN graphs.

        """
        # Check if fit had been called
        check_is_fitted(self, ['_nearest_neighbors'])
        X = check_array(X, allow_nd=True)

        Xt = Parallel(n_jobs=self.n_jobs)(
            delayed(self._make_adjacency_matrix)(X[i]) for i in
            range(X.shape[0]))
        Xt = np.array(Xt)
        return Xt
