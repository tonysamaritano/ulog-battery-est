# Battery monitoring library to estimate flight time remaining on the Verge X1 drone

import sys
import numpy as np
from dataclasses import dataclass


@dataclass
class PolyStruct:
    """Structure for the coefficients of a given
    third order polynomial function.

    Third order polynomial equation:
    a*x^3 + b*x^2 + c*x + d

    Attributes
    ----------
    a: float
        3rd degree coefficient for voltage->capacity conversion. 
        Default values are from previously calculated tests generated 
        by <batt-testing.py>
    b: float 
        2nd degree coefficient for voltage->capacity conversion
    c: float
        1st degree coefficient for voltage->capacity conversion
    d: float
        constant coeffcient for voltage->capacity conversion
    e: float
        3rd degree coefficient for capacity->time conversion. 
        Default values are from previously calculated tests generated 
        by <batt-testing.py>
    f: float
        2nd degree coefficient for capacity->time conversion
    g: float
        1st degree coefficient for capacity->time conversion
    h: float
        constant coefficient for capacity->time conversion
    capacity: float
        nominal capacity for battery, determined through testing
    """
    a: float = 58.821010559671066
    b: float = -2134.5758966115527
    c: float = 25869.660996405204
    d: float = -104622.36370746762

    e: float = 0.00031623534490089853
    f: float = -0.06535263801996286
    g: float = 15.21882160202914
    h: float = -32.77764056651616

    capacity: float = 8500


class Model:
    def __init__(self, struct: PolyStruct):
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
        self.capacity_array = np.array(np.ones(100))
        self.rolling_average = 0

        # Arm boolean, capacity init boolean
        self.armed = False
        self.capacity_initialized = False

        self.time_estimation = 0.0

    def update(self, dt) -> float:
        """
        Continuous update loop of battery information

        :param time: time elapsed 

        :return: estimated time remaining in seconds
        """
        # Initialize capacity
        if(not self.capacity_initialized):
            self.__init_capacity__()

        # Decrement current draw, assuming current is read as mA
        # *************************************************************************************************
        # *** will dt be continuously summed/overall time, or be passed as a duration since last update ***
        # *************************************************************************************************
        self.capacity = self.capacity - (self.current*(dt/3600))

        # Perform estimations on either real or experimental data, depedning on arm
        self.time_estimation = self.__equation__(
            self.e, self.f, self.g, self.h, self.capacity) if self.armed else self.__equation__(
                self.e, self.f, self.g, self.h, self.__equation__(self.a, self.b, self.c, self.d, self.voltage))

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

    def setArmed(self, set: bool) -> None:
        """
        Indicate arming of drone

        :param set: true/false for enabling/disabling arm
        """
        self.armed = set

    def __init_capacity__(self) -> bool:
        """
        Iterate and average rate of change of battery capacity to settle on an initial value
        """
        smallest_difference = 50
        difference_check = 0
        new_average = 0

        new_average = (self.rolling_average - self.rolling_average / 5) + (
            self.rolling_average + self.__equation__(self.a, self.b, self.c, self.d, self.voltage) / 5)

        difference_check = self.rolling_average - new_average

        return True if difference_check < smallest_difference else False

    def __equation__(self, a: float, b: float, c: float, d: float, input: float) -> float:
        """
        3rd order polynomial estimation of capacity fromm input value (voltage or capacity)

        :param voltage: input voltage
        :param a: 3rd degree coefficient
        :param b: 2nd degree coefficient
        :param c: 1st degree coefficient
        :param d: constant coefficient
        :return: resulting capacity estimate
        """
        return (a*input**3) + (b*input**2) + (c*input) + d
