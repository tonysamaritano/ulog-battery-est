import pytest
from batlib.model import Model
from batlib.model import PolyStruct


def model_test0():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    assert model_1.update(0.25 * 1e6) == 16.0
