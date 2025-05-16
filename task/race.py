# entry point for the race
import sys

from main import MarioKart

MY_IP = '192.168.2.210'

if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 2:
        ip = sys.argv[1]
        print("ip: ", ip)
    else:
        ip = MY_IP
    MarioKart(ip, norm_speed=3, communicate=True).run()