cmake_minimum_required(VERSION 2.8)

project(terratile)

# Some init settings
set(CMAKE_COLOR_MAKEFILE ON)
# Set path to additional CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})
include(FindAnyProject)

include(util)
check_version(CTB_VERSION_MAJOR CTB_VERSION_MINOR CTB_VERSION_PATCH)
set(VERSION ${CTB_VERSION_MAJOR}.${CTB_VERSION_MINOR}.${CTB_VERSION_PATCH})
report_version("${PROJECT_NAME}" ${VERSION})

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Perform as many checks as possible on debug builds:
#    cmake -DCMAKE_BUILD_TYPE=Debug ..
if(NOT MSVC)
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall -Wextra --pedantic")
endif()

# CTB
# The tile size (width and height). According to the spec this should always be
# 65
set(TERRAIN_TILE_SIZE 65)
# The tile water mask size (width and height). According to the spec this
# should always be 256
set(TERRAIN_MASK_SIZE 256)

set(CTB_SRC ${PROJECT_SOURCE_DIR}/third-party/ctb)

configure_file(
    ${CTB_SRC}/config.hpp.in
    ${CMAKE_BINARY_DIR}/third-party/ctb/config.hpp
)

include_directories(
    ${PROJECT_SOURCE_DIR}/third-party
    ${CMAKE_BINARY_DIR}/third-party/ctb
)

# We need GDAL
find_anyproject(GDAL REQUIRED VERSION 3.0)

string(SUBSTRING ${GDAL_VERSION_STRING} 0 1 GDAL_VERSION_MAJOR)
include_directories(
    ${PROJECT_SOURCE_DIR}/third-party/ctb/GDAL${GDAL_VERSION_MAJOR}
)

# We need zlib
find_anyproject(ZLIB REQUIRED)

set(LIBS ${LIBS} ${ZLIB_LIBRARIES} ${GDAL_LIBRARIES})

# PYBIND11
add_subdirectory(third-party/pybind11)

pybind11_add_module(_terratile
    extension/terratile.cpp
    extension/TemporaryOutputStream.cpp
    ${CTB_SRC}/GDALTile.cpp
    ${CTB_SRC}/GDALTiler.cpp
    ${CTB_SRC}/GDALDatasetReader.cpp
    ${CTB_SRC}/TerrainTiler.cpp
    ${CTB_SRC}/TerrainTile.cpp
    ${CTB_SRC}/MeshTiler.cpp
    ${CTB_SRC}/MeshTile.cpp
    ${CTB_SRC}/GlobalMercator.cpp
    ${CTB_SRC}/GlobalGeodetic.cpp    
    ${CTB_SRC}/CTBFileOutputStream.cpp
    ${CTB_SRC}/CTBZOutputStream.cpp
)

target_link_libraries(_terratile PRIVATE ${LIBS})
