from asyncio import base_tasks
from json import load
from lib2to3.pgen2.pgen import DFAState
import sys
from time import time
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import argparse


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
    log = ulog.ULog(file)  # Parse ULog data
    data = log.data_list  # Compile list of data objects
    for log_message in data:
        if log_message.name == "Vehicle":
            return np.array(log_message.data["batteryVoltage"]), (np.array(log_message.data["batteryCurrent"])/1000), (np.array(log_message.data["timestamp"]) / 1e6)


def find_motor_start(v_log):
    """
    Find the voltage level after the initial drop at motor turn on

    :param v_log: log of voltage data
    :return i: index of motor start
    """
    for i in range(0, len(v_log)-1):
        if((v_log[i] - v_log[i+1]) > 0.05):
            return i + 5
    return 0


def find_full_drain(cap_log):
    """
    Find the index when mAh capacity equals 0

    :param cap_log: log of mAh data
    :return i: index of full mAh drain
    """
    for i in range(0, len(cap_log)-1):
        if(cap_log[i] <= 0):
            return i
    return len(cap_log)-1


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


parser = argparse.ArgumentParser()

parser.add_argument(
    "-o", "--one-c", help="ulog file at 1C drain", nargs="?", default=".\\data\\reference_1c.ulog")
parser.add_argument("-t", "--thirty-amp", help="ulog at 30A drain",
                    nargs="?", default=".\\data\\reference_30A.ulog")
parser.add_argument("-c", "--capacity", nargs="?", type=float,
                    default="8500.0", help="set nominal charge capacity")

args = parser.parse_args()

print(f"1C ULog: {args.one_c} 30A ULog: {args.thirty_amp}")  # Print both files

voltage_log_1C, current_log_1C, timestamp_1C = pull_logs(args.one_c)
voltage_log_30A, current_log_30A, timestamp_30A = pull_logs(args.thirty_amp)

period_1C = timestamp_1C[1]-timestamp_1C[0]
period_30A = timestamp_30A[1]-timestamp_30A[0]

mAh_log_1C = []  # Intialize current capacity array
mAh_log_1C = (current_log_1C*1000)*(period_1C/3600)

mAh_log_30A = []
mAh_log_30A = (current_log_30A*1000)*(period_30A/3600)

# Get mAh data
final_capacity_1C, final_percent_1C = mAh_data(
    mAh_log_1C, timestamp_1C, args.capacity)
final_capacity_30A, final_percent_30A = mAh_data(
    mAh_log_30A, timestamp_30A, args.capacity)

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
