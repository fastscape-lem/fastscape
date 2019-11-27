import fastscapelib_fortran as fs
import numpy as np
import xsimlab as xs

from .grid import UniformRectilinearGrid2D


@xs.process
class TotalVerticalMotion:
    """Sum up all vertical motions of bedrock and topographic surface,
    respectively.

    Vertical motions may result from external forcing, erosion and/or
    feedback of erosion on tectonics (isostasy).

    """
    # TODO: remove any_upward_vars
    # see https://github.com/benbovy/xarray-simlab/issues/64
    any_upward_vars = xs.group('any_upward')
    bedrock_upward_vars = xs.group('bedrock_upward')
    surface_upward_vars = xs.group('surface_upward')
    surface_downward_vars = xs.group('surface_downward')

    bedrock_upward = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='bedrock motion in upward direction'
    )
    surface_upward = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='topographic surface motion in upward direction'
    )

    def run_step(self):
        sum_any = sum(self.any_upward_vars)

        self.bedrock_upward = sum_any + sum(self.bedrock_upward_vars)

        self.surface_upward = (sum_any +
                               sum(self.surface_upward_vars) -
                               sum(self.surface_downward_vars))


@xs.process
class SurfaceTopography:
    """Update the elevation of the (land and/or submarine) surface
    topography.

    """
    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='surface topography elevation'
    )

    motion_upward = xs.foreign(TotalVerticalMotion, 'surface_upward')

    def finalize_step(self):
        self.elevation += self.motion_upward


@xs.process
class SurfaceToErode:
    """Defines the topographic surface used for the computation of erosion
    processes.

    In this process class, it simply corresponds to the topographic
    surface, unchanged, at the current time step.

    Sometimes it would make sense to compute erosion processes after
    having applied other processes such as tectonic forcing. This
    could be achieved by subclassing.

    """
    topo_elevation = xs.foreign(SurfaceTopography, 'elevation')

    elevation = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='surface elevation before erosion'
    )

    def run_step(self):
        self.elevation = self.topo_elevation


@xs.process
class Bedrock:
    """Update the elevation of bedrock (i.e., land and/or submarine
    basement).

    """
    elevation = xs.variable(
        dims=('y', 'x'),
        intent='inout',
        description='bedrock elevation'
    )

    depth = xs.on_demand(
        dims=('y', 'x'),
        description='bedrock depth below topographic surface'
    )

    bedrock_motion_up = xs.foreign(TotalVerticalMotion, 'bedrock_upward')
    surface_motion_up = xs.foreign(TotalVerticalMotion, 'surface_upward')

    surface_elevation = xs.foreign(SurfaceTopography, 'elevation')

    @depth.compute
    def _depth(self):
        return self.surface_elevation - self.elevation

    def initialize(self):
        if np.any(self.elevation > self.surface_elevation):
            raise ValueError("Encountered bedrock elevation higher than "
                             "topographic surface elevation.")

    def run_step(self):
        self._elevation_next = np.minimum(
            self.elevation + self.bedrock_motion_up,
            self.surface_elevation + self.surface_motion_up
        )

    def finalize_step(self):
        self.elevation = self._elevation_next


@xs.process
class UniformSedimentLayer:
    """Uniform sediment (or regolith, or soil) layer.

    This layer has uniform properties (undefined in this class) and
    generally undergo under active erosion, transport and deposition
    processes.

    """

    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')
    bedrock_elevation = xs.foreign(Bedrock, 'elevation')

    thickness = xs.variable(
        dims=('y', 'x'),
        intent='out',
        description='sediment layer thickness'
    )

    @thickness.compute
    def _get_thickness(self):
        return self.surf_elevation - self.bedrock_elevation

    def initialize(self):
        self.thickness = self._get_thickness()

    def run_step(self):
        self.thickness = self._get_thickness()


@xs.process
class TerrainDerivatives:
    """Compute, on demand, terrain derivatives such as slope or
    curvature.

    """
    shape = xs.foreign(UniformRectilinearGrid2D, 'shape')
    spacing = xs.foreign(UniformRectilinearGrid2D, 'spacing')
    elevation = xs.foreign(SurfaceTopography, 'elevation')

    slope = xs.on_demand(
        dims=('y', 'x'),
        description='terrain local slope'
    )
    curvature = xs.on_demand(
        dims=('y', 'x'),
        description='terrain local curvature'
    )

    @slope.compute
    def _slope(self):
        slope = np.empty_like(self.elevation)
        ny, nx = self.shape
        dy, dx = self.spacing

        fs.slope(self.elevation.ravel(), slope.ravel(), nx, ny, dx, dy)

        return slope

    @curvature.compute
    def _curvature(self):
        curv = np.empty_like(self.elevation)
        ny, nx = self.shape
        dy, dx = self.spacing

        fs.curvature(self.elevation.ravel(), curv.ravel(), nx, ny, dx, dy)

        return curv


@xs.process
class StratigraphicHorizons:
    """Generate a fixed number of stratigraphic horizons.

    A horizon is active, i.e., it tracks the evolution of the
    land/submarine topographic surface until it is "frozen" at a given
    time. Beyond this freezing (or deactivation) time, the horizon
    will only be affected by tectonic deformation and/or erosion.

    To compute diagnostics on those horizons, you can create a
    subclass where you can add "on_demand" variables.

    """
    freeze_time = xs.variable(
        dims='horizon',
        description='horizon freezing (deactivation) time'
    )

    active = xs.variable(
        dims='horizon',
        intent='out',
        description='whether the horizon is active or not'
    )

    surf_elevation = xs.foreign(SurfaceTopography, 'elevation')
    elevation_motion = xs.foreign(TotalVerticalMotion, 'surface_upward')
    bedrock_motion = xs.foreign(TotalVerticalMotion, 'bedrock_upward')

    elevation = xs.variable(
        dims=('horizon', 'y', 'x'),
        intent='out',
        description='elevation of horizon surfaces'
    )

    @xs.runtime(args='sim_start')
    def initialize(self, start_time):
        if np.any(self.freeze_time < start_time):
            raise ValueError("'freeze_time' value must be greater than the "
                             "time of the beginning of the simulation")

        self.elevation = np.repeat(self.surf_elevation[None, :, :],
                                   self.freeze_time.size,
                                   axis=0)

        self.active = np.full_like(self.freeze_time, True, dtype=bool)

    @xs.runtime(args='step_start')
    def run_step(self, current_time):
        self.active = current_time < self.freeze_time

    def finalize_step(self):
        elevation_next = self.surf_elevation + self.elevation_motion

        self.elevation[self.active] = elevation_next

        self.elevation[~self.active] = np.minimum(
            self.elevation[~self.active] + self.bedrock_motion,
            elevation_next
        )
