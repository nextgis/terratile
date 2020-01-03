// #include <string>
#include <pybind11/pybind11.h>

#include "gdal.h"
#include "gdal_priv.h"

#include "ctb/types.hpp"
#include "ctb/GlobalGeodetic.hpp"
#include "ctb/TileCoordinate.hpp"
#include "ctb/TerrainTiler.hpp"

#include "TemporaryOutputStream.hpp"

namespace py = pybind11;

py::bytes build(
    size_t dataset,
    ctb::i_zoom z,
    ctb::i_tile x,
    ctb::i_tile y
) {
    GDALDataset *poDataset = (GDALDataset *) dataset;
    const ctb::Grid grid = ctb::GlobalGeodetic();
    const ctb::TileCoordinate coord = ctb::TileCoordinate(z, x, y);
    const ctb::TerrainTiler tiler = ctb::TerrainTiler(poDataset, grid);
    const auto tile = tiler.createTile(poDataset, coord);

    auto stream = TemporaryOutputStream();
    tile->writeFile(stream);
    delete tile;

    return py::bytes(stream.compress());
}

PYBIND11_MODULE(_terratile, m) {
    m.def("build", &build);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
