#include <iostream>
#include <math.h>

#include <verge/mission-command/BatteryModel.h>

using namespace Verge::MissionCommand;

BatteryModel::BatteryModel(BatteryCoefficients coefficients) : 
    m_coefficients(coefficients),
    m_voltage(0.0f),
    m_current(0.0f),
    m_capacity(0.0f),
    m_temperature(0.0f),
    m_rollingAverage(0.0f),
    m_armed(false),
    m_capacityInitialized(false) {}

float BatteryModel::equation(float x3, float x2, float x1, float x0, float input)
{
    /**
     * Return output of general 3rd order polynomial
     * 
     * @param x3    3rd degree coefficient
     * @param x2    2nd degree coefficient
     * @param x1    1st degree coefficient
     * @param x0    constant coefficient
     * 
     * @return output of 3rd order polynomial
     */

    return x3 * pow(input, 3) + x2 * pow(input, 2) + x1 * input + x0;
}

bool BatteryModel::initCapacity()
{
    /**
     * Initializes battery capacity based on measured voltages
     * 
     * @return status of capacity stabilization
     */

    float smallestDifference = 0.2f;
    float differenceCheck = 0.0f;

    float previous = m_rollingAverage;

    if(m_rollingAverage == 0.0)
    {
        m_rollingAverage = voltageToCapacity(m_voltage);
    }

    else
    {
        m_rollingAverage -= (m_rollingAverage / m_movingAvgSampleSize);
        m_rollingAverage += (voltageToCapacity(m_voltage) / m_movingAvgSampleSize);
    }

    differenceCheck = abs(m_rollingAverage - previous);
    m_capacity = m_rollingAverage;

    return (differenceCheck < smallestDifference);
}

float BatteryModel::getCapacity()
{
    /**
     * Returns current battery capacity
     * 
     * @return battery capacity in mAh
     */
    return m_capacity;
}

float BatteryModel::getTimeEstimate()
{
    /**
     * Calculate and return estimated time of flight in seconds
     * 
     * @return time in seconds
     */

    if(m_armed)
    {
        return capacityToTime(m_capacity);
    }
    else
    {
        float tempCapacity = voltageToCapacity(m_voltage);
        return capacityToTime(tempCapacity);
    }
}
