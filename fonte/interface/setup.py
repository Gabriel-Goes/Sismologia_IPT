from setuptools import setup, find_packages

setup(
    name="FarejadorSismologico",
    version="0.1.0",
    packages=find_packages(where='farejador_eventos/'),
    package_dir={'': 'farejador_eventos/'},
)
