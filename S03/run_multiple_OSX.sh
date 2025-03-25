#!/bin/bash

# for .py with same name as folder
prog=`basename "$PWD"`.py

# for first .py in folder
#prog=$(ls ./*.py| head -1)

echo $prog

for ip in "$@"
do
echo $prog' 192.168.2.'$ip
osascript -e 'tell app "Terminal"
    do script "cd '$PWD'; conda activate robotics; python3 ./'$prog' 192.168.2.'$ip'; read"
end tell'
sleep 1   
done
