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

float BatteryModel::equation(float x3, float x2, float x1, float x0, float input)
{
    return x3 * pow(input, 3) + x2 * pow(input, 2) + x1 * input + x0;
}

float BatteryModel::voltageToCapacity(float voltage)
{
    return equation(m_coefficients.x3, m_coefficients.x2,
                    m_coefficients.x1, m_coefficients.x0,
                    voltage);
}

float BatteryModel::capacityToTime(float capacity)
{
    return equation(m_coefficients.y3, m_coefficients.y2,
                    m_coefficients.y1, m_coefficients.y0,
                    capacity);
}

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

float BatteryModel::getCapacity() const
{
    return m_capacity;
}

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

void BatteryModel::setInput(float voltage, float current, float temperature)
{
    m_voltage = voltage;
    m_current = current;
    m_temperature = temperature;
}

void BatteryModel::setArmed(bool arm)
{
    m_armed = arm;
}
