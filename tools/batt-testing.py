from asyncio import base_tasks
from json import load
from lib2to3.pgen2.pgen import DFAState
import sys
from time import time
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def plotPowerData():
    """
    Plot relevant power data for battery tests
    """
    fig, axs = plt.subplots(2, 2)
    # Set voltage limits, batteries should never drop below 9V, never higher than 13V
    axs[0, 0].set_ylim([9, 13])
    axs[0, 0].set_title('Voltage')
    # Set current axes, tune as needed
    axs[0, 1].set_ylim([0, np.amax(currentLog)])
    axs[0, 1].set_title('Current')
    axs[1, 0].set_ylim([0, np.amax(powerLog)])
    axs[1, 0].set_title('Power Consumption')
    axs[1, 1].set_ylim([0, np.amax(mAhLog)])
    axs[1, 1].set_title('mAh Consumption')

    axs[0, 0].set(xlabel='Time (s)', ylabel='Voltage')
    axs[0, 1].set(xlabel='Time (s)', ylabel='Current (A)')
    axs[1, 0].set(xlabel='Time (s)', ylabel='Watts')
    axs[1, 1].set(xlabel='Time (s)', ylabel='mAh')

    plt.subplots_adjust(left=0.1,
                        bottom=0.1,
                        right=0.9,
                        top=0.9,
                        wspace=0.4,
                        hspace=0.4)

    # Plot all logs
    axs[0, 0].plot(timestamp, voltageLog)
    axs[0, 1].plot(timestamp, currentLog)
    axs[1, 0].plot(timestamp, powerLog)
    axs[1, 1].plot(timestamp, mAhLog)
    plt.show()


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
    for log_message in data:
        if log_message.name == "Vehicle":
            return np.array(log_message.data["batteryVoltage"]), (np.array(log_message.data["batteryCurrent"])/1000), (np.array(log_message.data["timestamp"]) / 1e6)


def drain_data(vlog, final_mAhlog, mahlog):
    for i in range(0, len(vlog)):
        if(vlog[i] < 11.4):
            print("11.4 iteration time: ", i)
            break
    for i in range(0, len(vlog)):
        if(vlog[i] < 11.1):
            print("11.1 iteration time: ", i)
            break
    print("Voltage full drain iteration time: ", len(vlog))

    for i in range(0, len(final_mAhlog)):
        if(final_mAhlog[i] < 0):
            print("mAh drain to 0 iteration time: ", i)
            break

    print("Total recorded mAh drain: ", sum(mahlog[:22412]))


def print_stats():
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
    print(c, b, a, d)


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
    print(c, b, a, d)


def plot_time_fit():
    """
    Plot estimated time remaining based on percentage of remaining capacity
    """
    plt.plot(mAh_percent_log[start_time:end_time], time_estimation_curve(
        np.array(mAh_percent_log[start_time:end_time])))
    plt.xlabel("Percent Capacity")
    plt.ylabel("Estimated Remaining Seconds")
    plt.title("Percent v Time")
    plt.show()


def plot_percentage_fit():
    """
    Plot estimated percentage from voltage
    """
    plt.plot(voltageLog[start_time:end_time],
             drain_curve_percent(voltageLog[start_time:end_time]))
    plt.xlabel("Voltage")
    plt.ylabel("Estimated Percentage Remaining")
    plt.title("Voltage v Percent")
    plt.show()


def simulate():
    """
    Simulate final time estimation from ULog voltages
    Best estimations from idle batteries
    """
    plt.plot(voltageLog[start_time:end_time], time_estimation_curve(
        drain_curve_percent(voltageLog[start_time:end_time])))
    plt.title("Time Estimation from Voltage")
    plt.xlabel("Voltage")
    plt.ylabel("Time Remaining (s)")
    plt.show()

    print(time_estimation_curve(
        drain_curve_percent(11.46)))


assert len(sys.argv) > 1, f"No input file specified"  # Verify file provided

print(f"input: {sys.argv[1]}")  # Print file name


vlog1, clog1, tstmp1 = pull_logs(sys.argv[1])

if (len(sys.argv) == 3):
    vlog2, clog2, tstmp2 = pull_logs(sys.argv[2])
    if(len(vlog1) > len(vlog2)):
        vlog1 = vlog1[:len(vlog2-1)]
        clog1 = clog1[:len(clog2-1)]
        tstmp1 = tstmp1[:len(tstmp2-1)]
    if(len(vlog2) > len(vlog1)):
        vlog2 = vlog2[:len(vlog1-1)]
        clog2 = clog2[:len(clog1-1)]
        tstmp2 = tstmp2[:len(tstmp1-1)]
    voltageLog = (vlog1 + vlog2)/2
    currentLog = (clog1 + clog2)/2
    timestamp = (tstmp1 + tstmp2)/2
    timestamp = timestamp - timestamp[0]
else:
    voltageLog = vlog1
    currentLog = clog1
    timestamp = tstmp1 - tstmp1[0]

timestampGap = timestamp[1]-timestamp[0]
frequency = 1/timestampGap

mAhLog = []  # Intialize current capacity array
mAhLog = [0 for i in range(currentLog.size)]
for x in range(0, currentLog.size):
    mAhLog[x] = (currentLog[x]*1000)*(timestampGap/3600)

powerLog = voltageLog * currentLog  # Calculate power consumption

# Calculate watt hours
nominalWattHours = 56
wHLog = []
wHLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    wHLog[x] = voltageLog[x] * (mAhLog[x]/1000)

# Find final wH
finalCapacity = nominalWattHours
finalCapacityLog = []
finalCapacityLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    finalCapacity = finalCapacity - wHLog[x]
    finalCapacityLog[x] = finalCapacity

# Final capacity in mAh
nominal_mAh = 8000
finalCapacitymAh = 8000
mAh_percent = 0
capacityAddedmAh = 0
mAh_percent_log = []
mAh_percent_log = [0 for i in range(timestamp.size)]
finalCapacitymAhLog = []
finalCapacitymAhLog = [0 for i in range(timestamp.size)]
for x in range(0, len(finalCapacitymAhLog)):
    capacityAddedmAh = capacityAddedmAh + mAhLog[x]
    mAh_percent_log[x] = 100-(capacityAddedmAh/nominal_mAh*100)
    finalCapacitymAh = finalCapacitymAh - mAhLog[x]

    finalCapacitymAhLog[x] = finalCapacitymAh

minVoltage = np.amin(voltageLog)
meanCurrent = np.average(currentLog)
meanWh = sum(wHLog)/len(wHLog)
wHPercent = int(finalCapacity/nominalWattHours * 100)

start_time = find_motor_start(voltageLog)
end_time = find_full_drain(finalCapacitymAhLog)
load_drop = max(voltageLog)-voltageLog[start_time]

# voltage_to_percent_fit(
#     voltageLog[start_time:end_time]+load_drop, mAh_percent_log[start_time:end_time])

# percent_to_time_fit(
#     mAh_percent_log[start_time:end_time], timestamp[start_time:end_time])

# drain_data(voltageLog[start_time:], finalCapacitymAhLog, mAhLog)
# plotPowerData()  # Plot voltage, current, and power consumption
# print_stats()

# plot_time_fit()
# plot_percentage_fit()
simulate()
