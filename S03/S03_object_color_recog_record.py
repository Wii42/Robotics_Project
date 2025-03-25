# run the code to generate IR sensor data 
from unifr_api_epuck import wrapper
import numpy as np
import os
import time

dir = "./img_ex2_2"

# create directory
try: 
    os.mkdir(dir)
except OSError as error: 
    print(error) 

MY_IP = '192.168.2.205'
MAX_STEPS = 200

robot = wrapper.get_robot(MY_IP)

robot.initiate_model()
robot.init_camera(dir)

#open file for writing
data = open("object_recog_2.csv", "w")

if data == None:
    print('Error opening data file!\n')
    quit

#write header in CSV file
data.write('step,x_center,y_center,width,height,conf,label,time\n')

colordata = open("color_recog.csv", "w")

if colordata == None:
    print('Error opening data file!\n')
    quit

#write header in CSV file
colordata.write('step,x_center,y_center,width,height,area,label,time\n')


# wait 3 seconds before starting
robot.sleep(3)

robot.set_speed(-1.5,1.5)
step = 0

while robot.go_on() and step < MAX_STEPS:

    img = np.array(robot.get_camera())

    # object detection
    start_time = time.time()        
    detections = robot.get_detection(img,conf_thresh = 0)
    compute_time = time.time() - start_time
    
    outlier = False
    #Just save the detection
    for item in detections:
        data.write("{},{},{},{},{},{},{},{}\n".format(step,item.x_center,item.y_center,item.width,item.height,item.confidence,item.label,compute_time))
        if item.y_center < 50:
            outlier = True 

    if outlier:
        robot.save_detection()  

    # color detection
    start_time = time.time()        
    colordetections = robot.get_colordetection(img, saveimg = True, savemasks = True)
    compute_time = time.time() - start_time
    
    #Just save the color detection
    for item in colordetections:
        colordata.write("{},{},{},{},{},{},{},{}\n".format(step,item.x_center,item.y_center,item.width,item.height,item.area,item.label,compute_time))

    step += 1
        
data.close()
colordata.close()
robot.clean_up()
