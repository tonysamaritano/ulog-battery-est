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

print("Printing data")
battery_model_1.print_data()
print("\nGraphing voltage vs battery percentage")
battery_model_1.graph_voltage_vs_percentage()
print(sys.getsizeof(battery_model_1))