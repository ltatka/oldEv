# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 20:52:33 2021

@author: hsauro
"""


from numba import jit

import tellurium as te
import roadrunner
import teUtils as tu
import numpy as np
import random
import matplotlib.pyplot as plt
import readObjData
import evalFitness
from uModel import TModel_
import copy, sys, os, math, getopt, json, time, zipfile
import evolUtils, uModel
from uModel import TReaction
from pprint import pprint
from datetime import date
from datetime import datetime
# import keyboard
from uLoadCvode import TCvode
import uLoadCvode




tu.buildNetworks.Settings.ReactionProbabilities.UniUi = 0.1
tu.buildNetworks.Settings.ReactionProbabilities.UniBi = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiUni = 0.4
tu.buildNetworks.Settings.ReactionProbabilities.BiBi = 0.1


# [UNIUNI, [6], [1], 0.4044825260841083]




if __name__ == "__main__":
    # ---------------------------------------------------------------------

    ## This is the real default config
    # defaultConfig = {"maxGenerations": 450,
    #           "sizeOfPopulation": 100,
    #           "numSpecies": 10,
    #           "numReactions": 14,
    #           "rateConstantScale": 50,
    #           "probabilityMutateRateConstant": 0.7, # 0.9 much worse
    #           "percentageCloned": 0.1,
    #           "percentageChangeInParameter": 0.15,
    #           "seed": -1,  # means no specific seed
    #           "threshold": 10.5, # a fitness below this we stop
    #           "frequencyOfOutput": 10,
    #           "multi": {"item 1": "item 2"},
    #           "key2": "value2"}

    defaultConfig = {"maxGenerations": 450,
                     "massConserved": True,
                     "toZip": False,
                     "sizeOfPopulation": 40,
                     "numSpecies": 3,
                     "numReactions": 9,
                     "rateConstantScale": 50,
                     "probabilityMutateRateConstant": 0.7,  # 0.9 much worse
                     "percentageCloned": 0.1,
                     "percentageChangeInParameter": 0.15,
                     "seed": -1,  # means no specific seed
                     "threshold": 10.5,  # a fitness below this we stop
                     "frequencyOfOutput": 10,
                     "multi": {"item 1": "item 2"},
                     "key2": "value2"}

    # todo you should use argparse for this in python. Its waaaaay easier and standard practice.
    seed = -1
    maxGenerations = -1
    newConfigFile = ''
    argv = sys.argv[1:]
    options, args = getopt.getopt(argv, 's:g:c:hv', [])
    for opt, arg in options:
        if opt in ('-s', ''):
            seed = int(arg)
        if opt in ('-g', ''):
            maxGenerations = int(arg)
        if opt in ('-c', ''):
            newConfigFile = arg
            if not newConfigFile.endswith('.json'):
                newConfigFile += '.json'
            print(newConfigFile + ' in use')
        if opt in ('-v', ''):
            print("version 1.0")
            sys.exit()
        if opt in ('-h', ''):
            print("Help:")
            print("Set the seed:  -s 54545353")
            print("Set the number of generations to use:  -g 1000")
            sys.exit()

    print("------------------------------")
    print("Press ctrl+q to interupt a run")
    print("------------------------------\n")
    if not os.path.exists('defaultConfig.json'):
        print("not os")
        with open('defaultConfig.json', 'w') as f:
            json.dump(defaultConfig, f)

    if newConfigFile == '':
        print("Default configuration in use")
        currentConfig = defaultConfig
    else:
        currentConfig = newConfigFile()

    # revert to default if not set
    if maxGenerations == -1:
        maxGenerations = currentConfig['maxGenerations']

    print("Maximum Generations = ", maxGenerations)

    objectiveData = evolUtils.readObjectiveFunction()
    # seed can be set at the cmd line using -s 1234
    # otherwise check config file, if that is not set
    # draw a random seed
    if seed == -1:
        if defaultConfig['seed'] == -1:
            seed = random.randrange(sys.maxsize)
        else:
            seed = currentConfig['seed']
    print('seed = ', seed)
    # seed = 456789
    random.seed(seed)

    tu.buildNetworks.Settings.allowMassViolatingReactions = not currentConfig['massConserved']
    tu.buildNetworks.Settings.rateConstantScale = currentConfig['rateConstantScale']

    # Create initial random population
    sizeOfPopulation = currentConfig['sizeOfPopulation']
    population = []
    for i in range(sizeOfPopulation):
        amodel = evolUtils.makeModel(currentConfig['numSpecies'], currentConfig['numReactions'])
        population.append(amodel)

    model = population[0]
    topElite = math.trunc(defaultConfig['percentageCloned'] * sizeOfPopulation)

    # Main loop
    fitnessArray = []
    startTime = time.time()
    for gen in range(0, maxGenerations):


        # Create the next population
        newPopulation = []
        if gen % currentConfig['frequencyOfOutput'] == 0:
            print(flush=True)
            print("gen[" + str(gen) + "] fitness=",
                  "{:.4f}".format(population[0].fitness),
                  str(len(population[0].reactions)), end='', flush=True)
        else:
            print('.', end='', flush=True)

        # Copy over random elite of the population
        candidates = list(range(sizeOfPopulation))
        elites_idx = random.choices(candidates, k=topElite)
        for i in elites_idx:
            newPopulation.append(uModel.clone(population[i]))

        # For the remainder use tournament selction on pairs of
        # individuals, picking the best and mutating it.
        remainder = sizeOfPopulation - topElite

        # For the remainder use tournament selction on pairs of
        # individuals, picking the best and mutating it.
        remainder = sizeOfPopulation - topElite
        for i in range(remainder):
            idx = random.choices(candidates, k=1)
            amodel = uModel.clone(population[idx[0]])
            if random.random() > currentConfig['probabilityMutateRateConstant']:
                evolUtils.mutateReaction(amodel)
            else:
                n, change = evolUtils.mutateRateConstant(amodel)
                amodel.reactions[n].rateConstant += change
            newPopulation.append(amodel)



        population = newPopulation
        evolUtils.savePopulation(gen, population)

    saveFileName = "Control_" + str(seed) + ".ant"
    astr = evolUtils.convertToAntimony2(newPopulation[0])
    with open(saveFileName, "w") as f:
        f.write(astr)
        f.close()