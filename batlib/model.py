# Battery monitoring library to estimate flight time remaining on the Verge X1 drone

import sys
import numpy as np
from dataclasses import dataclass


@dataclass
class BatteryCoefficientStruct:
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
    x3: float = 4438.520356552959
    x2: float = -161808.41170109142
    x1: float = 1970036.1888353096
    x0: float = -8003392.537598927

    y3: float = 5.124055173497321e-10
    y2: float = -9.008950105302864e-06
    y1: float = 0.17888813746864485
    y0: float = -32.85067290189358


class Model:
    def __init__(self, struct: BatteryCoefficientStruct):
        """
        Initialization of x3 model object

        :param struct: struct object of polynomial, capacity data
        """
        # Voltage -> Capacity coefficients
        self.__x3 = struct.x3
        self.__x2 = struct.x2
        self.__x1 = struct.x1
        self.__x0 = struct.x0

        # Capacity -> Time coefficients
        self.__y3 = struct.y3
        self.__y2 = struct.y2
        self.__y1 = struct.y1
        self.__y0 = struct.y0

        # Battery values/usage
        self.__voltage = 0.0
        self.__current = 0.0
        self.__temperature = 0.0
        self.__capacity = 0.0
        self.__rolling_average = 0.0

        # Arm boolean, capacity init boolean
        self.__armed = False
        self.__capacity_initialized = False

        self.__time_estimation = 0.0

        # Constants
        self.__moving_avg_sample_size = 3

    def update(self, dt):
        """
        Continuous update loop of battery information

        :param time: time elapsed (micro seconds)
        """
        # Initialize capacity
        if(not self.__capacity_initialized):
            self.__capacity_initialized = self.__init_capacity__()

        else:
            # Decrement current draw, assuming current is read as mA
            self.__capacity = self.__capacity - (self.__current*(dt/(3600*1e6)))

    def getCapacity(self) -> float:
        """
        Obtain current capacity value

        :return: current capacity
        """
        return self.__capacity

    def getTimeEstimate(self) -> float:
        """
        Return the current time estimation to the user

        :return: time estimation
        """
        # Perform estimations on either real or experimental data, depending on arm
        return self.__equation__(
            self.__y3, self.__y2, self.__y1, self.__y0, self.__capacity) if self.__armed else self.__equation__(
                self.__y3, self.__y2, self.__y1, self.__y0, self.__equation__(self.x3, self.__x2, self.__x1, self.__x0, self.__voltage))

    def setInput(self, voltage: float, current: float, temperature: float) -> None:
        """
        Set instantaneous battery information

        :param voltage: battery voltage
        :param current: current draw
        :param temperature: battery temperature
        """
        self.__voltage = voltage
        self.__current = current
        self.__temperature = temperature

    def setArmed(self, set: bool) -> None:
        """
        Indicate arming of drone

        :param set: true/false for enabling/disabling arm
        """
        self.__armed = set

    def __init_capacity__(self) -> bool:
        """
        Iterate and average rate of change of battery capacity to settle on an initial value

        :returns: a boolean value for if the capacity has been initialized
        """
        smallest_difference = 0
        difference_check = 0.0

        previous = self.__rolling_average

        if self.__rolling_average == 0.0:
            self.__rolling_average = self.__equation__(self.__x3, self.__x2,
                                                     self.__x1, self.__x0, self.__voltage)
        else:
            self.__rolling_average -= (self.__rolling_average /
                                     self.__moving_avg_sample_size)
            self.__rolling_average += (self.__equation__(self.__x3, self.__x2,
                                                       self.__x1, self.__x0, self.__voltage) / self.__moving_avg_sample_size)

        difference_check = abs(self.__rolling_average - previous)

        self.__capacity = self.__rolling_average

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
