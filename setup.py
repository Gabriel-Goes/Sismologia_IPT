from setuptools import setup, find_packages

setup(
    name="ClassificadorSismologico",
    version="0.4.0",
    packages=find_packages(where='fonte'),
    package_dir={'': 'fonte'},
)
