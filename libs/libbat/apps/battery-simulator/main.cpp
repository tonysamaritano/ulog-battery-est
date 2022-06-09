#include <iostream>

#include <verge/mission-command/test.h>

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

    return 0;
}