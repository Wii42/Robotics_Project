# run this code to generate IR sensor data 
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.xxx' # change robot number
MAX_STEPS = 200

robot = wrapper.get_robot(MY_IP)

robot.init_sensors()
robot.calibrate_prox()

#open file for writing
data = open("IRsensors.csv", "w")

if data == None:
    print('Error opening data file!\n')
    quit

#write header in CSV file
data.write('step,')
for i in range(robot.PROX_SENSORS_COUNT):
    data.write('ps'+str(i)+',')
data.write('\n')

# wait 3 seconds before starting
robot.sleep(3)

for step in range(MAX_STEPS):
    robot.go_on()
    ps = robot.get_calibrate_prox()
    #ps = robot.get_prox() # uncomment if analyzing uncalibrated sensor data

    #write a line of data 
    data.write(str(step)+',')
    for v in ps:
        data.write(str(v)+',')
    data.write('\n')
    
data.close()

robot.clean_up()

