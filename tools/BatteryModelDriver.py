# Driver script for battery model with sample inputs

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

from BatteryModel import BatteryModel

assert len(sys.argv) == 2, f"No input voltage specified"
try:
    voltage = float(sys.argv[1])
except ValueError:
    assert False, f"Input {sys.argv[1]} not a float"

battery_model_1 = BatteryModel()
print(battery_model_1.simulate(voltage))
