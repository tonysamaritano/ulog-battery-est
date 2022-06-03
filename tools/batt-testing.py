from asyncio import base_tasks
from json import load
from lib2to3.pgen2.pgen import DFAState
import sys
from time import time
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def equation(x, a, b, c, d):
    """
    Format of general 3rd order polynomial used for curve fitting

    :param x: independent variable
    :param a: 1st degree coefficient
    :param b: 2nd degree coefficient
    :param c: 3rd degree coefficient
    :param d: constant coefficient
    :return: equation format for 3rd order polynomial
    """
    return (a * x) + (b * x**2) + (c * x**3) + d


def pull_logs(file):
    """
    Pull and parse ULog data from drone SD

    :param file: path to .ulog file
    :return voltage, current, time: all necessary power draw data in numpy array format
    """
    log = ulog.ULog(sys.argv[1])  # Parse ULog data
    data = log.data_list  # Compile list of data objects
    for thing in data:
        if thing.name == "Vehicle":
            return np.array(thing.data["batteryVoltage"]), (np.array(thing.data["batteryCurrent"])/1000), (np.array(thing.data["timestamp"]) / 1e6)

    """
    Print stats for analysis
    """
    print("Final Voltage: %sV " % (voltageLog[voltageLog.size-1]))
    print("Maximum Voltage: %sV" % (voltageLog[0]))
    print("Minimum Voltage: %sV" % (minVoltage))
    print("Average Current: %sA" % meanCurrent)
    print("Average mAh: ", sum(mAhLog)/len(mAhLog))
    print("Final Capacity (mAh) %s" % (nominal_mAh-capacityAddedmAh))
    print("Average Wh: %sWh" % meanWh)
    print("Final Capacity: %sWh" % finalCapacity)
    print("Final Percentage: %d%%" % mAh_percent_log[len(mAh_percent_log)-1])


def find_motor_start(v_log):
    """
    Find the voltage level after the initial drop at motor turn on

    :param v_log: log of voltage data
    :return i: index of motor start
    """
    for i in range(0, len(v_log)):
        if(i == len(v_log)-1):
            return 0
        else:
            if(v_log[i+1]-v_log[i] > 0.05):
                return i+5  # Offset to account for sharp rise


def find_full_drain(cap_log):
    """
    Find the index when mAh capacity equals 0

    :param cap_log: log of mAh data
    :return i: index of full mAh drain
    """
    for i in range(0, len(cap_log)-1):
        if(i == len(cap_log)):
            break
        else:
            if(cap_log[i] <= 0):
                return i


def mAh_data(mAh_log, timestamp, nominal_mAh):
    """
    mAh data for provided ULog files

    :param mAh_log: list of mAh data
    :param timestamp: time data of ULog file
    :param nominal_mAh: nominal capacity value of battery

    :return final_capacity_log: list of final capacity values decrementing
    :return mAh_percent_log: list of final capacity values as percentages
    """
    finalCapacitymAh = nominal_mAh
    capacityAddedmAh = 0
    mAh_percent_log = []
    mAh_percent_log = [0 for i in range(timestamp.size)]
    final_capacity_log = []
    final_capacity_log = [0 for i in range(timestamp.size)]
    for x in range(0, len(final_capacity_log)-1):
        capacityAddedmAh = capacityAddedmAh + mAh_log[x]
        mAh_percent_log[x] = 100-(capacityAddedmAh/nominal_mAh*100)
        finalCapacitymAh = finalCapacitymAh - mAh_log[x]
        final_capacity_log[x] = finalCapacitymAh
    return final_capacity_log, mAh_percent_log


def drain_curve_percent(x):
    return 58.821010559671066*x**3 + -2134.5758966115527*x**2 + 25869.660996405204*x + -104622.36370746762


def time_estimation_curve(x):
    return 0.00031623534490089853*x**3 + -0.06535263801996286*x**2 + 15.21882160202914*x + -32.77764056651616


def voltage_to_percent_fit(v_log, cap_log):
    """
    Generate a prediction curve of percent capacity from voltage

    :param v_log: log of voltage data
    :param cap_log: log of capacity data, should be in percent
    :return: list, calculated values
    """
    # Scipy curve fitting
    popt, _ = curve_fit(
        equation, v_log, cap_log)
    a, b, c, d = popt
    # return list of fit line data
    print("Voltage->Percent Polynomial: ", c, b, a, d)


def percent_to_time_fit(percent_log, time_log):
    """
    Take a percentage of capacity and estimate a time remaining

    :param percent_log: log of percentage values retrieved from a percentage curve fit
    :param time_log:    log of time for full battery drain, preferably at 30A
    """

    time_log = time_log-time_log[0]
    # Offset to 0, swap so higher capacity is at lower time
    time_log = time_log[len(time_log)-1]-time_log
    popt, _ = curve_fit(equation, percent_log, time_log)
    a, b, c, d = popt
    print("Percent->Time Polynomial: ", c, b, a, d)


def simulate(voltage):
    """
    Simulate final time estimation from ULog voltages
    Best estimations from idle batteries

    :param voltage: voltage value
    :return: estimated time remaining in seconds
    """

    return time_estimation_curve(drain_curve_percent(voltage))


# Verify file provided
assert len(sys.argv) > 2, f"Expected <1C ULog> <30A ULog>"

print(f"1C ULog: {sys.argv[1]} 30A ULog: {sys.argv[2]}")  # Print both files

voltage_log_1C, current_log_1C, timestamp_1C = pull_logs(sys.argv[1])
voltage_log_30A, current_log_30A, timestamp_30A = pull_logs(sys.argv[2])

period_1C = timestamp_1C[1]-timestamp_1C[0]
period_30A = timestamp_30A[1]-timestamp_30A[0]

mAh_log_1C = []  # Intialize current capacity array
mAh_log_1C = (current_log_1C*1000)*(period_1C/3600)

mAh_log_30A = []
mAh_log_30A = (current_log_30A*1000)*(period_30A/3600)

# Get mAh data
final_capacity_1C, final_percent_1C = mAh_data(mAh_log_1C, timestamp_1C, 8500)
final_capacity_30A, final_percent_30A = mAh_data(
    mAh_log_30A, timestamp_30A, 8500)

# Find adequate start and end times for curve fitting
start_time_1C = find_motor_start(voltage_log_1C)
end_time_1C = find_full_drain(final_capacity_1C)
load_drop_1C = max(voltage_log_1C)-voltage_log_1C[start_time_1C]

start_time_30A = find_motor_start(voltage_log_30A)
end_time_30A = find_full_drain(final_capacity_30A)
load_drop_30A = max(voltage_log_30A)-voltage_log_30A[start_time_30A]

# Generate voltage v percent based on 1C draw
voltage_to_percent_fit(
    voltage_log_1C[start_time_1C:end_time_1C]+load_drop_1C, final_percent_1C[start_time_1C:end_time_1C])

# Generate percent v time based on 30A hover draw
percent_to_time_fit(
    final_percent_30A[start_time_30A:end_time_30A], timestamp_30A[start_time_30A:end_time_30A])
