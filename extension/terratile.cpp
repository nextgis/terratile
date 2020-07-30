// #include <string>
#include <pybind11/pybind11.h>

#include "gdal.h"
#include "gdal_priv.h"

#include "ctb/types.hpp"
#include "ctb/GlobalGeodetic.hpp"
#include "ctb/TileCoordinate.hpp"
#include "ctb/MeshTiler.hpp"

#include "TemporaryOutputStream.hpp"

namespace py = pybind11;

const ctb::Grid grid = ctb::GlobalGeodetic();

py::bytes meshTile(
    size_t dataset,
    ctb::i_zoom z,
    ctb::i_tile x,
    ctb::i_tile y,
    bool writeNormals=false,
    double meshQuality=1.0
) {
    GDALDataset *poDataset = (GDALDataset *) dataset;
    const ctb::TileCoordinate coord = ctb::TileCoordinate(z, x, y);
    const ctb::MeshTiler tiler = ctb::MeshTiler(poDataset, grid, meshQuality);
    const auto tile = tiler.createMesh(poDataset, coord);

    auto stream = TemporaryOutputStream();
    tile->writeFile(stream, writeNormals);
    delete tile;

    return py::bytes(stream.compress());
}

ctb::i_zoom maxZoom(size_t dataset)
{
    const auto tiler = ctb::MeshTiler((GDALDataset *) dataset, grid);
    return tiler.maxZoomLevel();
}

PYBIND11_MODULE(_terratile, m) {
    m.def("mesh_tile", &meshTile);
    m.def("max_zoom", &maxZoom);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
