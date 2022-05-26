import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

# Function to organize PyPlot graphs for power data


def plotPowerData():
    fig, axs = plt.subplots(2, 2)
    # Set voltage limits, batteries should never drop below 9V, never higher than 13V
    axs[0, 0].set_ylim([9, 13])
    axs[0, 0].set_title('Voltage')
    axs[0, 1].set_ylim([0, 50])  # Set current axes, tune as needed
    axs[0, 1].set_title('Current')
    axs[1, 0].set_ylim([0, 500])
    axs[1, 0].set_title('Power Consumption')
    axs[1, 1].set_ylim([0, 10000])
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
        timestamp = (timestamp-timestamp[0]) / 1000000  # Convert to seconds

timestampGap = timestamp[1]-timestamp[0]
frequency = 1/timestampGap

mAhLog = []  # Intialize current capacity array
mAhLog = [0 for i in range(currentLog.size)]
for x in range(0, currentLog.size):
    mAhLog[x] = (currentLog[x]/(timestampGap) /
                 frequency / 3600) * 1000  # Calculate mAh for each

powerLog = voltageLog * currentLog  # Calculate power consumption

# Calculate watt hours
nominalWattHours = 56
wHLog = []
wHLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    wHLog[x] = powerLog[x] / frequency / 3600

print(np.sum(wHLog))

# Find final wH
finalCapacity = nominalWattHours
finalCapacityLog = []
finalCapacityLog = [0 for i in range(timestamp.size)]
for x in range(0, len(wHLog)):
    finalCapacity = finalCapacity - wHLog[x]
    finalCapacityLog[x] = finalCapacity

# nominalCapacity = 5100
# finalCapacity = nominalCapacity
# for x in range(0, len(mAhLog), int(frequency)):
#     finalCapacity = finalCapacity - mAhLog[x]

minVoltage = np.amin(voltageLog)
meanCurrent = np.average(currentLog)
meanWh = sum(wHLog)/len(wHLog)
wHPercent = int(finalCapacity/nominalWattHours * 100)

print("Final Voltage: %sV " % (voltageLog[voltageLog.size-1]))
print("Minimum Voltage: %sV" % (minVoltage))
print("Average Current: %sA" % meanCurrent)
print("Average mAh: ", sum(mAhLog)/len(mAhLog))
print("Average Wh: %sWh" % meanWh)
print("Final Capacity: %sWh" % finalCapacity)
print("Final Percentage: %d%%" % wHPercent)

# plt.plot(timestamp, wHLog)
# plt.show()

# plt.plot(finalCapacityLog, voltageLog)
# plt.axis([max(finalCapacityLog), min(finalCapacityLog),
#          min(voltageLog), max(voltageLog)])
# plt.show()

plotPowerData()  # Plot voltage, current, and power consumption
