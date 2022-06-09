#include <iostream>
#include <cassert>

#include <verge/mission-command/battery-model.h>

using namespace Verge::MissionCommand;

int main(int argc, char *argv[])
{
    if (argc == 2)
    {
        Test::print_name(argv[1]);
    }
    else
    {
        std::cout << "Hello World" << std::endl;
    }

    /* Unit Tests Here */

    assert(false); // use assertion

    return 0;
}