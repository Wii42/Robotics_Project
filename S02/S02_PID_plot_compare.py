# run this plotting script for comparing several log file data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import glob

# find all files
FILENAME='./logPID_*'
files = sorted(glob.glob(FILENAME))[25:-2]

print(files)

df = pd.DataFrame()
legend = {}

for f in files:
    # get test number
    test = f.split('_')[-1].split('.')[0]
    # get data from CSV file
    log = pd.read_csv(f, index_col=0)
    if log.size == 0:
        continue
    log['test'] = test
    # get legend info
    legend[test] = [log['K'][0],log['T_I'][0],log['T_D'][0]]
    # drop columns K,T_I,T_D
    log.drop(log.columns[0:3], axis=1, inplace = True)
    df = pd.concat([df,log])


# plot data
boxplot = df.boxplot(column=['P','I','D','ds','left speed','right speed'], by='test',figsize=(12,9),layout=(2, 3),grid=False)

ax = plt.gca()
for i,e in enumerate(legend.keys()) :
    ax.annotate('test '+str(e)+': '+str(legend[e]),(0.75,0.03*i+0.1),xycoords='figure fraction')

plt.savefig('PID_compare.png')
plt.show()
