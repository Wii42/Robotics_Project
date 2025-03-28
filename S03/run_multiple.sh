#!/bin/bash

# for .py with same name as folder
#prog=`basename "$PWD"`.py

prog="S03_detecting_explorer.py"

# for first .py in folder
#prog=$(ls ./*.py| head -1)

echo $prog

for ip in "$@"
do
echo $prog' 192.168.2.'$ip
gnome-terminal -- bash -c "conda activate robotics; python3 ./'$prog' 192.168.2.'$ip'; read"
sleep 1   
done
