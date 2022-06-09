#include <iostream>
#include "verge/mission-command/BatteryCoefficients.h"

using namespace Verge::MissionCommand;

// Model Constructor
Model::Model(BatteryCoefficients coefficients)
{
    m_coefficients = coefficients;
}

/**
 * @brief Continuous update loop of battery information
 * 
 * @param[in] dt interval of time elasped in seconds
 */
void Model::update(float dt)
{
    // Initialize capacity
    if(!m_capacityInitialized)
    {
        m_capacityInitialized = init_capacity();
    }
    else
    {
        // Decrement current draw, assuming current is read at mA
        m_capacity = m_capacity - (m_current*(dt/(3600)))
    }
}

/**
 * @brief Set instantaneous battery information
 * 
 * @param[in] voltage battery voltage
 * @param[in] current current draw
 * @param[in] temperature battery temperature
 */
void Model::setInput(float voltage, float current, float temperature)
{
    m_voltage = voltage;
    m_current = current;
    m_temperature = temperature;
}

/**
 * @brief Indicate arming of drone
 * 
 * @param[in] arm true/false for enabling/disabling arm
 */
void Model::setArmed(bool arm)
{
    m_armed = arm;
}

/**
 * @brief Uses givne capacity and converts to time estimation
 * 
 * @param[in] capacity current capacity
 * @return float capacity estimation
 */
float Model::capacityToTime(float capacity)
{
    return equation(m_coefficients.y3, m_coefficients.y2, 
                    m_coefficients.y1, m_coefficients.y0,
                    capacity);
}

/**
 * @brief Uses a given voltage to estimation current capacity
 * 
 * @param[in] voltage battery voltage
 * @return float capacity estimation
 */
float Model::voltageToCapacity(float voltage)
{
    return equation(m_coefficients.x3, m_coefficients.x2, 
                    m_coefficients.x1, m_coefficients.x0,
                    voltage);
}