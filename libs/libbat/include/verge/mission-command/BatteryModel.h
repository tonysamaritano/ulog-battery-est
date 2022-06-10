#pragma once
#include <string>
#include <verge/mission-command/BatteryCoefficients.h>

namespace Verge
{
    namespace MissionCommand
    {
        class BatteryModel
        {
        public:
            BatteryModel(BatteryCoefficients coefficients);

            /**
             * Continuous update loop of battery information
             *
             * @param dt interval of time elasped in seconds
             */
            void update(float dt);

            /**
             * Returns current battery capacity
             *
             * @return battery capacity in mAh
             */
            float getCapacity() const;

            /**
             * Calculate and return estimated time of flight in seconds
             *
             * @return time in seconds
             */
            float getTimeEstimate();

            /**
             * Set instantaneous battery information
             *
             * @param voltage battery voltage
             * @param current current draw
             * @param temperature battery temperature
             */
            void setInput(float volatge, float current, float temperature);

            /**
             * Indicate arming of drone
             *
             * @param arm true/false for enabling/disabling arm
             */
            void setArmed(bool arm);

        private:
            // Curve polynomial coefficients
            BatteryCoefficients m_coefficients;

            // Battery data
            float m_voltage;
            float m_current;
            float m_capacity;
            float m_temperature;
            float m_rollingAverage;

            // Boolean flags
            bool m_armed;
            bool m_capacityInitialized;

            static constexpr float m_movingAvgSampleSize = 3;

            // Functions

            /**
             * Initializes battery capacity based on measured voltages
             *
             * @return status of capacity stabilization
             */
            bool initCapacity();

            /*
             * Return output of general 3rd order polynomial
             *
             * @param x3    3rd degree coefficient
             * @param x2    2nd degree coefficient
             * @param x1    1st degree coefficient
             * @param x0    constant coefficient
             *
             * @return output of 3rd order polynomial */
            float equation(float x3, float x2, float x1, float x0, float input);

            /**
             * Uses a given voltage to estimation current capacity
             *
             * @param voltage battery voltage
             * @return float capacity estimation
             */
            float voltageToCapacity(float voltage);

            /**
             * @brief Uses givne capacity and converts to time estimation
             *
             * @param capacity current capacity
             * @return float capacity estimation
             */
            float capacityToTime(float cap);
        };
    }
}
