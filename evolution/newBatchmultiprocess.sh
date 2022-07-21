#!/bin/bash
for ((count=0; count<500; count++))
do
    python batchrun.py --runs=100 --newConfigFile=newConfigFile.json
done
exit 0
