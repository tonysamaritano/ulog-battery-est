# Class model of a standard LiPo battery

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np


# Testing Purposes
# final_voltage = 0
# minimum_voltage = 0
# final_capacity = 0
# final_percent = 0
# average_current = 0
# average_power = 0
# average_mAh = 0
# average_Wh = 0
# frequency = 0
# period = 0
# temperature = 0
# nominal_Ah = 0
# nominal_voltage = 0
# nominal_mAh = 0
# nominal_watt_hours = 0
# file = ""


class BatteryModel:
    def __init__(self, nominal_voltage, nominal_mAh, cells, file):
        # Log Data Inits
        self.voltage_log = [] 
        self.current_log = []
        self.power_log = []
        self.mAh_log = []
        self.wh_log = []
        self.timestamp = []
        self.final_capacity_log = []
        
        # Givens
        self.nominal_voltage = nominal_voltage
        # self.nominal_mAh = nominal_mAh
        self.cells = cells                      
        self.file = file
        self.nominal_Ah = nominal_mAh/1000.0
        self.nominal_watt_hours = nominal_voltage * self.nominal_Ah

        # Attributes
        self.final_voltage = 0
        self.minimum_voltage = 0
        self.final_capacity = 0
        self.final_percent = 0
        self.average_current = 0
        self.average_power = 0
        self.average_mAh = 0
        self.average_Wh = 0
        self.frequency = 0
        self.period = 0
        self.temperature = 0

        # Calculations and Function Calls
        self.__retrieve_logs()
        self.__calculate_power()
        self.__calculate_frequency()
        self.__calculate_wh()
        self.__calculate_mAh()
        self.__calculate_final_capacity()
        self.__calculate_final_stats()

    # Retrieve U-Log data from file
    def __retrieve_logs(self):
        log = ulog.ULog(self.file)  # Parse ULog data
        data = log.data_list  # Compile list of data objects

        # Print Message Names
        for thing in data:
            if thing.name == "Vehicle":
                # Pull voltage logs
                self.voltage_log = np.array(thing.data["batteryVoltage"])
                # Pull current logs
                self.current_log = np.array(thing.data["batteryCurrent"])
                self.current_log = self.current_log/1000  # Convert to amps
                self.timestamp = np.array(thing.data["timestamp"])  # Pull time logs
                # Convert to seconds
                self.timestamp = (self.timestamp-self.timestamp[0]) / 1000000

    # Calculate power consumption
    def __calculate_power(self):
        self.power_log = self.voltage_log * self.current_log  # Calculate power consumption

    # Calculate timestamp frequency
    def __calculate_frequency(self):
        self.frequency = 1/(self.timestamp[1]-self.timestamp[0])

    # Calculates watt hours
    def __calculate_wh(self):
        self.nominal_watt_hours = self.nominal_Ah*self.nominal_voltage
        self.wh_log = [0 for i in range(len(self.timestamp))]
        for x in range(0, len(self.wh_log)):
            self.wh_log[x] = self.power_log[x] / self.frequency / 3600.0

    # Calculate mAh consumption from current data
    def __calculate_mAh(self):
        self.mAh_log = [0 for i in range(self.current_log.size)]

        for x in range(0, self.current_log.size):
            self.mAh_log[x] = (self.current_log[x]/(self.timestamp[1]-self.timestamp[0]) /
                          self.frequency / 3600) * 1000  # Calculate mAh for each

    # Calculate final capacity by decrementing Wh from nominal Wh
    def __calculate_final_capacity(self):
        self.final_capacity = self.nominal_watt_hours

        # finalCapacityLog = []
        self.final_capacity_log = [0 for i in range(self.timestamp.size)]
        for x in range(0, len(self.wh_log)): 
            self.final_capacity = self.final_capacity - self.wh_log[x]
            self.final_capacity_log[x] = self.final_capacity

    # Calculate averages, minimums, and final values of logs
    def __calculate_final_stats(self):
        self.final_voltage = self.voltage_log[len(self.voltage_log)-1]
        self.minimum_voltage = np.amin(np.array(self.voltage_log))
        self.average_current = np.average(np.array(self.current_log))
        self.average_Wh = sum(self.wh_log)/len(self.wh_log)
        self.final_percent = int(self.final_capacity/self.nominal_watt_hours * 100)
        self.average_mAh = sum(self.mAh_log)/len(self.mAh_log)

    # Scale capacity estimation based on external temperature
    def scale_temperature(self):
        pass

    # Append new data to end of current lists
    def update_lists(self):
        pass

    # Print useful information from data collection
    def print_data(self):
        print("Minimum Voltage: %sV" % self.minimum_voltage)
        print("Final Voltage: %sV " % self.final_voltage)
        print("Average Current: %sA" % self.average_current)
        print("Average mAh: ", self.average_mAh)
        print("Average Wh: %sWh" % self.average_Wh)
        print("Final Capacity: %sWh" % self.final_capacity)
        print("Final Percentage: %d%%" % self.final_percent)

    # Graphical representation of drone power statistics
    def graph_power_data(self):
        fig, axs = plt.subplots(2, 2)
        # Set voltage limits, batteries should never drop below 9V, never higher than 13V
        axs[0, 0].set_ylim([9, 13])
        axs[0, 0].set_title('Voltage')
        # Set current axes, tune as needed
        axs[0, 1].set_ylim([0, max(self.current_log)])
        axs[0, 1].set_title('Current')
        axs[1, 0].set_ylim([0, max(self.power_log)])
        axs[1, 0].set_title('Power Consumption')
        axs[1, 1].set_ylim([0, max(self.wh_log)])
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
        axs[0, 0].plot(self.timestamp, self.voltage_log)
        axs[0, 1].plot(self.timestamp, self.current_log)
        axs[1, 0].plot(self.timestamp, self.power_log)
        axs[1, 1].plot(self.timestamp, self.mAh_log)
        plt.show()

    # Generate capacity curve compared to voltage level
    def graph_capacity_data(self):
        # print(str(self.final_capacity_log) + "\n")
        # print(str(self.voltage_log))
        plt.plot(self.final_capacity_log, self.voltage_log)
        plt.axis([max(self.final_capacity_log), min(self.final_capacity_log),
                 min(self.voltage_log), max(self.voltage_log)])
        plt.xlabel("Capacity Wh")
        plt.ylabel("Voltage")
        plt.show()