# -*- coding: utf-8 -*-
"""MultiRocketMultivariate test code."""
import numpy as np
import pytest
from sklearn.linear_model import RidgeClassifierCV
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sktime.datasets import load_basic_motions
from sktime.transformations.panel.rocket import MultiRocketMultivariate
from sktime.utils.validation._dependencies import _check_soft_dependencies


@pytest.mark.skipif(
    not _check_soft_dependencies("numba", severity="none"),
    reason="skip test if required soft dependency not available",
)
def test_multirocket_multivariate_on_basic_motions():
    """Test of MultiRocketMultivariate on basic motions."""
    # load training data
    X_training, Y_training = load_basic_motions(split="train", return_X_y=True)

    # 'fit' MultiRocket -> infer data dimensions, generate random kernels
    multirocket = MultiRocketMultivariate(random_state=0)
    multirocket.fit(X_training)

    # transform training data
    X_training_transform = multirocket.transform(X_training)

    # test shape of transformed training data -> (number of training
    # examples, nearest multiple of 4*84=336 < 50,000 (2*4*6_250))
    np.testing.assert_equal(X_training_transform.shape, (len(X_training), 49_728))

    # fit classifier
    classifier = make_pipeline(
        StandardScaler(with_mean=False),
        RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
    )
    classifier.fit(X_training_transform, Y_training)

    # load test data
    X_test, Y_test = load_basic_motions(split="test", return_X_y=True)

    # transform test data
    X_test_transform = multirocket.transform(X_test)

    # test shape of transformed test data -> (number of test examples,
    # nearest multiple of 4*84=336 < 50,000 (2*4*6_250))
    np.testing.assert_equal(X_test_transform.shape, (len(X_test), 49_728))

    # predict (alternatively: 'classifier.score(X_test_transform, Y_test)')
    predictions = classifier.predict(X_test_transform)
    accuracy = accuracy_score(predictions, Y_test)

    # test predictions (on BasicMotions, should be 100% accurate)
    assert accuracy == 1.0
