import os
import math
from pathlib import Path
from collections import OrderedDict

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.templating import Jinja2Templates

from osgeo import gdal, osr

from terratile import build

CFG_DATA_PATH = Path(os.environ.get('TERRATILE_DATA_PATH', './'))
CFG_EXTENSIONS = ('.tif', '.tiff', '.vrt')

EPSG_4326 = osr.SpatialReference()
EPSG_4326.ImportFromEPSG(4326)

EPSG_3857 = osr.SpatialReference()
EPSG_3857.ImportFromEPSG(3857)


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
        
        sr = osr.SpatialReference()
        sr.ImportFromProj4(self.gdal_ds.GetProjection())

        if sr.IsSameGeogCS(EPSG_4326):
            self.sr = EPSG_4326
            self.tile_res = 180
            self.tile_origin = (-180, -90)
        elif sr.IsSameGeogCS(EPSG_3857):
            self.sr = EPSG_3857
            self.tile_res = 2 * 20037508.34
            self.tile_origin = (-20037508.34, -20037508.34)
        else:
            raise ValueError("Only EPSG:4326 and EPSG:3857 supported!")

        ulx, xres, xskew, uly, yskew, yres  = self.gdal_ds.GetGeoTransform()
        lrx = ulx + (self.gdal_ds.RasterXSize * xres)
        lry = uly + (self.gdal_ds.RasterYSize * yres)

        self.ul = (ulx, uly)
        self.lr = (lrx, lry)

        self.min_x, self.min_y = min(ulx, lrx), min(uly, lry)
        self.max_x, self.max_y = max(ulx, lrx), max(uly, lry)

        # TODO: Reproject bounds to EPSG:4326
        self.bounds = (self.min_x, self.min_y, self.max_x, self.max_y)

        z = 0
        tres = self.tile_res
        minres = 16 * min(abs(xres), abs(yres))
        self.avtile = []
        while True:
            self.avtile.append((
                math.floor((self.min_x - self.tile_origin[0]) / tres),
                math.floor((self.min_y - self.tile_origin[1]) / tres),
                math.ceil((self.max_x - self.tile_origin[0]) / tres) - 1,
                math.ceil((self.max_y - self.tile_origin[1]) / tres) - 1,
            ) if z > 0 else (
                (0, 0, 1, 0) if self.sr == EPSG_4326
                else (0, 0, 0, 0)
            ))

            z += 1
            tres /= 2

            if tres < minres:
                break


app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent.resolve()))

@app.get('/{dataset}/layer.json')
def layer_json(dataset: str):
    ds = Dataset.from_name(dataset)
    data = OrderedDict(
        tilejson='2.1.0',
        name=dataset,
        description='',
        version='1.1.0',
        format='quantized-mesh-1.0',
        attribution='',
        schema='tms',
        extensions=('octvertexnormals', ),
        tiles=('{z}/{x}/{y}.terrain', ),
        projection='EPSG:4326' if ds.sr == EPSG_4326 else 'EPSG:3857',
        bounds=ds.bounds,
        available=[
            (OrderedDict(zip(('startX', 'startY', 'endX', 'endY'), a)), )
            for a in ds.avtile
        ]
    )

    return JSONResponse(data)


@app.get('/{dataset}/{z}/{x}/{y}.terrain')
def tile(dataset: str, z: int, x: int, y: int):
    ds = Dataset.from_name(dataset)
    data = build(ds.gdal_ds, (z, x, y))
    return Response(data, media_type="application/octet-stream", headers={
        'Access-Control-Allow-Origin': '*',
        'Content-Encoding': 'gzip',
    })


@app.get('/{dataset}/preview')
def preview(request: Request, dataset: str):
    ds = Dataset.from_name(dataset)
    return templates.TemplateResponse('preview.html', {
        'request': request,
        'dataset': dataset,
        'bounds': ds.bounds,
    })