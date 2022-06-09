#pragma once
#include <string>
#include <verge/mission-command/BatteryCoefficients.h>
#include <math.h>

namespace Verge
{
    namespace MissionCommand
    {
        class BatteryModel
        {
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

            const float m_movingAvgSampleSize = 3;

            // Functions
            bool initCapacity();
            float equation(float x3, float x2, float x1, float x0, float input);
            float voltageToCapacity(float voltage);
            float capacityToTime(float cap);

        public:
            BatteryModel(BatteryCoefficients coefficients);
            void update(float dt);
            float getCapacity();
            float getTimeEstimate();
            void setInput(float volatge, float current, float temperature);
            void setArmed(bool arm);
        };
    }
}
