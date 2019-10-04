import xsimlab as xs

from .main_drivers import TotalErosion
from .tectonics import BaseVerticalUplift


@xs.process
class BaseIsostasy:
    """Base class for isostasy.

    Do not use this base class directly in a model! Use one of its
    subclasses instead.

    However, if you need one or several of the variables declared here
    in another process, it is preferable to pass this base class in
    :func:`xsimlab.foreign`.

    """
    isostasy = xs.variable(
        dims=('y', 'x'),
        intent='out',
        group='bedrock_upward'
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

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.isostasy = self.i_coef * self.erosion


@xs.process
class LocalIsostasyUplift(BaseLocalIsostasy):
    """Local isostasic effect of rock uplift."""

    uplift = xs.foreign(BaseVerticalUplift, 'uplift')

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.isostasy = -1. * self.i_coef * self.uplift


@xs.process
class LocalIsostasyErosionUplift(BaseLocalIsostasy):
    """Local isostatic effect of both erosion and tectonic uplift."""

    erosion = xs.foreign(TotalErosion, 'erosion')
    uplift = xs.foreign(BaseVerticalUplift, 'uplift')

    @xs.runtime(args='step_delta')
    def run_step(self, dt):
        self.isostasy = self.i_coef * (self.erosion - self.rock_uplift)
