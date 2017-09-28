from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cf-compare',
    version='1.0.0',
    description='Web app to compare problems solved by two users on codeforces',
    long_description=long_description,
    url='https://github.com/praran26/CF-Compare',
    license='MIT'
)