#!/bin/bash

# For installing from testpypi:
# pip install --index-url https://test.pypi.org/simple/ pymilldb
python3 -m twine upload --repository testpypi dist/*
