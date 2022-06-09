cmake_minimum_required(VERSION 3.10)

project(BatteryLibrary VERSION 1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_executable(bat-sim
    apps/battery-simulator/main.cpp
)

include_directories(include)

add_library(bat
    src/test.cpp
)

target_link_libraries(bat-sim PUBLIC bat)
target_include_directories(bat-sim PUBLIC include)


