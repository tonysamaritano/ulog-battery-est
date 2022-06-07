from asyncio import format_helpers
import random
import pytest
import numpy as np

from batlib.model import Model
from batlib.model import PolyStruct


def voltage_noise_array(final_value, noise_range, noise_voltage, length):
    volt_data = [0 for i in range(0, length-1)]
    volt_data = [(random.uniform(-noise_range, noise_range)+noise_voltage)
                 for i in range(0, int(length/2)-1)]
    for i in range(int(length/2), length-1):
        volt_data.append(final_value)
    return volt_data


def test_test0():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = voltage_noise_array(12.3, 0.5, 11.9, 100)
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
    volt_data = voltage_noise_array(12.1, 0.5, 11.9, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1e3, 25)
        model_1.update(0.05)
    assert (model_1.getTimeEstimate() >
            910 and model_1.getTimeEstimate() < 940)


def test_test2():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = voltage_noise_array(12.5, 0.5, 12.2, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            1120 and model_1.getTimeEstimate() < 1160)


def test_test3():
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = voltage_noise_array(11.7, 0.5, 11.9, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            670 and model_1.getTimeEstimate() < 690)
