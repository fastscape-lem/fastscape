from setuptools import setup, find_packages
from os.path import exists

import versioneer


setup(name='fastscape',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=('A fast, versatile and user-friendly '
                   'landscape evolution model'),
      url='http://github.com/fastscape-lem/fastscape',
      maintainer='Benoit Bovy',
      maintainer_email='benbovy@gmail.com',
      license='BSD-Clause3',
      keywords='python landscape evolution modelling',
      packages=find_packages(),
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      python_requires='>=3.5',
      install_requires=['xarray-simlab >= 0.3.0'],
      # tests_require=['pytest >= 3.3.0'],
      zip_safe=False)
