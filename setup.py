from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in vortex/__init__.py
from vortex import __version__ as version

setup(
	name="vortex",
	version=version,
	description="Whatsapp message",
	author="8848digital",
	author_email="prateek@8848digital.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
