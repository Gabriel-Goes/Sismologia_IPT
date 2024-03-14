from setuptools import setup, find_packages
from BaixarFormaOnda import create_event_dirname

setup(
    name="ClassificadorSismologico",
    version="0.1",
    packages=find_packages(),
)

create_event_dirname()
