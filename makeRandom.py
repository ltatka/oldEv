import evolUtils as ev
import os

nModels = 1000
nSpecies = 3
nReactions = 9



save_dir = '/home/hellsbells/Desktop/3nodeControls'
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

os.chdir(save_dir)

for i in range(nModels):
    model = ev.makeModel(nSpecies, nReactions)
    astr = ev.convertToAntimony2(model)
    with open(f'{str(i)}.ant', 'w') as f:
        f.write(astr)
        f.close()



print('done')