import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

from BatteryModel import BatteryModel


assert len(sys.argv) > 1, f"No input file specified"  # Verify file provided

print(f"input: {sys.argv[1]}")  # Print file name

# Test 1
print("making battery model object")
battery_model_1 = BatteryModel(11.1, 5100, 3, sys.argv[1])

print("printing data")
battery_model_1.print_data()
print("graphing power data")
battery_model_1.graph_power_data()
print("graphing capacity data")
battery_model_1.graph_capacity_data()