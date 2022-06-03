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
        self.__power_log = []
        self.__mAh_log = []
        self.__wh_log = []
        self.__timestamp = []
        self.__final_capacity_log = []
        self.__mAh_percent_log = []
        self.__samplerate = []
        
        # Givens
        self.__nominal_voltage = nominal_voltage
        self.__cells = cells                      
        self.__nominal_Ah = nominal_mAh/1000.0

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
        self.__calculate_samplerate()
        self.__calculate_wh()
        self.__calculate_mAh()
        self.__calculate_mAh_percent(nominal_mAh)
        self.__calculate_final_capacity(nominal_mAh)
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
    def __calculate_samplerate(self):
        tmp = np.roll(self.__timestamp, 1)
        tmp[0] = 0
        self.__samplerate  = self.__timestamp-tmp

    # Calculates watt hours
    def __calculate_wh(self):
        self.__wh_log = self.__power_log * self.__samplerate / 3600.0

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
        self.__average_Wh = sum(self.__wh_log)/len(self.__wh_log)
        self.__final_percent = int(self.__final_capacity/self.__nominal_Ah/1000 * 100)
        self.__average_mAh = sum(self.__mAh_log)/len(self.__mAh_log)

    def __find_start_voltage(self):
        """Return the voltage from where the battery is first used"""
        for i in range(0, len(self.__voltage_log)-1):
            if((self.__voltage_log[i] - self.__voltage_log[i+1]) > 0.05):
                return self.__voltage_log[i + 5]
        return self.__voltage_log[0]

    def __find_stop_voltage(self):
        """Return the voltage from where the battery is stopped
        
        If an index was found where the percentage dropped below zero 
        return the related voltage with the associated 
        index with an offset
        else return the position of the minimum current percentage
        """
        stop_index = np.where(self.__mAh_percent_log < 0)[0][0]
        if(not(stop_index > 0)):
            stop_index = self.__mAh_percent_log.index(min(self.__mAh_percent_log))
        return self.__voltage_log[stop_index + 5]
        
        
        

    # Curve fitting objective function
    def __objective(self, x, a, b, c, d):
        # return a * arctan(b*np.array(x)) + c
        return (a * np.array(x)) + (b * np.array(x)**2) + (c * np.array(x)**3) + d

    # Temporary helper method to find the voltage value at 
    # a given value for a generated curve fit model
    # using the pre-calculated parameters from that curve fit
    # Testing purposes only
    def __get_voltage_at_value(self, objective,
                               value, popt):
        return objective(value)
    
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
        print(max(self.__mAh_log))
        print(max(self.__wh_log))
        # NOTE max(mAh_log) was wh_log before change. 
        # mAh log's max: 0.13333334
        # wh log's max: 0.0016849361571670688
        axs[1, 1].set_ylim([0, max(self.__mAh_log)]) 
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
        # index to avoid cut offs in the graph
        print("Start voltage " + str(self.__find_start_voltage()))
        stop_index= np.where(self.__mAh_percent_log < 0)[0][0]
        indices = np.where((self.__voltage_log < self.__find_start_voltage()) & (self.__voltage_log > self.__voltage_log[stop_index]))
         # get curve fit
        popt, _ = curve_fit(f = self.__objective,
                            xdata = self.__final_capacity_log[indices],
                            ydata = self.__voltage_log[indices])
        print(popt)
        a, b, c, d = popt
        plt.plot(self.__final_capacity_log[indices], self.__voltage_log[indices])
        y_line = self.__objective(self.__final_capacity_log[indices], a, b, c, d)
        print(y_line)
        plt.axis([max(self.__final_capacity_log[indices]), min(self.__final_capacity_log[indices]),
                 min(self.__voltage_log[indices]), max(self.__voltage_log[indices])])
        plt.plot(self.__final_capacity_log[indices], y_line, '--', color='red')
        plt.xlabel("Capacity mAh")
        plt.ylabel("Voltage")
        plt.show()

    # Graph voltage vs battery percentage 
    def graph_voltage_vs_percentage(self):
        # print(str(self.__mAh_percentage_objective(0)) + " volts")
        print("Start voltage: " + str(self.__find_start_voltage()))
        print("This is the percnet log")
        print(self.__mAh_percent_log)
        print("This is the end of the percent log")
        print(np.where(self.__mAh_percent_log < 0))
        stop_index= np.where(self.__mAh_percent_log < 0)[0][0]
        # print(str(type(stop_indices)))
        # stop_index = stop_indices[0][0]
        print("Stop index: " + str(stop_index))
        print("Stop voltage: " + str(self.__voltage_log[stop_index]))
        # print(str(stop_index) + " is the index")
        indices = np.where((self.__voltage_log < self.__find_start_voltage()) &
                           (self.__voltage_log >= self.__voltage_log[stop_index])) 
        # get curve fit
        popt, _ = curve_fit(
            f = self.__objective,
            xdata = self.__mAh_percent_log[indices],
            ydata = self.__voltage_log[indices])
        # parameters for curve fit objective
        a, b, c, d = popt
        # NOTE random prints that should be deleted
        print(self.__mAh_percent_log)
     
        
        plt.plot(self.__mAh_percent_log[indices], self.__voltage_log[indices])
        y_line = self.__objective(self.__mAh_percent_log[indices], a, b, c, d)
        print(y_line)
        plt.axis([max(self.__mAh_percent_log[indices]), min(self.__mAh_percent_log[indices]),
                 min(self.__voltage_log[indices]), max(self.__voltage_log[indices])])
        plt.plot(self.__mAh_percent_log[indices], y_line, '--', color='red')
        plt.xlabel("mAh Percentage")
        plt.ylabel("Voltage")
        plt.show()