import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Function to organize PyPlot graphs for power data


def plotPowerData():
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


# define the true objective function
def objective(x, a, b, c, d):
    return (a * x) + (b * x**2) + (c * x**3) + d


assert len(sys.argv) > 1, f"No input file specified"  # Verify file provided

print(f"input: {sys.argv[1]}")  # Print file name

log = ulog.ULog(sys.argv[1])  # Parse ULog data
data = log.data_list  # Compile list of data objects

# Print Message Names
for thing in data:
    if thing.name == "Vehicle":
        # Pull voltage logs
        voltageLog = np.array(thing.data["batteryVoltage"])
        # Pull current logs
        currentLog = np.array(thing.data["batteryCurrent"])
        currentLog = currentLog/1000  # Convert to amps
        timestamp = np.array(thing.data["timestamp"])  # Pull time logs
        timestamp = (timestamp-timestamp[0]) / 1e6  # Convert to seconds

timestampGap = timestamp[1]-timestamp[0]
frequency = 1/timestampGap

mAhLog = []  # Intialize current capacity array
mAhLog = [0 for i in range(currentLog.size)]
for x in range(0, currentLog.size):
    # mAhLog[x] = (currentLog[x]/(timestampGap) /
    #              frequency / 3600) * 1000  # Calculate mAh for each
    mAhLog[x] = (currentLog[x]*1000)*(timestampGap/3600)

powerLog = voltageLog * currentLog  # Calculate power consumption

# Calculate watt hours
nominalWattHours = 56
wHLog = []
wHLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    # wHLog[x] = powerLog[x] / frequency / 3600
    # wHLog[x] = powerLog[x] * (timestampGap/3600)
    wHLog[x] = voltageLog[x] * (mAhLog[x]/1000)

# Find final wH
finalCapacity = nominalWattHours
finalCapacityLog = []
finalCapacityLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    finalCapacity = finalCapacity - wHLog[x]
    finalCapacityLog[x] = finalCapacity

# Final capacity in mAh
nominal_mAh = 5100
finalCapacitymAh = 5100
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


# nominalCapacity = 5100
# finalCapacity = nominalCapacity
# for x in range(0, len(mAhLog), int(frequency)):
#     finalCapacity = finalCapacity - mAhLog[x]

minVoltage = np.amin(voltageLog)
meanCurrent = np.average(currentLog)
meanWh = sum(wHLog)/len(wHLog)
wHPercent = int(finalCapacity/nominalWattHours * 100)

# print("Final Voltage: %sV " % (voltageLog[voltageLog.size-1]))
# print("Maximum Voltage: %sV" % (voltageLog[0]))
# print("Minimum Voltage: %sV" % (minVoltage))
# print("Average Current: %sA" % meanCurrent)
# print("Average mAh: ", sum(mAhLog)/len(mAhLog))
# print("Final Capacity (mAh) %s" % (nominal_mAh-capacityAddedmAh))
# print("Average Wh: %sWh" % meanWh)
# print("Final Capacity: %sWh" % finalCapacity)
# print("Final Percentage: %d%%" % mAh_percent_log[len(mAh_percent_log)-1])

# plt.plot(timestamp, wHLog)
# plt.show()

# plt.plot(finalCapacityLog, voltageLog)
# plt.axis([56, 0,
#          10, 13])
# plt.show()

# plt.plot(mAh_percent_log, voltageLog)
# plt.axis([100, 0, 10, 12.6])
# plt.show()

plotPowerData()  # Plot voltage, current, and power consumption

test_log = voltageLog[200:12886]
print(test_log)

# # Scipy curve fitting
# popt, _ = curve_fit(objective, voltageLog, mAh_percent_log)
# a, b, c, d = popt
# # calculate the output for the range
# plt.plot(voltageLog, mAh_percent_log)
# y_line = objective(voltageLog, a, b, c, d)
# print(objective(11.9, a, b, c, d))
# plt.plot(voltageLog, y_line, '--', color='red')
# plt.show()
