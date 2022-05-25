import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

#Function to organize PyPlot graphs for power data
def plotPowerData():
    fig, axs = plt.subplots(2,2)
    axs[0,0].set_ylim([9, 13]) #Set voltage limits, batteries should never drop below 9V, never higher than 13V
    axs[0,0].set_title('Voltage')
    axs[0,1].set_ylim([0,50])  #Set current axes, tune as needed
    axs[0,1].set_title('Current')
    axs[1,0].set_ylim([0,500])
    axs[1,0].set_title('Power Consumption')
    axs[1,1].set_ylim([0,10000])
    axs[1,1].set_title('mAh Consumption')

    axs[0,0].set(xlabel='Time (s)', ylabel='Voltage')
    axs[0,1].set(xlabel='Time (s)', ylabel='Current (A)')
    axs[1,0].set(xlabel='Time (s)', ylabel='Watts')
    axs[1,1].set(xlabel='Time (s)', ylabel='mAh')

    plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

    #Plot all logs
    axs[0,0].plot(timestamp,voltageLog)
    axs[0,1].plot(timestamp,currentLog)
    axs[1,0].plot(timestamp,powerLog)
    axs[1,1].plot(timestamp,mAhLog)
    plt.show()

assert len(sys.argv) > 1, f"No input file specified" #Verify file provided

print(f"input: {sys.argv[1]}") #Print file name

log = ulog.ULog(sys.argv[1]) #Parse ULog data
data = log.data_list #Compile list of data objects

# Print Message Names
for thing in data:
    if thing.name == "Vehicle":
        voltageLog = np.array(thing.data["batteryVoltage"]) #Pull voltage logs
        currentLog = np.array(thing.data["batteryCurrent"]) #Pull current logs
        currentLog = currentLog/1000 #Convert to amps
        timestamp = np.array(thing.data["timestamp"]) #Pull time logs
        timestamp = (timestamp-timestamp[0]) / 1000000 # Convert to seconds

mAhLog = [] #Intialize current capacity array
mAhLog = [0 for i in range (currentLog.size)]
for x in range(0,currentLog.size):
    mAhLog[x] = (currentLog[x]*((timestamp[1]-timestamp[0])))*1000 #Calculate mAh for each

print(mAhLog) #Print mAh values

powerLog = voltageLog * currentLog #Calculate power consumption

frequency = 4
nominalCapacity = 5100
finalCapacity = nominalCapacity
for x in range(0,len(mAhLog),frequency):
    finalCapacity = finalCapacity - mAhLog[x]

minVoltage = np.amin(voltageLog)
meanCurrent = np.average(currentLog)

print("Final Voltage: %s V" % (minVoltage))
print("Average Current: %s A" % meanCurrent)
print("Average mAh: ",sum(mAhLog)/len(mAhLog))
print("Final Capacity: ", finalCapacity)

plotPowerData() #Plot voltage, current, and power consumption