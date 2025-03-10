# run this plotting script for showing one log file data (the last one)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import glob

# config
FILENAME='./logPID*'

# use last
file = sorted(glob.glob(FILENAME))[-1]
print("using log file "+file)

# get data from CSV file
log = pd.read_csv(file, index_col=0)
log.drop(log.columns[0:3], axis=1, inplace = True)

# plot data
log.plot(subplots=True,figsize=(12,9))
plt.legend(loc='upper right')
plt.savefig('PID_single.png')
plt.show()
