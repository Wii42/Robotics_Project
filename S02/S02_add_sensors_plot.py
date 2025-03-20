# run the script to plot the additional sensor responses 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# select data to plot
columns = [
    'tof',
    #'accX',
    #'accY',
    #'accZ',
#    'acc',
#    'incl',
#    'orient',
#    'roll',
#    'pitch',
    #'gyroX',
    #'gyroY',
    #'gyroZ',
#    'mic0',
#    'mic1',
#    'mic2',
#    'mic3',
    'placeholder' # here for ease of commenting in/out
     ]

# get data from CSV file
colors = ['white', 'red', 'blue']
for color in colors:
    for i in range(1,4):


        csv = pd.read_csv(f'ADDsensors_tof_{color}_{i}.csv', index_col=0)

        # drop last empty column
        csv.drop(csv.columns[-1], axis=1, inplace = True)

        # select columns to plot (removing placeholder)
        new_csv = csv[columns[:-1]]
        csv = new_csv

        ## plot single sensor one by one with subplots
        #csv.plot(subplots=True)
        ## save plot
        #plt.savefig(f'additional_sensors_single.png')
        #plt.show()

        # plot all sensors on single plot
        csv.plot()
        # set the legend on right corner
        plt.legend(loc='upper right')
        plt.savefig(f'additional_sensors_{color}_{i}.png')
        plt.show()
