from unifr_api_epuck import wrapper
import time
from datetime import datetime

race_manager = wrapper.get_client(client_id='Race Manager', host_ip='http://127.0.0.1:8000')

time_start = None
time_goal1 = None
time_goal2 = None

IDLE = 0
RACE = 1
FIRST = 2
SECOND = 3

state = IDLE

while(True):
    if(race_manager.has_receive_msg()):
        msg = race_manager.receive_msg()
        print(msg)
        if msg == "start":
            time_start = datetime.now()
            state = RACE
        elif msg == "goal":
            if state == RACE:
                time_goal1 = datetime.now()
                print ("first "+str(time_goal1-time_start))
                state = FIRST
            elif state == FIRST :
                time_goal2 = time.time()
                time_goal2 = datetime.now()
                print ("second "+str(time_goal2-time_start))
                state = SECOND
    if state == SECOND :
        break

timeformat = "%H:%M:%S %f"

print(f"\nStart time: {time_start}\n\nArrival times:\n\n\t1. {time_goal1.strftime(timeformat)}\n\t2. {time_goal2.strftime(timeformat)}\n\nDifference: {time_goal2-time_goal1}")
            

