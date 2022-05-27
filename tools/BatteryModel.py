# Class model of a standard LiPo battery

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np

class BatteryModel:
    def __init__(self, file, nominal_voltage: float = 11.1, nominal_mAh: float = 5100.0, cells: int = 3):
        # Log Data Inits
        self.__voltage_log = [] 
        self.__current_log = []
        self.__power_log = []
        self.__mAh_log = []
        self.__wh_log = []
        self.__timestamp = []
        self.__final_capacity_log = []
        
        # Givens
        self.__nominal_voltage = nominal_voltage
        self.__cells = cells                      
        self.__nominal_Ah = nominal_mAh/1000.0
        self.__nominal_watt_hours = nominal_voltage * self.__nominal_Ah

        # Attributes
        self.__final_voltage = 0
        self.__minimum_voltage = 0
        self.__final_capacity = 0
        self.__final_percent = 0
        self.__average_current = 0
        self.__average_power = 0
        self.__average_mAh = 0
        self.__average_Wh = 0
        self.__frequency = 0
        self.__period = 0
        self.__temperature = 0
        self.__minimum_cell_voltage = 3
        self.__maximum_cell_voltage = 4.2

        # Calculations and Function Calls
        self.__retrieve_logs(file)
        self.__calculate_power()
        self.__calculate_frequency()
        self.__calculate_wh()
        self.__calculate_mAh()
        self.__calculate_final_capacity()
        self.__calculate_final_stats()

    # Retrieve U-Log data from file
    def __retrieve_logs(self, file):
        log = ulog.ULog(file)  # Parse ULog data
        data = log.data_list  # Compile list of data objects

        # Print Message Names
        for log_message in data:
            if log_message.name == "Vehicle":
                # Pull voltage logs
                self.__voltage_log = np.array(log_message.data["batteryVoltage"])
                # Pull current logs
                self.__current_log = np.array(log_message.data["batteryCurrent"])
                self.__current_log = self.__current_log/1000  # Convert to amps
                self.__timestamp = np.array(log_message.data["timestamp"])  # Pull time logs
                # Convert to seconds
                self.__timestamp = (self.__timestamp-self.__timestamp[0]) / 1e6

    # Calculate power consumption
    def __calculate_power(self):
        self.__power_log = self.__voltage_log * self.__current_log  # Calculate power consumption

    # Calculate timestamp frequency
    def __calculate_frequency(self):
        tmp = np.roll(self.__timestamp, 1)
        tmp[0] = 0
        self.__frequency = 1/(self.__timestamp-tmp)
        print("freq: " + str(self.__frequency))

    # Calculates watt hours
    def __calculate_wh(self):
        self.__nominal_watt_hours = self.__nominal_Ah*self.__nominal_voltage
        self.__wh_log = self.__power_log / self.__frequency / 3600.0

    # Calculate mAh consumption from current data
    def __calculate_mAh(self):
      self.__mAh_log = (self.__current_log / 3600) * 1000  # Calculate mAh for each
       
    # Calculate final capacity by decrementing Wh from nominal Wh
    def __calculate_final_capacity(self):
        self.__final_capacity = self.__nominal_watt_hours

        # finalCapacityLog = []
        self.__final_capacity_log = np.zeros_like(self.__timestamp)
        for x in range(0, len(self.__wh_log)): 
            self.__final_capacity = self.__final_capacity - self.__wh_log[x]
            self.__final_capacity_log[x] = self.__final_capacity

    # Calculate averages, minimums, and final values of logs
    def __calculate_final_stats(self):
        self.__final_voltage = self.__voltage_log[len(self.__voltage_log)-1]
        self.__minimum_voltage = np.amin(np.array(self.__voltage_log))
        self.__average_current = np.average(np.array(self.__current_log))
        self.__average_Wh = sum(self.__wh_log)/len(self.__wh_log)
        self.__final_percent = int(self.__final_capacity/self.__nominal_watt_hours * 100)
        self.__average_mAh = sum(self.__mAh_log)/len(self.__mAh_log)

    # Scale capacity estimation based on external temperature
    def scale_temperature(self):
        pass

    # Append new data to end of current lists
    def update_lists(self):
        pass

    # Print useful information from data collection
    def print_data(self):
        print("Minimum Voltage: %sV" % self.__minimum_voltage)
        print("Final Voltage: %sV " % self.__final_voltage)
        print("Average Current: %sA" % self.__average_current)
        print("Average mAh: ", self.__average_mAh)
        print("Average Wh: %sWh" % self.__average_Wh)
        print("Final Capacity: %sWh" % self.__final_capacity)
        print("Final Percentage: %d%%" % self.__final_percent)

    # Graphical representation of drone power statistics
    def graph_power_data(self):
        fig, axs = plt.subplots(2, 2)
        # Set voltage limits, batteries should never drop below 9V, never higher than 13V
        axs[0, 0].set_ylim([self.__cells * self.__minimum_cell_voltage * .9, self.__cells * self.__maximum_cell_voltage * 1.1])
        axs[0, 0].set_title('Voltage')
        # Set current axes, tune as needed
        axs[0, 1].set_ylim([0, max(self.__current_log)])
        axs[0, 1].set_title('Current')
        axs[1, 0].set_ylim([0, max(self.__power_log)])
        axs[1, 0].set_title('Power Consumption')
        axs[1, 1].set_ylim([0, max(self.__wh_log)])
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
        axs[0, 0].plot(self.__timestamp, self.__voltage_log)
        axs[0, 1].plot(self.__timestamp, self.__current_log)
        axs[1, 0].plot(self.__timestamp, self.__power_log)
        axs[1, 1].plot(self.__timestamp, self.__mAh_log)
        plt.show()

    # Generate capacity curve compared to voltage level
    def graph_capacity_data(self):
        # print(str(self.__final_capacity_log) + "\n")
        # print(str(self.__voltage_log))
        plt.plot(self.__final_capacity_log, self.__voltage_log)
        plt.axis([max(self.__final_capacity_log), min(self.__final_capacity_log),
                 min(self.__voltage_log), max(self.__voltage_log)])
        plt.xlabel("Capacity Wh")
        plt.ylabel("Voltage")
        plt.show()