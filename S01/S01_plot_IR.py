# run this code to plot the result 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# get data from CSV file
csv: pd.DataFrame = pd.read_csv('IRsensors.csv', index_col=0)

# drop last empty column
csv.drop(csv.columns[8], axis=1, inplace = True)
front_sensors = csv[['ps0', 'ps7']].copy()
front_sensors.rename(columns={"ps0": "Front right", "ps7": "Front left"}, inplace=True)
front_sensors['Average'] = front_sensors.mean(axis=1)

front_sensors.plot(color=['orange', 'cyan', 'grey', 'red'])
# set the legend on right corner
plt.legend(loc='upper right')
plt.savefig('calibrated_IR_sensors.png')
plt.show()
