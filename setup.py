from setuptools import setup, find_packages

setup(
    name="ClassificadorSismologico",
    version="0.4",
    packages=find_packages(where='fonte'),
    package_dir={'': 'fonte'},
)
