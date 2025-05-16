# Robotics Project 2

## Overview

This project provides a system for managing and visualizing the movement of multiple robots on a track. It includes a coordinator for robot distance management and a graphical user interface (GUI) for real-time visualization. Communication between the coordinator and the GUI is handled via a thread-safe queue.

## Features

- Real-time robot state management and visualization
- Multi-robot coordination with adjustable optimal distance
- Modular design for easy extension and maintenance

## Requirements

- Python 3.10+
- `unifr_api_epuck` package for robot communication

## Usage

1. **Start the server**  
   Before running the main script, start the server with the following command:
   ```bash
   python3 -m unifr_api_epuck -g
   ```
2. **Run the main script**  
Launch the main entry point:

## Notes

- The beacon detector is currently not robust and works reliably only when the robot speed is relatively constant.
- Ensure all dependencies are installed and the robots are connected to the correct network.

## Authors

- @Lukas Künzi
- @Thirith Yang

**Date:** 18 May 2025