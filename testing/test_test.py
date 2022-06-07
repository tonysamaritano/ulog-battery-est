import pytest
from batlib.model import Model
from batlib.model import PolyStruct


def test_test():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    model_1.setInput(12.3, 30, 25)
    assert model_1.update(0.25 * 1e6) == 1066.7119729339645
