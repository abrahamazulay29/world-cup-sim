cmake_minimum_required(VERSION 3.15)
project(world_cup_sim LANGUAGES CXX)

find_package(pybind11 REQUIRED)

# build the module
pybind11_add_module(cxx_sim MODULE src/core/cxx_sim.cpp)
target_compile_features(cxx_sim PRIVATE cxx_std_17)
set_target_properties(cxx_sim PROPERTIES PREFIX "")   # cxx_sim.so

# NEW: make sure it is placed in the wheel / editable install
install(TARGETS cxx_sim LIBRARY DESTINATION .)
