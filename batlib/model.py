# Battery monitoring library to estimate flight time remaining on the Verge X1 drone

import sys
import numpy as np


class Model:
    def __init__(self, struct):
        """
        Initialization of a model object

        :param struct: struct object of polynomial, capacity data
        """
        # Voltage -> Capacity coefficients
        self.a = struct.a
        self.b = struct.b
        self.c = struct.c
        self.d = struct.d

        # Capacity -> Time coefficients
        self.e = struct.e
        self.f = struct.f
        self.g = struct.g
        self.h = struct.h

        # User specified nominal capacity of battery
        self.nominal_capacity = struct.nominal_capacity

        # Battery values/usage
        self.voltage = 0
        self.current = 0
        self.temperature = 0
        self.capacity = 0

        # Arm boolean
        self.armed = False

        self.time_estimation = 0.0

    def update(self, time):
        """
        Continuous update loop of battery information

        :param time: time elapsed 
        """
        pass

    def getTimeEstimate(self) -> float:
        """
        Return the current time estimation to the user

        :return: time estimation
        """
        return self.time_estimation

    def setInput(self, voltage: float, current: float, temperature: float) -> None:
        """
        Set instantaneous battery information

        :param voltage: battery voltage
        :param current: current draw
        :param temperature: battery temperature
        """
        self.voltage = voltage
        self.current = current
        self.temperature = temperature

    def setArmed(self) -> None:
        """
        Indicate arming of drone
        """
        self.armed = True

    def __init_capacity__(self) -> bool:
        """
        Iterate and average rate of change of battery capacity to settle on an initial value
        """

        pass

    def __voltage_to_capacity__(self, a: float, b: float, c: float, d: float, voltage: float) -> float:
        """
        3rd order polynomial estimation of capacity form voltage value

        :param voltage: input voltage
        :param a: 3rd degree coefficient
        :param b: 2nd degree coefficient
        :param c: 1st degree coefficient
        :param d: constant coefficient
        :return: resulting capacity estimate
        """
        return (a*voltage**3) + (b*voltage**2) + (c*voltage) + d

    def __capacity_to_time__(self, a: float, b: float, c: float, d: float, capacity: float) -> float:
        """
        3rd order polynomial estimation of time form capacity value

        :param capacity: input capacity
        :param a: 3rd degree coefficient
        :param b: 2nd degree coefficient
        :param c: 1st degree coefficient
        :param d: constant coefficient
        :return: resulting time estimate
        """
        return (a*capacity**3) + (b*capacity**2) + (c*capacity) + d
