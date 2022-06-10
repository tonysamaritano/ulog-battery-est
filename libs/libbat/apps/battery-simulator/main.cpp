#include <cassert>
#include <cstdlib>
#include <vector>
#include <iostream>

#include <gtest/gtest.h>

#include <verge/mission-command/BatteryModel.h>

using namespace Verge::MissionCommand;

void voltageNoiseArray(std::vector<float> &volt_data, float finalValue, float noiseRange, float noiseVoltage, int length)
{
    for (int i = 0; i < length / 2; i++)
    {
        volt_data[i] = noiseVoltage + (-noiseRange + (float)(rand()) / (float)(RAND_MAX / (noiseRange - (-noiseRange))));
    }

    for (int i = length / 2; i <= length - 1; i++)
    {
        volt_data[i] = finalValue;
    }
}

TEST(NotArmedAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);
    voltageNoiseArray(voltage, 12.5f, 0.3f, 12.2f, 100);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(NotArmedAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 12.1f, 0.3f, 11.9f, 100);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(NotArmedAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 11.7f, 0.3f, 11.9f, 100);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 670);
    EXPECT_LT(model.getTimeEstimate(), 690);
}

TEST(ArmedAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);
    voltageNoiseArray(voltage, 12.5f, 0.2f, 12.2f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(ArmedAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 12.1f, 0.3f, 11.9f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(ArmedAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 11.7f, 0.3f, 11.9f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    EXPECT_GT(model.getTimeEstimate(), 670);
    EXPECT_LT(model.getTimeEstimate(), 690);
}

TEST(ArmSwapAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 12.5f, 0.3f, 12.2f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    model.setArmed(false);

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(ArmSwapAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 12.1f, 0.3f, 11.9f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    model.setArmed(false);

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(ArmSwapAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    std::vector<float> voltage(100);

    voltageNoiseArray(voltage, 11.7f, 0.3f, 11.9f, 100);
    model.setArmed(true);

    for (auto volts : voltage)
    {
        model.setInput(volts, 1.0e3f, 25.0f);
        model.update(1.0f / 20.0f);
    }

    model.setArmed(false);

    EXPECT_GT(model.getTimeEstimate(), 670);
    EXPECT_LT(model.getTimeEstimate(), 690);
}

int main(int argc, char *argv[])
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}