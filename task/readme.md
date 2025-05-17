# Robotics Task


## Requirements

- Python 3.10+
- `unifr_api_epuck` package for robot communication

## Usage

1. **Activate the conda environment**
   ```bash
   conda activate robotics
   ```

2. **Start the server**  
   Before running the main script, start the server with the following command:
   ```bash
   python3 -m unifr_api_epuck -g
   ```
3. **Run the main script**  
   So set up the race, run the shell script `run.sh` from the task folder.
   
   It will start the race manager and initialize the robots.
   The robots will begin the race when receiving the "start" message from the web console.
    ```bash
    ./run.sh <robot1> <robot2>
   ```


## Notes

- Ensure all dependencies are installed and the robots as well as you machine are connected to the correct network.

## Authors

- @Lukas Künzi
- @Thirith Yang

**Date:** 18 May 2025