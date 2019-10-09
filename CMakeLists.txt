cmake_minimum_required(VERSION 3.15.3)
project(py_common_util_for_c)

# c++17 support
set(CMAKE_CXX_STANDARD 17)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_C_FLAGS "-Wall -Wextra")
set(CMAKE_C_FLAGS_DEBUG "-g")
set(CMAKE_C_FLAGS_RELEASE "-O3")

# cmake files
#set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_LIST_DIR}/cmake)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_LIST_DIR}/py_common_util/hello/cmake)
include(UseCython)

# cython files
set(CYTHON_FLAGS ${CYTHON_FLAGS} -3)
FILE(GLOB SOURCE_FILES py_common_util/hello/cython/*.pyx)
add_subdirectory(py_common_util/hello/cython)

# c++ files
set(foo_src "src/hello/foo.cc")
add_library(foo SHARED ${foo_src})
