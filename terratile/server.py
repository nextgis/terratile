import os
import math
from pathlib import Path
from collections import OrderedDict

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.templating import Jinja2Templates

from osgeo import gdal, osr

from terratile import mesh_tile, max_zoom

CFG_DATA_PATH = Path(os.environ.get('TERRATILE_DATA_PATH', './'))
CFG_EXTENSIONS = ('.tif', '.tiff', '.vrt')

EPSG_4326 = osr.SpatialReference()
EPSG_4326.ImportFromEPSG(4326)


class Dataset(object):
    datasets = dict()

    @classmethod
    def from_name(cls, name):
        result = cls.datasets.get(name)
        if result is not None:
            return result

        for s in ('', ) + CFG_EXTENSIONS:
            fn = CFG_DATA_PATH / (name + s)
            if fn.is_file():
                obj = Dataset(str(fn))
                cls.datasets[name] = obj
                return obj

        return None

    def __init__(self, filename):
        self.gdal_ds = gdal.Open(filename, gdal.GA_ReadOnly)
        self.sr = osr.SpatialReference(wkt=self.gdal_ds.GetProjection())

        self.tile_res = 180
        self.tile_origin = (-180, -90)

        ulx, xres, xskew, uly, yskew, yres = self.gdal_ds.GetGeoTransform()
        lrx = ulx + (self.gdal_ds.RasterXSize * xres)
        lry = uly + (self.gdal_ds.RasterYSize * yres)

        transform = osr.CoordinateTransformation(self.sr, EPSG_4326)
        ul = transform.TransformPoint(ulx, uly)
        lr = transform.TransformPoint(lrx, lry)

        self.min_x, self.min_y = min(ul[0], lr[0]), min(ul[1], lr[1])
        self.max_x, self.max_y = max(ul[0], lr[0]), max(ul[1], lr[1])

        self.bounds = (self.min_x, self.min_y, self.max_x, self.max_y)

        tres = self.tile_res
        self.avtile = []
        for z in range(0, max_zoom(self.gdal_ds)):
            self.avtile.append((
                math.floor((self.min_x - self.tile_origin[0]) / tres),
                math.floor((self.min_y - self.tile_origin[1]) / tres),
                math.ceil((self.max_x - self.tile_origin[0]) / tres) - 1,
                math.ceil((self.max_y - self.tile_origin[1]) / tres) - 1,
            ) if z > 0 else (0, 0, 1, 0))

            tres /= 2


app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent.resolve()))


@app.get('/{dataset}/layer.json')
def layer_json(dataset: str, normals:bool=False):
    ds = Dataset.from_name(dataset)
    tiles_url='{z}/{x}/{y}.terrain'
    if normals:
        tiles_url+='?normals=True'
    data = OrderedDict(
        tilejson='2.1.0',
        name=dataset,
        description='',
        version='1.1.0',
        format='quantized-mesh-1.0',
        attribution='',
        schema='tms',
        extensions=['octvertexnormals'] if normals else [],
        tiles=(tiles_url, ),
        projection='EPSG:4326',
        bounds=ds.bounds,
        available=[
            (OrderedDict(zip(('startX', 'startY', 'endX', 'endY'), a)), )
            for a in ds.avtile
        ]
    )

    return JSONResponse(data)


@app.get('/{dataset}/{z}/{x}/{y}.terrain')
def tile(dataset: str, z: int, x: int, y: int, normals: bool=False, quality: float=1.0):
    ds = Dataset.from_name(dataset)
    data = mesh_tile(ds.gdal_ds, (z, x, y), write_normals=normals, quality=quality)
    return Response(data, media_type="application/octet-stream", headers={
        'Access-Control-Allow-Origin': '*',
        'Content-Encoding': 'gzip',
        'Cache-Control': 'max-age=600'
    })


@app.get('/{dataset}/preview')
def preview(request: Request, dataset: str, normals:bool=None, quality:float=None):
    ds = Dataset.from_name(dataset)
    return templates.TemplateResponse('preview.html', {
        'request': request,
        'dataset': dataset,
        'bounds': ds.bounds,
        'quality': quality,
        'normals':normals
    })
