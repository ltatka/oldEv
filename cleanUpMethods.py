import tellurium as te
import roadrunner
import copy, sys, os, math, getopt, json, time, zipfile, shutil
from scipy.signal import find_peaks
import json


def readSavedRun(fileName):
    zf = zipfile.ZipFile(fileName, 'r')
    data = zf.read('summary.txt').decode("utf-8")
    data = data.splitlines()
    numGenerations = int(data[5].split('=')[1])
    numPopulation = int(data[6].split('=')[1])
    # print ("Number of Generations = ", numGenerations)
    # print ("Size of population in each generation =", numPopulation)
    return zf

def getNumGenerations(zip_file):
    data = zip_file.read('summary.txt').decode("utf-8")
    data = data.splitlines()
    return int(data[5].split('=')[1])



def readModel(zf, generation, individual):
    fileName = "populations/generation_" + str(generation) + '/individual_' + str(individual) + '.txt'
    ant = zf.read(fileName).decode("utf-8")
    ant = ant.splitlines()
    if ant[0].startswith('#'):
        ant = ant[1:]
    zf.close()
    return ant

def test_readModel():
    zf = readSavedRun("C:\\Users\\tatka\\Desktop\\Models\\FAIL\\FAIL_Model_128987634590189990.zip")
    ant = readModel(zf, 499, 0)
    print(ant)


def findStart(lines):
    for index, line in enumerate(lines):
        line = line.split(' ')
        if line[0] != 'var' and (line[0] != 'ext'):
            return index


def findEnd(lines):
    for index, line in enumerate(lines):
        if line[0] == 'k':
            return index


def countEig(eig):
    numConjugates = 0
    for eigenvalue in eig:
        if abs(eigenvalue.imag) > 0.1:
            numConjugates += 1
    return numConjugates


# Return True if the model is damped
def isModelDampled(antstr):
    dampled = False
    r = te.loada(antstr)
    try:
        m = r.simulate(0, 100, 100)
        peaks, _ = find_peaks(m[:, 2], prominence=1)
        if len(peaks) == 0:
            dampled = True
        else:
            # It could be damped
            try:
                m = r.simulate(0, 10, 500)
                peaks, _ = find_peaks(m[:, 2], prominence=1)
                if len(peaks) == 0:
                    dampled = True

            except Exception:
                dampled = True

    except Exception:
        dampled = True
    return dampled


def choose_iter(elements, length):
    for i in range(len(elements)):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i + 1:len(elements)], length - 1):
                yield (elements[i],) + next


def choose(l, k):
    return list(choose_iter(l, k))


def nChooseK(n, k):
    return int(math.factorial(n)/ (math.factorial(k) * math.factorial(n-k)))

def stringToList(indices):
    indices = indices.split(', ')
    indices[0] = indices[0][1:]
    if len(indices) > 1:
        indices[-1] = indices[-1][:-2]
    for i in range(len(indices)):
        indices[i] = int(indices[i])
    return indices

def makeNonEssRxnDict(modelPath, savePath):
    # e.g. file = './data.json'
    modelPath = 'C:\\Users\\tatka\\Desktop\\Models\\OSCILLATOR'
    indices_dict = {}
    for filename in os.listdir(modelPath):
        os.chdir(modelPath)
        if filename.startswith('Model'):
            modelPath = os.path.join(modelPath, filename)
            os.chdir(modelPath)
            for file in os.listdir(modelPath):
                if file.endswith('summary.txt'):
                    with open(file, "r") as f:
                        lines = f.readlines()
                        f.close()
                    model = lines[0].split(' = ')[1][:-5]
                    indices = lines[4].split(' = ')[1]
                    indices = stringToList(indices)
                    indices_dict[model] = indices
    with open(os.path.join(modelPath, 'oscillators_dict.json'), 'w') as f:
        json.dump(indices_dict, f)

def loadNonEssRxnDict(path):
    with open(path, 'r') as f:
        idx_dict = json.load(f)
    return idx_dict

def loadAntimonyText(path):
    with open(path, "r") as f:
        lines = f.readlines()
        f.close()
    # First line is comment for fitness, ignore
    if lines[0].startswith('#'):
        lines = lines[1:]
    return lines

def loadAntimonyText_noLines(path):
    # THIS WILL INCLUDE THE FIRST COMMENTED LINE!
    with open(path, "r") as f:
        ant = f.read()
        f.close()
    return ant