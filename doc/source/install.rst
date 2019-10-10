.. _install:

Install fastscape
=================

Required dependencies
---------------------

- Python 3
- `xarray <http://xarray.pydata.org>`__
- `xarray-simlab <http://xarray-simlab.readthedocs.io>`__
- `fastscapelib-fortran <https://github.com/fastscape-lem/fastscapelib-fortran>`__

Install using conda
-------------------

fastscape can be installed or updated using conda_::

  $ conda install fastscape -c conda-forge

This installs fastscape and all the required dependencies.

the fastscape conda package is maintained on the `conda-forge`_
channel.

.. _conda-forge: https://conda-forge.org/
.. _conda: https://conda.io/docs/

Install from source
-------------------

Be sure you have the required dependencies installed first. You might
consider using conda_ to install them::

    $ conda install xarray-simlab fastscapelib-f2py -c conda-forge

A good practice (especially for development purpose) is to install the packages
in a separate environment, e.g. using conda::

    $ conda create -n fastscape python=3.7 xarray-simlab fastscapelib-f2py -c conda-forge
    $ source activate fastscape

Then you can clone the ``fastscape`` git repository and install it
using ``pip`` locally::

    $ git clone https://github.com/fastscape-lem/fastscape.git
    $ cd fastscape
    $ pip install .

For development purpose, use the following command::

    $ pip install -e .

Import fastscape
----------------

To make sure that ``fastscape`` is correctly installed, try import it in a
Python console::

    >>> import fastscape
