#!/bin/bash

for ((count=0; count<10; count++))
do
    python batchrun.py -r 100
done
exit 0
