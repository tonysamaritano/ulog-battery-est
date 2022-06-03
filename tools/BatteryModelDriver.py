# Driver script for battery model with sample inputs

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

from BatteryModel import BatteryModel

assert len(sys.argv) > 1, f"No input file specified"  # Verify file provided

print(f"input: {sys.argv[1]}")  # Print file name

# Test 1
print("Making battery model object")
battery_model_1 = BatteryModel(sys.argv[1])

print(battery_model_1.simulate(12.3)/60)