from ratcave.utils import gl as ugl
import ctypes
import pytest


def test_vec_creates_ctypes_array():
    data = ugl.vec([10, 20, 30])
    assert isinstance(data, ctypes.Array)


def test_vec_makes_sequence():
    data = ugl.vec([10, 20, 30])
    assert data[0] == 10
    assert data[2] == 30


def test_vec_is_typed_and_defaults_to_float():
    data = ugl.vec([10, 20, 30])
    assert data._type_ == ctypes.c_float
    data = ugl.vec([10., 20., 30.])
    assert data._type_ == ctypes.c_float
    data = ugl.vec([10., 20,])
    assert data._type_ == ctypes.c_float
    assert data[1] == 20.

    int_data = ugl.vec([10, 20], dtype=int)
    assert int_data._type_ == ctypes.c_uint


def test_int_vec_is_unsigned():
    with pytest.raises(ValueError):
        ugl.vec([10, -20], dtype=int)


