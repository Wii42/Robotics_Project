#!/bin/bash

# Check if exactly two parameters are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <param1> <param2>"
    exit 1
fi

# Assign parameters to variables
PARAM1="192.168.2.$1"
PARAM2="192.168.2.$2"

# Example logic: print the parameters
echo "First parameter: $PARAM1"
echo "Second parameter: $PARAM2"

# Start server
#gnome-terminal -- bash -c "python3 -m unifr_api_epuck -g"



#start controllers
gnome-terminal -- bash -c "python3 ./race.py $PARAM1"
gnome-terminal -- bash -c "python3 ./race.py $PARAM2"

#start race_manager
python3 ./race_manager.py



# You can add more logic below as needed