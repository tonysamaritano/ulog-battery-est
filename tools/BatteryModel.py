# Class model of a standard LiPo battery

import sys
import pyulog as ulog
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

class BatteryModel:
    def __init__(self, file, nominal_voltage: float = 11.1, nominal_mAh: float = 5100.0, cells: int = 3):
   
        # Givens
        # self.__nominal_voltage = nominal_voltage
        self.__cells = cells                      
        self.__nominal_Ah = nominal_mAh/1000.0
        
        self.__nominal_capacity = 8500      # mAh

    
    # Scale capacity estimation based on external temperature
    def __scale_temperature(self):
        pass

    def __drain_curve_percent(self, x):
        return 58.821010559671066*x**3 + -2134.5758966115527*x**2 + 25869.660996405204*x + -104622.36370746762


    def __time_estimation_curve(self, x):
        return 0.00031623534490089853*x**3 + -0.06535263801996286*x**2 + 15.21882160202914*x + -32.77764056651616


    def simulate(self, voltage):
        """
        Simulate final time estimation from ULog voltages
        Best estimations from idle batteries

        :param voltage: voltage value
        :return: estimated time remaining in seconds
        """

        return self.__time_estimation_curve(self.__drain_curve_percent(voltage))

