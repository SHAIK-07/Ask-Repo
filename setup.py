# 1st install --> pip install setuptools wheel
# 2nd in terminal give #python setup.py install

from setuptools import find_packages,setup
from typing import List



setup(
name='Code-Analyzer',
version='0.0.1',
author='shaik',
author_email='shaik.hidaythulla07@gmail.com',
packages=find_packages()
)