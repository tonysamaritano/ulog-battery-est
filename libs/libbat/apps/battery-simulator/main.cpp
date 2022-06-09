#include <iostream>
#include <cassert>

#include <verge/mission-command/BatteryModel.h>

#include <gtest/gtest.h>

#include <cstdlib>

using namespace Verge::MissionCommand;

void voltageNoiseArray(float * volt_data, float finalValue, float noiseRange, float noiseVoltage, int length)
{
    for (int i = 0; i <= (int)(length / 2) - 1; i++)
    {
        volt_data[i] = noiseVoltage + (-noiseRange + (float)(rand()) / (float)(RAND_MAX / (noiseRange - (-noiseRange))));
    }

    for (int i = (int)(length / 2); i <= length - 1; i++)
    {
        volt_data[i] = finalValue;
    }
}

TEST(NotArmedAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];
    voltageNoiseArray(voltage, 12.5, 0.3, 12.2, 100);

    int arrSize = sizeof(voltage) / sizeof(float);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(NotArmedAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 12.1, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(NotArmedAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 11.7, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 670);
    EXPECT_LT(model.getTimeEstimate(), 690);
}

TEST(ArmedAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 12.5, 0.3, 12.2, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(ArmedAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 12.1, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(ArmedAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 11.7, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    EXPECT_GT(model.getTimeEstimate(), 670);
    EXPECT_LT(model.getTimeEstimate(), 690);
}

TEST(ArmSwapAccuracyTest, FullVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 12.5, 0.3, 12.2, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    model.setArmed(false);

    EXPECT_GT(model.getTimeEstimate(), 1120);
    EXPECT_LT(model.getTimeEstimate(), 1160);
}

TEST(ArmSwapAccuracyTest, MidVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 12.1, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
    }

    model.setArmed(false);

    EXPECT_GT(model.getTimeEstimate(), 910);
    EXPECT_LT(model.getTimeEstimate(), 940);
}

TEST(ArmSwapAccuracyTest, LowVoltage)
{
    BatteryCoefficients coefficients;
    BatteryModel model = BatteryModel(coefficients);

    float voltage[100];

    voltageNoiseArray(voltage, 11.7, 0.3, 11.9, 100);
    int arrSize = sizeof(voltage) / sizeof(float);
    model.setArmed(true);

    for (int i = 0; i <= arrSize-1; i++)
    {
        model.setInput(voltage[i], 1e3, 25);
        model.update(1 / 20);
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