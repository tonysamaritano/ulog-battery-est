#pragma once
#include <string>

namespace Verge
{
    namespace MissionCommand
    {
        struct BatteryCoefficients
        {
            float x3 = 4438.520356552959;
            float x2 = -161808.41170109142;
            float x1 = 1970036.1888353096;
            float x0 = -8003392.537598927;

            float y3 = 5.124055173497321e-10;
            float y2 = -9.008950105302864e-06;
            float y1 = 0.17888813746864485;
            float y0 = -32.85067290189358;
        };

        class Model
        {
        private:
            BatteryCoefficients m_coefficients;

            // Battery values/usage
            float m_voltage = 0.0;
            float m_current = 0.0;
            float m_temperature = 0.0;
            float m_capacity = 0.0;
            float m_rollingAverage = 0.0;

            // Arm boolean, capacity init boolean
            bool m_armed = false;
            bool m_capacityInitialized = false;

            // Constraints
            int m_movingAvgSamapleSize = 3;

            float capacityToTime(float capacity);
            float voltageToCapacity(float voltage);
        
        public:
            void update(float dt);
            void setInput(float voltage, float current, float, temperature);
            void setArmed(bool arm);
        };
    }
}
