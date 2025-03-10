# run the code to plot the ground sensor results 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# get data from CSV file
csv = pd.read_csv('Gsensors.csv', index_col=0)

# drop last empty column
csv.drop(csv.columns[-1], axis=1, inplace = True)

# plot single sensor one by one with subplots
csv.plot(subplots=True,sharey='col')
# save plot
plt.savefig('ground_sensors_single.png')
plt.show()

# plot all sensors on single plot
csv.plot()
# set the legend on right corner
plt.legend(loc='upper right')
plt.savefig('ground_sensors.png')
plt.show() 
