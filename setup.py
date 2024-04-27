# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cache', 'cache.algorithm', 'cache.config', 'cache.runners', 'cache.utils']

package_data = \
{'': ['*']}

install_requires = \
['conf>=0.4.1,<0.5.0',
 'fire>=0.5.0,<0.6.0',
 'hydra-core>=1.3.2,<2.0.0',
 'ipywidgets>=8.1.2,<9.0.0',
 'joblib>=1.3.2,<2.0.0',
 'matplotlib>=3.8.3,<4.0.0',
 'numba>=0.59.1,<0.60.0',
 'numpy>=1.26.4,<2.0.0',
 'pandas>=2.2.1,<3.0.0',
 'scipy>=1.12.0,<2.0.0',
 'seaborn>=0.13.2,<0.14.0',
 'tqdm>=4.66.2,<5.0.0']

setup_kwargs = {
    'name': 'Cache',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': '',
    'author_email': '@',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

