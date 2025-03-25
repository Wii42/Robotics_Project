# run the cell to record images_216_blue1
from unifr_api_epuck import wrapper
import os

dir = "./images_205_blue_3"
# create directory
try: 
    os.mkdir(dir)
except OSError as error: 
    print(error)  

MY_IP = '192.168.2.205'
robot = wrapper.get_robot(MY_IP)

N_SAMPLES = 10

robot.init_camera(dir) # define your working directory for storing images_216_blue1 (do not forget to create it)

#wait 3 seconds
robot.sleep(3)

step = 0
while robot.go_on() and step < N_SAMPLES :

    robot.take_picture('image'+str(step).zfill(3))
    step += 1

robot.clean_up()
