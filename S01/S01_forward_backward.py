from unifr_api_epuck import wrapper

MY_IP = '192.168.2.208' # modify the last number with the last 3 digits of the robot ID (on sticker)
robot = wrapper.get_robot(MY_IP)

counter = 0

while robot.go_on() and counter < 1000:
    counter += 1
    
    if counter % 806 < 403:
        robot.set_speed(3, 6)
    else:
        robot.set_speed(6, 3)

robot.clean_up()
