import csv
import matplotlib.pyplot as plt

# Read data from CSV
pair_distances = {}
pair_indices = {}

with open('distances.csv', mode='r') as file:
    reader = csv.DictReader(file)
    index = 0
    for row in reader:
        pair = f"{row['rear']} → {row['front']}"
        dist_str = row['distance']
        if dist_str == '':
            continue
        distance = float(row['distance'])
        if pair not in pair_distances:
            pair_distances[pair] = []
            pair_indices[pair] = []
        pair_distances[pair].append(distance)
        pair_indices[pair].append(index)
        index += 1

plt.figure(figsize=(10, 6))
for pair in pair_distances:
    if pair == "205 → 210":
        plt.plot(pair_indices[pair], pair_distances[pair], label=pair)

plt.xlabel('Sample Index')
plt.ylabel('Distance (meters)')
plt.title('Distances Between Robot Pairs Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()