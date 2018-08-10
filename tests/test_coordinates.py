import ratcave as rc
import pytest
import numpy as np

def test_from_translation_matrix():
    for _ in range(10):
        mat = np.random.rand(4, 4)
        trans = rc.Translation.from_matrix(mat)
        assert np.all(np.isclose(trans.xyz, mat[:3, -1]))

def test_to_translation_matrix():
    for _ in range(10):
        vals = np.random.rand(3)
        trans = rc.Translation(*vals)
        mat = trans.to_matrix()
        assert np.all(np.isclose(trans.xyz, mat[:3, -1]))