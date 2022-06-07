from random import random
import pytest

from batlib.model import Model
from batlib.model import PolyStruct


def test_test0():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = [12, 12.3, 11.9, 12.5, 12.3, 12,
                 12.1, 12.3, 12.3, 12.3, 12.3, 12.3, 12.3]
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        print(model_1.getCapacity())
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            1000 and model_1.getTimeEstimate() < 1100)


def test_test1():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    model_1.setArmed(False)
    volt_data = [12.4, 12.1, 12.5, 12.0, 12.6, 11.9, 12.3,
                 12.1, 12.1, 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91,
                 11.91, 11.92, 11.91, 11.90, 11.91
                 ]
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1e3, 25)
        model_1.update(0.05)
    assert (model_1.getTimeEstimate() >
            810 and model_1.getTimeEstimate() < 830)


def test_test2():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = [11.85, 11.8, 11.9, 11.4, 11.86, 11.91, 11.97, 11.99, 12.1, 12.21,
                 12.33, 12.39, 12.44, 12.41, 12.49, 12.49, 12.5, 12.5, 12.49, 12.5, 12.5]
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            1120 and model_1.getTimeEstimate() < 1160)


def test_test3():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = [11.1, 11.1, 11.1, 11.1, 11.3, 11.4, 11.5, 11.6,
                 11.7, 11.7, 11.7, 11.6, 11.7, 11.7, 12.5, 11.7, 11.7]
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            670 and model_1.getTimeEstimate() < 690)
