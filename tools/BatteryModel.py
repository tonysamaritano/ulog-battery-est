# Class model of a standard LiPo battery

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

class BatteryModel:
    def __init__(self, file, nominal_voltage: float = 11.1, nominal_mAh: float = 5100.0, cells: int = 3):
        # Log Data Inits
        self.__voltage_log = [] 
        self.__current_log = []
        self.__mAh_log = []
        self.__timestamp = []
        self.__final_capacity_log = []
        self.__mAh_percent_log = []
        self.__samplerate = []
        
        # Givens
        # self.__nominal_voltage = nominal_voltage
        self.__cells = cells                      
        self.__nominal_Ah = nominal_mAh/1000.0

        # Attributes
        self.__final_voltage = 0
        self.__minimum_voltage = 0
        self.__final_capacity = 0
        self.__final_percent = 0
        self.__average_current = 0
        self.__average_mAh = 0
        self.__average_Wh = 0
        self.__frequency = 0
        self.__period = 0
        self.__temperature = 0
        self.__minimum_cell_voltage = 3
        self.__maximum_cell_voltage = 4.2

        # Calculations and Function Calls
        self.__retrieve_logs(file)
        self.__calculate_samplerate()
        self.__calculate_mAh()
        self.__calculate_mAh_percent(nominal_mAh)
        self.__calculate_final_capacity(nominal_mAh)
        self.__calculate_final_stats()

    # Retrieve U-Log data from file
    def __retrieve_logs(self, file):
        """
        Pull and parse ULog data from drone SD

        :param file: path to .ulog file
        :return voltage, current, time: all necessary power draw data in numpy array format
        """
        # Print Message Names
        log = ulog.ULog(sys.argv[1])  # Parse ULog data
        data = log.data_list  # Compile list of data objects
        for log_message in data:
            if log_message.name == "Vehicle":
                return np.array(log_message.data["batteryVoltage"]), (np.array(log_message.data["batteryCurrent"])/1000), (np.array(log_message.data["timestamp"]) / 1e6)

    # Calculate timestamp frequency
    def __calculate_samplerate(self):
        tmp = np.roll(self.__timestamp, 1)
        tmp[0] = 0
        self.__samplerate  = self.__timestamp-tmp

    # Calculate mAh consumption from current data
    def __calculate_mAh(self):
      self.__mAh_log = ((self.__current_log*1000) * (0.25/3600))  # Calculate mAh for each
       
    # Calculate final capacity by decrementing Wh from nominal Wh
    def __calculate_final_capacity(self, nominal_mAh):
        self.__final_capacity = nominal_mAh

        # finalCapacityLog = []
        self.__final_capacity_log = np.zeros_like(self.__timestamp)
        for x in range(0, len(self.__mAh_log)): 
            self.__final_capacity = self.__final_capacity - self.__mAh_log[x]
            self.__final_capacity_log[x] = self.__final_capacity

    # Calculate mAh percent log 
    def __calculate_mAh_percent(self, nominal_mAh):
        capacity_added_mAh = 0
        self.__mAh_percent_log = np.zeros_like(self.__timestamp)
        for x in range(0, len(self.__mAh_log)):
            capacity_added_mAh = capacity_added_mAh + self.__mAh_log[x]
            self.__mAh_percent_log[x] = 100-(capacity_added_mAh/nominal_mAh*100)


    # Calculate averages, minimums, and final values of logs
    def __calculate_final_stats(self):
        self.__final_voltage = self.__voltage_log[len(self.__voltage_log)-1]
        self.__minimum_voltage = np.amin(np.array(self.__voltage_log))
        self.__average_current = np.average(np.array(self.__current_log))
        self.__final_percent = int(self.__final_capacity/self.__nominal_Ah/1000 * 100)
        self.__average_mAh = sum(self.__mAh_log)/len(self.__mAh_log)

    # Helper function to find the start voltage of the log data
    # for graphing purposes
    def __find_start_voltage(self):
        """Return the voltage from where the battery is first used"""
        for i in range(0, len(self.__voltage_log)-1):
            if((self.__voltage_log[i] - self.__voltage_log[i+1]) > 0.05):
                return self.__voltage_log[i + 5]
        return self.__voltage_log[0]

    # Helper function to find the end voltage when the battery is stopped 
    # or reaches 0% charge for graphing 
    def __find_stop_voltage(self):
        """Return the voltage from where the battery is stopped
        
        If an index was found where the percentage dropped below zero 
        return the related voltage with the associated 
        index with an offset
        else return the position of the minimum current percentage
        """
        stop_index = 0
        try:
            stop_index = np.where(self.__mAh_percent_log < 0)[0][0]
        except:
            stop_index = np.where(self.__mAh_percent_log == np.amin(self.__mAh_percent_log))[0][0]
        return self.__voltage_log[stop_index]      

    def __objective(self, x, a, b, c, d):
        """
        Format of general 3rd order polynomial used for curve fitting

        :param x: independent variable
        :param a: 1st degree coefficient
        :param b: 2nd degree coefficient
        :param c: 3rd degree coefficient
        :param d: constant coefficient
        :return: equation format for 3rd order polynomial
        """
        return (a * np.array(x)) + (b * np.array(x)**2) + (c * np.array(x)**3) + d
    
    
    
    # NOTE: These two helper functions are most likely 
    # can be done better and make more sense by using 
    # the popt for each of ths
    # curve fit objective with precalculated parameters
    # for the capacity vs voltage graph
    def __capacity_objective(self, x):
        return (1.33125743e-04*x) +  (6.76370845e-09*x**2) + (1.20037955e-12*x**3) + 1.13612003e+01

    # curve fit objective with precalculated parameters
    # for the current percentage vs voltage graph
    def __mAh_percentage_objective(self, x):
        return (6.78941291e-03*x) + (1.75924048e-05*x**2) + (1.59231555e-07*x**3) + 1.13612003e+01
    
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
        print("Final Capacity: %sWh" % self.__final_capacity)
        print("Final Percentage: %d%%" % self.__final_percent)

    # Graph voltage vs battery percentage 
    def graph_voltage_vs_percentage(self):
        # print(str(self.__mAh_percentage_objective(0)) + " volts")
        print("Start voltage: " + str(self.__find_start_voltage()))
        print("Stop voltage: " + str(self.__find_stop_voltage()))
        indices = np.where((self.__voltage_log < self.__find_start_voltage()) &
                           (self.__voltage_log >= self.__find_stop_voltage())) 
        # get curve fit
        popt, _ = curve_fit(
            f = self.__objective,
            xdata = self.__mAh_percent_log[indices],
            ydata = self.__voltage_log[indices])
        # parameters for curve fit objective
        a, b, c, d = popt
        plt.plot(self.__mAh_percent_log[indices], self.__voltage_log[indices])
        y_line = self.__objective(self.__mAh_percent_log[indices], a, b, c, d)
        plt.axis([max(self.__mAh_percent_log[indices]), min(self.__mAh_percent_log[indices]),
                 min(self.__voltage_log[indices]), max(self.__voltage_log[indices])])
        plt.plot(self.__mAh_percent_log[indices], y_line, '--', color='red')
        plt.xlabel("mAh Percentage")
        plt.ylabel("Voltage")
        plt.show()