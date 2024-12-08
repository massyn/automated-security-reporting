#!/bin/bash

cd 01-collectors
python wrapper.py
cd ..

cd 02-metrics
python metrics.py
cd ..

cd 03-pipeline
python pipeline.py
cd ..

echo " == end of run =="
