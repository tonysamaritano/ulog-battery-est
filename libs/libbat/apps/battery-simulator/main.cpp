#include <iostream>
#include <cassert>

<<<<<<< HEAD
#include <verge/mission-command/battery-model.h>
=======
#include <verge/mission-command/BatteryCoefficients.h>
>>>>>>> 214dce341fedd92ee4677a455e23018015a38846

using namespace Verge::MissionCommand;

int main(int argc, char *argv[])
{
    if (argc == 2)
    {
        BatteryCoefficients::print_name(argv[1]);
    }
    else
    {
        std::cout << "Hello World" << std::endl;
    }

    /* Unit Tests Here */

    assert(false); // use assertion

    return 0;
}