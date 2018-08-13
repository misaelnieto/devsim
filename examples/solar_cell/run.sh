#!/bin/bash
echo "Using devsim: `which devsim`"
ln -sf ../../python_packages/ python_packages
devsim solar_2d.py
