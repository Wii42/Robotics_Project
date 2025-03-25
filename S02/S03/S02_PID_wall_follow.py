# wall following controller 

from unifr_api_epuck import wrapper
import os # for log files

import signal

MY_IP = '192.168.43.153'
robot = wrapper.get_robot(MY_IP)

def handler(signum, frame):
    robot.clean_up()

signal.signal(signal.SIGINT, handler)

# general parameters
PID_MAX_DS = 1.5
NORM_SPEED = 2
PID_WALL_TARGET = 200
a = 4
b = 2
c = 1
d = 0

# PID parameters
K = XXX
T_D = 0

T_I = 9999999999  #optional


class PID:

    TIME_STEP = 64

    def __init__(self, k, t_i, t_d):
        self.error = 0
        self.deriv = 0
        self.integ = 0
        self.K = k
        self.T_I = t_i
        self.T_D = t_d

    def compute(self,prox,target):    
        prev_err = self.error
        self.error = prox - target

        self.deriv = (self.error - prev_err)*1000/self.TIME_STEP
        self.integ += self.error*self.TIME_STEP/1000

        #return self.K * ( self.error + 1.0 / self.T_I * self.integ + self.T_D * self.deriv)
        return self.P() + self.I() + self.D()

    def P(self) :
        return self.K * self.error    

    def I(self) :
        return self.K * (self.integ/self.T_I)    

    def D(self) :
        return self.K * (self.T_D * self.deriv)    
    

# open file for writing (adding a number if already exists)
n = 0
while os.path.exists("logPID_{}.csv".format(n)):
    n += 1
data = open("logPID_{}.csv".format(n), "w")

if data == None:
    print('Error opening data file!\n')
    quit

#write header in CSV file
data.write('step,K,T_I,T_D,P,I,D,ds,left speed,right speed\n')

# create pid instance
pid = PID( K, T_I, T_D)

step = 0

robot.init_sensors()
robot.calibrate_prox()

robot.sleep(2)

#infinite loop
while robot.go_on():
    ps = robot.get_calibrate_prox()
    proxR = (a * ps[0] + b * ps[1] + c * ps[2] + d * ps[3]) / (a+b+c+d);
                      
    # compute PID response according to IR sensor value
    ds = pid.compute(proxR,PID_WALL_TARGET);      
          
    # make the robot turn towards the wall by default    
    ds += .05

    speedR = NORM_SPEED + ds
    speedL = NORM_SPEED - ds
    
    # "clamping" function for corners
    if abs(ds) > PID_MAX_DS :
            speedR = +ds
            speedL = -ds
    
    robot.set_speed(speedL,speedR)

    # write a line of data in log file
    data.write("{},{},{},{},{},{},{},{},{},{}\n".format(step, K, T_I, T_D, pid.P(), pid.I(), pid.D(), ds, speedL,speedR))
        
    step += 1
    
robot.clean_up()

