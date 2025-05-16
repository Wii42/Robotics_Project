# run the code to generate IR sensor data 
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.210'
MAX_STEPS = 750

robot = wrapper.get_robot(MY_IP)

robot.init_ground()

#open file for writing
data = open("Gsensors.csv", "w")

if data == None:
    print('Error opening data file!\n')
    quit

#write header in CSV file
data.write('step,')
for i in range(robot.GROUND_SENSORS_COUNT):
    data.write('gs'+str(i)+',')
data.write('\n')

# wait 3 seconds before starting
robot.sleep(3)

for step in range(MAX_STEPS):
    robot.go_on()
    gs = robot.get_ground()
    
    #write a line of data 
    data.write(str(step)+',')
    for v in gs:
        data.write(str(v)+',')
    data.write('\n')

    robot.set_speed(2, 2)
    
data.close()

robot.clean_up()
