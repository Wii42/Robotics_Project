from unifr_api_epuck import wrapper

MY_IP = '192.168.2.206' # modify the last number with the last 3 digits of the robot ID (on sticker)
robot = wrapper.get_robot(MY_IP)

counter = 0

while robot.go_on() and counter < 400:
    counter += 1
    
    if counter % 80 < 40:
        robot.set_speed(2, 2)
    else:
        robot.set_speed(-2, -2)

robot.clean_up()
