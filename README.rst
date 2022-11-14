Terratile
=========

Installation
------------

Build requirements (package names in Ubuntu are shown in parentheses):

* GDAL library (``libgdal20`` and ``libgdal-dev``)
* ZLib library (``zlib1g``, ``zlib1g-dev``)
* C++ compiler and CMake (``build-essential`` and ``cmake``)
* Python 3.8+ with header files (``python-dev`` or ``python3-dev``)

Install into virtualenv:

.. code-block::

    $ python3 -m venv env
    $ . env/bin/activate
    $ pip install git+https://github.com/nextgis/terratile.git

Usage example
-------------

.. code-block::

    import terratile
    from osgeo import gdal

    ds = gdal.Open(path_to_dataset, gdal.GA_ReadOnly)
    data = terratile.mesh_tile(ds, (z, x, y))

Terrain tile server
-------------------

Install terratile with ``[server]`` option:

.. code-block::

    $ pip install git+https://github.com/nextgis/terratile.git#egg=terratile[server]

Put some geotiff to current directory (``demo.tiff`` in example) and start
terrain tile server with ``uvicorn``:

.. code-block::

    $ uvicorn terratile.server:app --workers 4

Go to http://localhost:8000/demo/preview to preview terrain tiles with simple
Cesium frontend. Tiles for ``demo.tiff`` are located in
``http://localhost:8000/demo/{z}/{x}/{y}.terrain``. Metadata file ``layer.json``
is available at ``http://localhost:8000/demo/layer.json``.
