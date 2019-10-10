.. _processes:

Processes
=========

Fastscape provides a few dozens of processes, i.e., Python classes
decorated with :func:`xsimlab.process`, serving as building blocks for
the creation of custom landscape evolution models.

Those processes are presented by thematic below. You can import any of
them from the ``processes`` subpackage, e.g.,

.. code-block:: python

    from fastscape.processes import SurfaceTopography

Rather than building models from scratch, you might better want to
pick one of the model presets presented in the :doc:`models` section
and customize it using :meth:`xsimlab.Model.update_processes` or
:meth:`xsimlab.Model.drop_processes`.

For more help on how to use these process classes to create new
:class:`xsimlab.Model` objects, see the :doc:`examples` section or
`xarray-simlab's documentation`_.

.. _`xarray-simlab's documentation`: http://xarray-simlab.readthedocs.io/

Main interfaces & drivers
-------------------------

Defined in ``fastscape/processes/main.py``

These processes define (update them over time) the main interfaces
used in landscape evolution models, such as the topographic surface,
the bedrock level or several stratigraphic horizons.

.. currentmodule:: fastscape.processes
.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   Bedrock
   SurfaceTopography
   SurfaceToErode
   StratigraphicHorizons
   TerrainDerivatives
   TotalVerticalMotion
   UniformSedimentLayer

Grid
----

Defined in ``fastscape/processes/grid.py``

Processes that define the model grids used in Fastscape and their
properties (shape, spacing, length, etc.).

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   UniformRectilinearGrid2D
   RasterGrid2D

Boundaries
----------

Defined in ``fastscape/processes/boundary.py``

Processes that can be used for setting the boundary conditions.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   BorderBoundary

Initial conditions
------------------

Defined in ``fastscape/processes/initial.py``

Processes that mostly serve as common "presets" for various initial
conditions (e.g., initial topography, erosion pre-history, initial
sediment cover).

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   BareRockSurface
   Escarpment
   FlatSurface
   NoErosionHistory

Tectonics
---------

Defined in ``fastscape/processes/tectonics.py``

All processes (generic or specific) about tectonic forcing.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   BlockUplift
   HorizontalAdvection
   SurfaceAfterTectonics
   TectonicForcing
   TwoBlocksUplift

Flow routing
------------

Defined in ``fastscape/processes/flow.py``

Processes that route flow on the topographic surface.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   FlowRouter
   SingleFlowRouter
   MultipleFlowRouter
   AdaptiveFlowRouter

Erosion / deposition
--------------------

Defined in ``fastscape/processes/erosion.py``

General erosion (or deposition) processes.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   TotalErosion

Channel processes
-----------------

Defined in ``fastscape/processes/channel.py``

River channel erosion, transport and/or deposition processes.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   ChannelErosion
   DifferentialStreamPowerChannel
   DifferentialStreamPowerChannelTD
   StreamPowerChannel
   StreamPowerChannelTD

Hillslope processes
-------------------

Defined in ``fastscape/processes/hillslope.py``

Hillslope erosion, transport and/or deposition processes.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   LinearDiffusion
   DifferentialLinearDiffusion

Marine processes
----------------

Defined in ``fastscape/processes/marine.py``

Generic or specialized processes used to model (sediment or other)
dynamics in submarine environments.

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   MarineSedimentTransport
   Sea

Isostasy
--------

Defined in ``fastscape/processes/isostasy.py``

Processes for modeling the local or flexural isostatic effect of
erosion and/or other driving processes (tectonics).

.. autosummary::
   :nosignatures:
   :template: process_class.rst
   :toctree: _api_generated/

   BaseIsostasy
   BaseLocalIsostasy
   Flexure
   LocalIsostasyErosion
   LocalIsostasyErosionTectonics
   LocalIsostasyTectonics
