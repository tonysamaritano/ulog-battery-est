from asyncio import format_helpers
import random
import pytest
import numpy as np

from batlib.model import Model
from batlib.model import PolyStruct


def voltage_noise_array(final_value, noise_range, noise_voltage, length):
    """
    Creates an array of random voltages set around a given range of noise 
    at a voltage value.
    After half of the length of the array is reached, the array will start
    to settle around a final voltage value.
    
    :param final_value:     final voltage value to settle to
    :param noise_range:     added noise range to a noise voltage
    :param noise_voltage:   voltage where noise is generated around
    :param length:          length of the data array 
    """
    volt_data = [0 for i in range(0, length-1)]
    volt_data = [(random.uniform(-noise_range, noise_range)+noise_voltage)
                 for i in range(0, int(length/2)-1)]
    for i in range(int(length/2), length-1):
        volt_data.append(final_value)
    return volt_data


def test_model_0():
    """
    This is a test for the functions in the model.py class.
    The voltage data is being initialized with a final settling 
    voltage value of 12.3, noise range of .5, noise voltage value 
    of 11.9 and length of 100
    """
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = voltage_noise_array(12.3, 0.5, 11.9, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1e3, 25)
        print(model_1.getCapacity())
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            1000 and model_1.getTimeEstimate() < 1100)


def test_model_1():
    """
    This is a test for the functions in the model.py class.
    The voltage data is being initialized with a final settling 
    voltage value of 12.1, noise range of .5, noise voltage value 
    of 11.9 and lenght of 200
    """
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    model_1.setArmed(True)
    volt_data = voltage_noise_array(12.1, 0.5, 11.9, 200)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1e3, 25)
        model_1.update(0.05)
    assert (model_1.getTimeEstimate() >
            910 and model_1.getTimeEstimate() < 940)


def test_model_2():
    """
    This is a test for the functions in the model.py class.
    The voltage data is being initialized with a final settling 
    voltage value of 12.5, noise range of 1, noise voltage value 
    of 12.2 and lenght of 100
    """
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    volt_data = voltage_noise_array(12.5, 1, 12.2, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            1120 and model_1.getTimeEstimate() < 1160)


def test_model_3():
    """
    This is a test for the functions in the model.py class.
    The voltage data is being initialized with a final settling 
    voltage value of 11.7, noise range of .5, noise voltage value 
    of 11.9 and lenght of 100
    """
    struct_1 = PolyStruct()
    model_1 = Model(struct_1)
    model_1.setArmed(False)
    volt_data = voltage_noise_array(11.7, 0.5, 11.9, 100)
    for i in range(0, len(volt_data)-1):
        model_1.setInput(volt_data[i], 1000, 25)
        model_1.update(0.25 * 1e6)
    assert (model_1.getTimeEstimate() >
            670 and model_1.getTimeEstimate() < 690)
