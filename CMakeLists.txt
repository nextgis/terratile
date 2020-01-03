cmake_minimum_required(VERSION 2.8)

project(terratile)

# ZLIB
find_package(ZLIB)
include_directories(${ZLIB_INCLUDE_DIRS})
set(LIBS ${LIBS} ${ZLIB_LIBRARIES})

# GDAL
find_package(GDAL)
include_directories(${GDAL_INCLUDE_DIRS})
set(LIBS ${LIBS} ${GDAL_LIBRARIES})

# CTB
set(CTB_VERSION_MAJOR 0)
set(CTB_VERSION_MINOR 4)
set(CTB_VERSION_PATCH 1)
set(TERRAIN_TILE_SIZE 65)
set(TERRAIN_MASK_SIZE 256)

configure_file(
  "ctb/src/config.hpp.in"
  "external/ctb/config.hpp"
)

file(COPY ctb/src/ DESTINATION external/ctb)

include_directories(${CMAKE_BINARY_DIR}/external)

# PYBIND11
add_subdirectory(pybind11)

pybind11_add_module(_terratile
    extension/terratile.cpp
    extension/TemporaryOutputStream.cpp
    external/ctb/GDALTile.cpp
    external/ctb/GDALTiler.cpp
    external/ctb/GDALDatasetReader.cpp
    external/ctb/TerrainTiler.cpp
    external/ctb/TerrainTile.cpp
    external/ctb/MeshTiler.cpp
    external/ctb/MeshTile.cpp
    external/ctb/GlobalMercator.cpp
    external/ctb/GlobalGeodetic.cpp    
    external/ctb/CTBFileOutputStream.cpp
    external/ctb/CTBZOutputStream.cpp
)

target_link_libraries(_terratile PRIVATE ${LIBS})
