import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .boundary import BorderBoundary
from .erosion import TotalErosion
from .grid import UniformRectilinearGrid2D
from .main import SurfaceTopography
from .tectonics import TectonicForcing


@xs.process
class BaseIsostasy:
    """Base class for isostasy.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    # TODO: group=['bedrock_upward', 'surface_upward']
    # see https://github.com/benbovy/xarray-simlab/issues/64
    rebound = xs.variable(
        dims=('y', 'x'),
        intent='out',
        group='any_upward',
        description='isostasic rebound due to material loading/unloading'
    )


@xs.process
class BaseLocalIsostasy(BaseIsostasy):
    """Base class for local isostasy.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    i_coef = xs.variable(description='local isostatic coefficient')


@xs.process
class LocalIsostasyErosion(BaseLocalIsostasy):
    """Local isostasic effect of erosion."""

    erosion = xs.foreign(TotalErosion, 'erosion')

    def run_step(self):
        self.rebound = self.i_coef * self.erosion


@xs.process
class LocalIsostasyTectonics(BaseLocalIsostasy):
    """Local isostasic effect of tectonic forcing."""

    bedrock_upward = xs.foreign(TectonicForcing, 'bedrock_upward')

    def run_step(self):
        self.rebound = -1. * self.i_coef * self.bedrock_upward


@xs.process
class LocalIsostasyErosionTectonics(BaseLocalIsostasy):
    """Local isostatic effect of both erosion and tectonic forcing.

    This process makes no distinction between the density of rock and
    the density of eroded material (one single coefficient is used).

    """
    erosion = xs.foreign(TotalErosion, 'erosion')
    surface_upward = xs.foreign(TectonicForcing, 'surface_upward')

    def run_step(self):
        self.rebound = self.i_coef * (self.erosion - self.surface_upward)


@xs.process
class Flexure(BaseIsostasy):
    """Flexural isostatic effect of both erosion and tectonic
    forcing.

    """
    lithos_density = xs.variable(
        dims=[(), ('y', 'x')],
        description='lithospheric rock density'
    )
    asthen_density = xs.variable(
        description='asthenospheric rock density'
    )
    e_thickness = xs.variable(
        description='effective elastic plate thickness'
    )

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    length = xs.foreign(UniformRectilinearGrid2D, 'length')

    ibc = xs.foreign(BorderBoundary, 'ibc')

    elevation = xs.foreign(SurfaceTopography, 'elevation')

    erosion = xs.foreign(TotalErosion, 'erosion')
    surface_upward = xs.foreign(TectonicForcing, 'surface_upward')

    def run_step(self):
        ny, nx = self.shape
        yl, xl = self.length

        lithos_density = np.broadcast_to(
            self.lithos_density, self.shape).flatten()

        elevation = self.elevation.ravel()
        diff = (self.surface_upward - self.erosion).ravel()

        # set elevation pre and post rebound
        elevation_pre = elevation - diff
        elevation_post = elevation_pre.copy()

        fs.flexure(elevation_post, elevation, nx, ny, xl, yl,
                   lithos_density, self.asthen_density, self.e_thickness,
                   self.ibc)

        self.rebound = (elevation_post - elevation_pre).reshape(self.shape)
