import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .main import SurfaceToErode, UniformSedimentLayer


@xs.process
class LinearDiffusion:
    """Hillslope erosion by diffusion."""

    diffusivity = xs.variable(
        dims=[(), ("y", "x")], description="diffusivity (transport coefficient)"
    )
    erosion = xs.variable(dims=("y", "x"), intent="out", groups="erosion")

    shape = xs.foreign(UniformRectilinearGrid2D, "shape")
    elevation = xs.foreign(SurfaceToErode, "elevation")
    fs_context = xs.foreign(FastscapelibContext, "context")

    def run_step(self):
        kd = np.broadcast_to(self.diffusivity, self.shape).flatten()
        self.fs_context["kd"] = kd

        # we don't use the kdsed fastscapelib-fortran feature directly
        # see class DifferentialLinearDiffusion
        self.fs_context["kdsed"] = -1.0

        # bypass fastscapelib-fortran global state
        self.fs_context["h"] = self.elevation.flatten()

        fs.diffusion()

        erosion_flat = self.elevation.ravel() - self.fs_context["h"]
        self.erosion = erosion_flat.reshape(self.shape)


@xs.process
class DifferentialLinearDiffusion(LinearDiffusion):
    """Hillslope differential erosion by diffusion.

    Diffusivity may vary depending on whether the topographic surface
    is bare rock or covered by a soil (sediment) layer.

    """

    diffusivity_bedrock = xs.variable(dims=[(), ("y", "x")], description="bedrock diffusivity")
    diffusivity_soil = xs.variable(dims=[(), ("y", "x")], description="soil (sediment) diffusivity")

    diffusivity = xs.variable(dims=("y", "x"), intent="out", description="differential diffusivity")

    soil_thickness = xs.foreign(UniformSedimentLayer, "thickness")

    def run_step(self):
        self.diffusivity = np.where(
            self.soil_thickness <= 0.0, self.diffusivity_bedrock, self.diffusivity_soil
        )

        super().run_step()
