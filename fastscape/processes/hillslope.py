import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .surface import SurfaceTopography


@xs.process
class LinearDiffusion:
    """Hillslope erosion by diffusion."""

    diffusivity = xs.variable(dims=[(), ('y', 'x')], description='diffusivity')
    erosion = xs.variable(dims=('y', 'x'), intent='out', group='erosion')

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    elevation = xs.foreign(SurfaceTopography, 'elevation')
    fs_context = xs.foreign(FastscapelibContext, 'context')

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        kd = np.broadcast_to(self.diffusivity, self.shape).flatten()
        self.fs_context.kd = kd

        # we don't use the kdsed fastscapelib-fortran feature directly
        # see class DiffusivityBedrockSoil
        self.fs_context.kdsed = -1.

        # fs.diffusion() updates elevation in-place: not desired here
        elevation = self.fs_context.h.copy()

        fs.diffusion()

        erosion_flat = elevation - self.fs_context.h
        self.erosion = erosion_flat.reshape(self.shape)

        self.fs_context.h = elevation


@xs.process
class DiffusivityBedrockSoil:
    """Use a different diffusivity value whether or
    not bedrock is covered by a soil layer.

    """
    bedrock = xs.variable(dims=[(), ('y', 'x')],
                          description='diffusivity (bedrock)')
    soil = xs.variable(description='diffusivity (soil)')

    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    diffusivity = xs.foreign(LinearDiffusion, 'diffusivity', intent='out')

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        # TODO: get soil thickness (surface - bedrock)
        self.diffusivity = np.broadcast_to(self.bedrock, self.shape)
