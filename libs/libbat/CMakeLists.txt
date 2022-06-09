cmake_minimum_required(VERSION 3.10)

project(BatteryLibrary VERSION 1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

enable_testing()
find_package(GTest REQUIRED)


add_executable(bat-sim
    apps/battery-simulator/main.cpp
)

add_test(AllGTests bat-sim)

include_directories(include)

add_library(bat
    src/BatteryModel.cpp
)

target_link_libraries(bat-sim PUBLIC bat GTest::gtest GTest::gtest_main)
target_include_directories(bat-sim PUBLIC include)
