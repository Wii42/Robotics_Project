import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Select data to plot
columns = [
    'tof',
    'placeholder'  # here for ease of commenting in/out
]

# List of colors and runs
colors = ['white', 'red', 'blue']
runs = [1, 2, 3]

mean_dfs = {}  # store mean dataframes per color

for color in colors:
    data_per_run = []  # store dataframes per run for this color

    for i in runs:
        csv = pd.read_csv(f'ADDsensors_tof_{color}_{i}.csv', index_col=0)
        csv.drop(csv.columns[-1], axis=1, inplace=True)
        csv = csv[columns[:-1]]  # remove placeholder
        data_per_run.append(csv)

        ## Plot individual run
        #csv.plot(title=f'{color.capitalize()} Run {i}')
        #plt.legend(loc='upper right')
        #plt.savefig(f'additional_sensors_{color}_{i}.png')
        #plt.show()

    # Plot all 3 runs on the same diagram for this color
    plt.figure()
    for idx, df in enumerate(data_per_run):
        plt.plot(df.index, df['tof'], label=f'Run {idx+1}', linewidth=0.8)
    plt.title(f'ToF {color.capitalize()}')
    plt.xlabel('Steps')
    plt.ylabel('ToF Distance (mm)')
    plt.ylim(0, 1500)
    plt.legend()
    plt.savefig(f'{color}_all_runs.png')
    plt.show()

    # Compute mean across runs
    min_len = min(df.shape[0] for df in data_per_run)
    trimmed_dfs = [df.iloc[:min_len] for df in data_per_run]
    mean_df = pd.concat(trimmed_dfs).groupby(level=0).median()
    mean_dfs[color] = mean_df


# Plot means of all colors in one diagram
plt.figure()
for color, df in mean_dfs.items():
    plt.plot(df.index, df['tof'], label=f'{color.capitalize()}', color=color if color != 'white' else 'black', linewidth=0.8)
plt.title('Median of Runs - All Colors')
plt.xlabel('Steps')
plt.ylabel('ToF Distance (mm)')
plt.ylim(0, 1500)
plt.legend()
plt.savefig('all_colors_mean.png')
plt.show()