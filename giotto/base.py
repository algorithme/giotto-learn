"""Implements a TransformerResamplerMixin for transformers that have a resample
method."""
# License: Apache 2.0


class TransformerResamplerMixin:
    """Mixin class for all transformers-resamplers in giotto-learn."""

    _estimator_type = 'transformer_resampler'

    def fit_transform(self, X, y=None, **fit_params):
        """Fit to data, then transform it.

        Fits transformer to `X` and `y` with optional parameters `fit_params`
        and returns a transformed version of `X`.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Training set.

        y : ndarray, shape (n_samples,)
            Target values.

        Returns
        -------
        X_new : ndarray, shape (n_samples, n_features_new)
            Transformed array.

        """
        # non-optimized default implementation; override when a better
        # method is possible for a given clustering algorithm
        if y is None:
            # fit method of arity 1 (unsupervised transformation)
            return self.fit(X, **fit_params).transform(X)
        else:
            # fit method of arity 2 (supervised transformation)
            return self.fit(X, y, **fit_params).transform(X, y)

    def transform_resample(self, X, y):
        """Fit to data, then transform it.

        Fits transformer to `X` and `y` with optional parameters `fit_params`
        and returns a transformed version of `X`.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Training set.

        y : ndarray, shape (n_samples,)
            Target values.

        Returns
        -------
        X_new : ndarray, shape (n_samples, n_features_new)
            Transformed array.

        """
        return self.transform(X), self.resample(y, X)

    def fit_transform_resample(self, X, y, **fit_params):
        """Fit to data, then transform it.

        Fits transformer to `X` and `y` with optional parameters `fit_params`
        and returns a transformed version of `X`.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            Training set.

        y : ndarray, shape (n_samples,)
            Target values.

        Returns
        -------
        X_new : ndarray, shape (n_samples, n_features_new)
            Transformed array.

        """
        return self.fit(X, y, **fit_params).transform_resample(X, y)
