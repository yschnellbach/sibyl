import pytest
import os
import numpy as np

from snake import Snake


@pytest.fixture
def mock_snake():
    test_base = os.path.dirname(__file__)
    test_file = os.path.join(test_base, "positron_samples.root")
    yield Snake(test_file)


def test_getEvent(mock_snake):
    mock_snake.getEvent(0)


def test_getHitInfo(mock_snake):
    mock_snake.getEvent(0)
    charge, time = mock_snake.getHitInfo()
    assert len(charge) == len(time)
    assert isinstance(charge, np.ndarray)
    assert isinstance(time, np.ndarray)
