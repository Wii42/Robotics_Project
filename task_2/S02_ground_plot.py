"""
S02_ground_plot.py

This script reads ground sensor data from a CSV file and generates plots for analysis.
It provides both individual sensor plots and a combined plot for all sensors, saving the results as PNG images.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

# run the code to plot the ground sensor results 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load ground sensor data from CSV file, using the first column as the index (step)
csv = pd.read_csv('Gsensors.csv', index_col=0)

# Drop the last column if it is empty (artifact from CSV writing)
csv.drop(csv.columns[-1], axis=1, inplace=True)

# Apply a rolling mean with window size 3 to smooth the sensor data
csv = csv.rolling(window=3).mean()

# Plot each sensor in a separate subplot, sharing the y-axis
csv.plot(subplots=True, sharey='col')
plt.savefig('ground_sensors_single.png')  # Save the subplot figure
plt.show()

# Plot all sensors on a single plot for comparison
csv.plot()
plt.legend(loc='upper right')  # Place the legend in the upper right corner
plt.savefig('ground_sensors.png')  # Save the combined plot
plt.show()
