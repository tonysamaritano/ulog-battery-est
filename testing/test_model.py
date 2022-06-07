from matplotlib import testing
import pytest
import unittest

from batlib.model import Model
from batlib.model import PolyStruct


def test_model():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    
    # setter function calls
    
    model_1.setInput(12.3, 1.0, 0)
    model_1.setArmed(False)
    
    # finding time remaining
    sample_interval = .25 * 1e6 # micro seconds
    model_1.update(sample_interval)
    time_remaining= model_1.getTimeEstimate() # seconds
    print(time_remaining)
    assert time_remaining > 16.0 * 60
    assert time_remaining < 18.0 * 60
    
    