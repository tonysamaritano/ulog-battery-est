# Class model of a standard LiPo battery

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

voltage_log = []  # Log lists
current_log = []
power_log = []
mAh_log = []
wh_log = []
timestamp = []
final_capacity_log = []
final_voltage = 0
minimum_voltage = 0
final_capacity = 0
final_percent = 0
average_current = 0
average_power = 0
average_mAh = 0
average_Wh = 0
frequency = 0
period = 0
temperature = 0
nominal_Ah = 0
nominal_voltage = 0
nominal_mAh = 0
nominal_watt_hours = 0
file = ""


class BatteryModel:
    def __init__(self, nominal_voltage, nominal_mAh, cells, file):
        self.nominal_voltage = nominal_voltage
        self.nominal_mAh = nominal_mAh
        self.cells = cells
        self.file = file
        nominal_Ah = nominal_mAh/1000
        self.retrieve_logs()
        nominal_watt_hours = nominal_voltage * nominal_Ah

    # Retrieve U-Log data from file
    def retrieve_logs():
        log = ulog.ULog(file)  # Parse ULog data
        data = log.data_list  # Compile list of data objects

        # Print Message Names
        for thing in data:
            if thing.name == "Vehicle":
                # Pull voltage logs
                voltage_log = np.array(thing.data["batteryVoltage"])
                # Pull current logs
                current_log = np.array(thing.data["batteryCurrent"])
                current_log = current_log/1000  # Convert to amps
                timestamp = np.array(thing.data["timestamp"])  # Pull time logs
                # Convert to seconds
                timestamp = (timestamp-timestamp[0]) / 1000000

    # Calculate power consumption
    def calculate_power():
        power_log = voltage_log * current_log  # Calculate power consumption

    # Calculate timestamp frequency
    def calculate_frequency():
        frequency = 1/(timestamp[1]-timestamp[0])

    # Calculates watt hours
    def calculate_wh():
        nominal_watt_hours = nominal_Ah*nominal_voltage
        wh_log = [0 for i in range(len(timestamp))]
        for x in range(0, len(wh_log)):
            wh_log[x] = wh_log[x] / frequency / 3600

    # Calculate mAh consumption from current data
    def calculate_mAh():
        mAh_log = [0 for i in range(current_log.size)]

        for x in range(0, current_log.size):
            mAh_log[x] = (current_log[x]/(timestamp[1]-timestamp[0]) /
                          frequency / 3600) * 1000  # Calculate mAh for each

    # Calculate final capacity by decrementing Wh from nominal Wh
    def calculate_final_capacity():
        final_capacity = nominal_watt_hours

        finalCapacityLog = []
        finalCapacityLog = [0 for i in range(timestamp.size)]
        for x in range(0, len(wh_log)):
            final_capacity = final_capacity - wh_log[x]
            final_capacity_log[x] = final_capacity

    # Calculate averages, minimums, and final values of logs
    def calculate_final_stats():
        final_voltage = voltage_log[len(voltage_log)-1]
        minimum_voltage = np.amin(np.array(voltage_log))
        average_current = np.average(np.array(current_log))
        average_Wh = sum(wh_log)/len(wh_log)
        final_percent = int(final_capacity/nominal_watt_hours * 100)
        average_mAh = sum(mAh_log)/len(mAh_log)

    # Scale capacity estimation based on external temperature
    def scale_temperature():
        pass

    # Append new data to end of current lists
    def update_lists():
        pass

    # Print useful information from data collection
    def print_data():
        print("Minimum Voltage: %sV" % minimum_voltage)
        print("Final Voltage: %sV " % final_voltage)
        print("Average Current: %sA" % average_current)
        print("Average mAh: ", average_mAh)
        print("Average Wh: %sWh" % average_Wh)
        print("Final Capacity: %sWh" % final_capacity)
        print("Final Percentage: %d%%" % final_percent)

    # Graphical representation of drone power statistics
    def graph_power_data():
        fig, axs = plt.subplots(2, 2)
        # Set voltage limits, batteries should never drop below 9V, never higher than 13V
        axs[0, 0].set_ylim([9, 13])
        axs[0, 0].set_title('Voltage')
        # Set current axes, tune as needed
        axs[0, 1].set_ylim([0, max(current_log)])
        axs[0, 1].set_title('Current')
        axs[1, 0].set_ylim([0, max(power_log)])
        axs[1, 0].set_title('Power Consumption')
        axs[1, 1].set_ylim([0, max(wh_log)])
        axs[1, 1].set_title('Wh Consumption')

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
        axs[0, 0].plot(timestamp, voltage_log)
        axs[0, 1].plot(timestamp, current_log)
        axs[1, 0].plot(timestamp, power_log)
        axs[1, 1].plot(timestamp, mAh_log)
        plt.show()

    # Generate capacity curve compared to voltage level
    def graph_capacity_data():
        plt.plot(final_capacity_log, voltage_log)
        plt.axis([max(final_capacity_log), min(final_capacity_log),
                 min(voltage_log), max(voltage_log)])
        plt.xlabel("Capacity Wh")
        plt.ylabel("Voltage")
        plt.show()
