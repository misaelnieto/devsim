#!/bin/bash
echo "Using devsim: `which devsim`"
ln -sf ../../python_packages/ python_packages
ln -sf ../diode/diode_common.py diode_common.py
devsim solar_2d.py
