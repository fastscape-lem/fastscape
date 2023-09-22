import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .boundary import BorderBoundary
from .context import FastscapelibContext
from .grid import UniformRectilinearGrid2D
from .main import Bedrock, SurfaceToErode, SurfaceTopography


@xs.process
class TectonicForcing:
    """Sum up all tectonic forcing processes and their effect on the
    vertical motion of the bedrock surface and the topographic
    surface, respectively.

    """

    bedrock_forcing_vars = xs.group("bedrock_forcing_upward")
    surface_forcing_vars = xs.group("surface_forcing_upward")

    bedrock_upward = xs.variable(
        dims=[(), ("y", "x")],
        intent="out",
        groups="bedrock_upward",
        description="imposed vertical motion of bedrock surface",
    )

    surface_upward = xs.variable(
        dims=[(), ("y", "x")],
        intent="out",
        groups="surface_upward",
        description="imposed vertical motion of topographic surface",
    )

    grid_area = xs.foreign(UniformRectilinearGrid2D, "area")

    domain_rate = xs.on_demand(description="domain-integrated volumetric tectonic rate")

    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        self._dt = dt

        self.bedrock_upward = sum(self.bedrock_forcing_vars)
        self.surface_upward = sum(self.surface_forcing_vars)

    @domain_rate.compute
    def _domain_rate(self):
        return np.sum(self.surface_upward) * self.grid_area / self._dt


@xs.process
class SurfaceAfterTectonics(SurfaceToErode):
    """Used for the computation erosion processes after
    applying tectonic forcing.

    """

    topo_elevation = xs.foreign(SurfaceTopography, "elevation")

    forced_motion = xs.foreign(TectonicForcing, "surface_upward")

    elevation = xs.variable(
        dims=("y", "x"), intent="out", description="surface elevation before erosion"
    )

    def run_step(self):
        self.elevation = self.topo_elevation + self.forced_motion


@xs.process
class BlockUplift:
    """Vertical tectonic block uplift.

    Automatically resets uplift to zero at grid borders where
    'fixed_value' boundary conditions are set.

    """

    rate = xs.variable(dims=[(), ("y", "x")], description="uplift rate")

    shape = xs.foreign(UniformRectilinearGrid2D, "shape")
    status = xs.foreign(BorderBoundary, "border_status")
    fs_context = xs.foreign(FastscapelibContext, "context")

    uplift = xs.variable(
        dims=[(), ("y", "x")],
        intent="out",
        groups=["bedrock_forcing_upward", "surface_forcing_upward"],
        description="imposed vertical uplift",
    )

    def initialize(self):
        # build uplift rate binary mask according to border status
        self._mask = np.ones(self.shape)

        _all = slice(None)
        slices = [(_all, 0), (_all, -1), (0, _all), (-1, _all)]

        for status, border in zip(self.status, slices):
            if status == "fixed_value":
                self._mask[border] = 0.0

    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        rate = np.broadcast_to(self.rate, self.shape) * self._mask

        self.uplift = rate * dt


@xs.process
class TwoBlocksUplift:
    """Set two blocks separated by a clip plane, with different
    uplift rates.

    """

    x_position = xs.variable(description="position of the clip plane along the x-axis", static=True)

    rate_left = xs.variable(description="uplift rate of the left block")
    rate_right = xs.variable(description="uplift rate of the right block")

    shape = xs.foreign(UniformRectilinearGrid2D, "shape")
    x = xs.foreign(UniformRectilinearGrid2D, "x")

    uplift = xs.variable(
        dims=[(), ("y", "x")],
        intent="out",
        groups=["bedrock_forcing_upward", "surface_forcing_upward"],
        description="imposed vertical uplift",
    )

    def initialize(self):
        # align clip plane position
        self._x_idx = np.argmax(self.x > self.x_position)

    @xs.runtime(args="step_delta")
    def run_step(self, dt):
        rate = np.full(self.shape, self.rate_left)

        rate[:, self._x_idx :] = self.rate_right

        self.uplift = rate * dt


@xs.process
class HorizontalAdvection:
    """Horizontal rock advection imposed by a velocity field."""

    u = xs.variable(dims=[(), ("y", "x")], description="velocity field component in x-direction")
    v = xs.variable(dims=[(), ("y", "x")], description="velocity field component in y-direction")

    shape = xs.foreign(UniformRectilinearGrid2D, "shape")
    fs_context = xs.foreign(FastscapelibContext, "context")

    bedrock_elevation = xs.foreign(Bedrock, "elevation")
    surface_elevation = xs.foreign(SurfaceTopography, "elevation")

    bedrock_veffect = xs.variable(
        dims=("y", "x"),
        intent="out",
        groups="bedrock_forcing_upward",
        description="vertical effect of advection on bedrock surface",
    )

    surface_veffect = xs.variable(
        dims=("y", "x"),
        intent="out",
        groups="surface_forcing_upward",
        description="vertical effect of advection on topographic surface",
    )

    def run_step(self):
        self.fs_context["vx"] = np.broadcast_to(self.u, self.shape).flatten()
        self.fs_context["vy"] = np.broadcast_to(self.v, self.shape).flatten()

        # bypass fastscapelib-fortran state
        self.fs_context["h"] = self.surface_elevation.flatten()
        self.fs_context["b"] = self.bedrock_elevation.flatten()

        fs.advect()

        h_advected = self.fs_context["h"].reshape(self.shape)
        self.surface_veffect = h_advected - self.surface_elevation

        b_advected = self.fs_context["b"].reshape(self.shape)
        self.bedrock_veffect = b_advected - self.bedrock_elevation
