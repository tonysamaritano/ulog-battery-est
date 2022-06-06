import pytest
from batlib.model import Model
from batlib.model import PolyStruct

def test_test():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    assert model_1.update(120.0 * 1e6) == 16.0