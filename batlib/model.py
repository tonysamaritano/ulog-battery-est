# Battery monitoring library to estimate flight time remaining on the Verge X1 drone

import sys
import numpy as np
from dataclasses import dataclass


@dataclass
class PolyStruct:
    """Structure for the coefficients of x3 given
    third order polynomial function.

    Third order polynomial equation:
    x3*x^3 + x2*x^2 + x1*x + x0

    Attributes
    ----------
    x3: float
        3rd degree coefficient for voltage->capacity conversion. 
        Default values are from previously calculated tests generated 
        by <batt-testing.py>
    x2: float 
        2nd degree coefficient for voltage->capacity conversion
    x1: float
        1st degree coefficient for voltage->capacity conversion
    x0: float
        constant coeffcient for voltage->capacity conversion
    y3: float
        3rd degree coefficient for capacity->time conversion. 
        Default values are from previously calculated tests generated 
        by <batt-testing.py>
    y2: float
        2nd degree coefficient for capacity->time conversion
    y1: float
        1st degree coefficient for capacity->time conversion
    y0: float
        constant coefficient for capacity->time conversion
    capacity: float
        nominal capacity for battery, determined through testing
    """
    x3: float = 58.821010559671066
    x2: float = -2134.5758966115527
    x1: float = 25869.660996405204
    x0: float = -104622.36370746762

    y3: float = 0.00031623534490089853
    y2: float = -0.06535263801996286
    y1: float = 15.21882160202914
    y0: float = -32.77764056651616

    capacity: float = 8500


class Model:
    def __init__(self, struct: PolyStruct):
        """
        Initialization of x3 model object

        :param struct: struct object of polynomial, capacity data
        """
        # Voltage -> Capacity coefficients
        self.x3 = struct.x3
        self.x2 = struct.x2
        self.x1 = struct.x1
        self.x0 = struct.x0

        # Capacity -> Time coefficients
        self.y3 = struct.y3
        self.y2 = struct.y2
        self.y1 = struct.y1
        self.y0 = struct.y0

        # User specified nominal capacity of battery
        self.nominal_capacity = struct.capacity

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

        :param time: time elapsed (micro seconds)

        :return: estimated time remaining in seconds
        """
        # Initialize capacity
        if(not self.capacity_initialized):
            self.__init_capacity__()

        # Decrement current draw, assuming current is read as mA
        # *************************************************************************************************
        # *** will dt be continuously summed/overall time, or be passed as x3 duration since last update ***
        # *************************************************************************************************
        self.capacity = self.capacity - (self.current*(dt/(3600*1e6)))

        # Perform estimations on either real or experimental data, depedning on arm
        self.time_estimation = self.__equation__(
            self.y3, self.y2, self.y1, self.y0, self.capacity) if self.armed else self.__equation__(
                self.y3, self.y2, self.y1, self.y0, self.__equation__(self.x3, self.x2, self.x1, self.x0, self.voltage))

        return self.time_estimation

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

        :returns: a boolean value for if the capacity has been initialized
        """
        smallest_difference = 50
        difference_check = 0
        new_average = 0

        new_average = (self.rolling_average - self.rolling_average / 5) + (
            self.rolling_average + self.__equation__(self.x3, self.x2, self.x1, self.x0, self.voltage) / 5)

        difference_check = self.rolling_average - new_average

        return True if difference_check < smallest_difference else False

    def __equation__(self, x3: float, x2: float, x1: float, x0: float, input: float) -> float:
        """
        3rd order polynomial estimation of capacity fromm input value (voltage or capacity)

        :param voltage: input voltage
        :param x3: 3rd degree coefficient
        :param x2: 2nd degree coefficient
        :param x1: 1st degree coefficient
        :param x0: constant coefficient
        :return: resulting capacity estimate
        """
        return (x3*input**3) + (x2*input**2) + (x1*input) + x0
