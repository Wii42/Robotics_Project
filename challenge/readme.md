# Robotics Challenge

## Overview

This project provides a system for managing and visualizing the movement of multiple robots on a track. 
It includes a coordinator for robot distance management and a graphical user interface for real-time visualization.


## Requirements

- Python 3.10+
- `unifr_api_epuck` package for robot communication

## Usage

1. **Activate the conda environment**
   ```bash
   conda activate robotics
   ```
   Make sure the additional dependency `pygame` is installed.

2. **Start the server**  
   Before running the main script, start the server with the following command:
   ```bash
   python3 -m unifr_api_epuck -g
   ```
3. **Run the main script**  
   Launch run the main.py from the root directory of the project, e.g the parent directory of the `challenge` folder:
   ```bash
   python3 -m challenge.main
   ```
   This is needed to ensure that the imports and asset paths are correctly resolved.


## Notes

- Ensure all dependencies are installed and the robots as well as you machine are connected to the correct network.

## Authors

- @Lukas Künzi
- @Thirith Yang

**Date:** 18 May 2025