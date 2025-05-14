from unifr_api_epuck import wrapper
import numpy as np

def object_with_largest_area(detections):
    if len(detections) == 0:
        return None
    max_area = 0
    max_obj = None
    for obj in detections:
        area = obj.width * obj.height
        if area > max_area:
            max_area = area
            max_obj = obj
    return max_obj


def block_detector(robot, upperB, lowerB):
    
    img = np.array(robot.get_camera())
    detections = robot.get_detection(img)
    robot.save_detection()
    
    red_blocks = []
    green_blocks = []
    
    if detections is not None and len(detections) > 0:
        red_blocks = [obj for obj in detections if obj.label == "Red Block"]
        green_blocks = [obj for obj in detections if obj.label == "Green Block"]

        print("Red blocks: ", red_blocks)
        print("Green blocks: ", green_blocks)

    obj = object_with_largest_area(red_blocks)
    if obj is not None and lowerB<obj.height<upperB:
        
        print(obj.height)
        print(obj.label)
        return obj.label

    obj = object_with_largest_area(green_blocks)
    if obj is not None and lowerB<obj.height<upperB:
        print(obj.height)
        print(obj.label)
        print(obj.height)
        return obj.label
    return None
