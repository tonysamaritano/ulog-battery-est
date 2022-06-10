#include <verge/mission-command/BatteryModel.h>
#include <cmath>

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

/**
 * Continuous update loop of battery information
 *
 * @param dt interval of time elasped in seconds
 */
void BatteryModel::update(float dt)
{
    /* Initialize capacity */
    if (!m_capacityInitialized)
    {
        m_capacityInitialized = initCapacity();
    }

    else
    {
        /* Decrement current draw, assuming current is read at mA */
        m_capacity = m_capacity - (m_current * (dt / (3600.0f)));
    }
}

/*
 * Return output of general 3rd order polynomial
 *
 * @param x3    3rd degree coefficient
 * @param x2    2nd degree coefficient
 * @param x1    1st degree coefficient
 * @param x0    constant coefficient
 *
 * @return output of 3rd order polynomial */
float BatteryModel::equation(float x3, float x2, float x1, float x0, float input)
{
    return x3 * pow(input, 3) + x2 * pow(input, 2) + x1 * input + x0;
}

/**
 * Uses a given voltage to estimation current capacity
 *
 * @param voltage battery voltage
 * @return float capacity estimation
 */
float BatteryModel::voltageToCapacity(float voltage)
{
    return equation(m_coefficients.x3, m_coefficients.x2,
                    m_coefficients.x1, m_coefficients.x0,
                    voltage);
}

/**
 * @brief Uses givne capacity and converts to time estimation
 *
 * @param capacity current capacity
 * @return float capacity estimation
 */
float BatteryModel::capacityToTime(float capacity)
{
    return equation(m_coefficients.y3, m_coefficients.y2,
                    m_coefficients.y1, m_coefficients.y0,
                    capacity);
}

/**
 * Initializes battery capacity based on measured voltages
 *
 * @return status of capacity stabilization
 */
bool BatteryModel::initCapacity()
{
    const float smallestDifference = 0.2f;
    float differenceCheck = 0.0f;

    float previous = m_rollingAverage;

    if (m_rollingAverage == 0.0f)
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

/**
 * Returns current battery capacity
 *
 * @return battery capacity in mAh
 */
float BatteryModel::getCapacity()
{
    return m_capacity;
}

/**
 * Calculate and return estimated time of flight in seconds
 *
 * @return time in seconds
 */
float BatteryModel::getTimeEstimate()
{
    if (m_armed)
    {
        return capacityToTime(m_capacity);
    }
    else
    {
        float tempCapacity = voltageToCapacity(m_voltage);
        return capacityToTime(tempCapacity);
    }
}

/**
 * Set instantaneous battery information
 * 
 * @param voltage battery voltage
 * @param current current draw
 * @param temperature battery temperature
 */
void BatteryModel::setInput(float voltage, float current, float temperature)
{
    m_voltage = voltage;
    m_current = current;
    m_temperature = temperature;
}

/**
 * Indicate arming of drone
 * 
 * @param arm true/false for enabling/disabling arm
 */
void BatteryModel::setArmed(bool arm)
{
    m_armed = arm;
}
