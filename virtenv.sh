#!/bin/bash
virtualenv -p /usr/bin/python2.7 python
source python/bin/activate

pip install colorlog
pip install termcolor
pip install python-dateutil
pip install numpy
pip install matplotlib
pip install sphinx
