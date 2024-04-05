# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ura_efris/__init__.py
from ura_efris import __version__ as version

setup(
	name="ura_efris",
	version=version,
	description="intergration with ura",
	author="mututa paul",
	author_email="mututapaul01@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
