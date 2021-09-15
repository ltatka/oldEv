# -*- coding: utf-8 -*-
"""
Created on Sat May  1 22:11:57 2021

@author: hsauro & ltatka
"""

import os, sys, getopt 
import time
from datetime import date
from datetime import datetime
import multiprocessing
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-r", default=10, type=int, help="Change the number of evolution trials")
parser.add_argument("-multiprocess", default="True", type=str, help="Enable or disable multiprocessing")

def toBool(args):
    multiprocess = args.multiprocess.upper()
    if multiprocess.startswith("T"):
        return True
    else:
        return False

def runEvolution():
    os.system('python evolve.py')


       
print ("Batch set up for " + str (args.r) + " runs")
today = date.today()
now = datetime.now()
print ("Run Started on: ", today.strftime("%b-%d-%Y"))
print ("at time: ", now.strftime("%H:%M:%S"), '\n')
start = time.time()

# If multiprocessing
if toBool(args):
    processes = []
    for i in range(args.r):
        p = multiprocessing.Process(target=runEvolution)
        processes.append(p)
        p.start()
    for process in processes:
        process.join()
else:
    for i in range(args.r):
        runEvolution()

print ("Time taken to do batch runs = ", time.time() - start)
# for i in range (numberOfRuns):
#     print ("-----------------------------------------------------")
#     print (" --- BATCH NUMBER --- " + str (i+1) + ' out of ' + str (numberOfRuns) + ' total.')
#     print ("-----------------------------------------------------")
#     os.system('python evolve.py' + ' -g 500')
#
# print ("Time taken to do batch runs = ", time.time() - start)
