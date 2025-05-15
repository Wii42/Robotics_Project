from unifr_api_epuck import wrapper
import numpy as np
from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck, Detected


def object_with_largest_area(detections):
    """
    Find the object with the largest area from a list of detections.

    :param detections: A list of detected objects, where each object has `width` and `height` attributes.
    :return: The object with the largest area, or None if no detections are provided.
    """
    if len(detections) == 0:
        return None  # Return None if there are no detections

    max_area = 0  # Variable to store the maximum area found
    max_obj = None  # Variable to store the object with the largest area

    # Iterate through all detected objects
    for obj in detections:
        area = obj.width * obj.height  # Calculate the area of the object
        if area > max_area:
            max_area = area  # Update the maximum area
            max_obj = obj  # Update the object with the largest area

    return max_obj  # Return the object with the largest area


def block_detector(robot: WifiEpuck, upperB, lowerB):
    """
    Detect blocks (red or green) within a specific height range using the robot's camera.

    :param robot: The robot instance with a camera and detection capabilities.
    :param upperB: The upper bound for the block's height.
    :param lowerB: The lower bound for the block's height.
    :return: The label of the detected block ("Red Block" or "Green Block"), or None if no block is detected.
    """
    # Capture an image from the robot's camera
    img = np.array(robot.get_camera())

    # Perform object detection on the captured image
    detections: list[Detected] = robot.get_detection(img)
    robot.save_detection()

    # Lists to store detected red and green blocks
    red_blocks = []
    green_blocks = []
    
    # Filter detections into red and green blocks
    if detections is not None and len(detections) > 0:
        #detections = [obj for obj in detections if 30 < obj.y_center < 130]

        red_blocks = [obj for obj in detections if obj.label == "Red Block"]
        green_blocks = [obj for obj in detections if obj.label == "Green Block"]

        print("Red blocks: ", red_blocks)
        print("Green blocks: ", green_blocks)

    obj = object_with_largest_area(red_blocks)
    if obj is not None and lowerB < obj.height < upperB:
        print(obj.height)  # Print the height of the detected block
        print(obj.label)  # Print the label of the detected block
        return obj.label  # Return the label of the detected block

    # Check for the largest green block within the specified height range
    obj = object_with_largest_area(green_blocks)
    if obj is not None and lowerB < obj.height < upperB:
        print(obj.height)  # Print the height of the detected block
        print(obj.label)  # Print the label of the detected block
        return obj.label  # Return the label of the detected block

    return None  # Return None if no block is detected within the specified range
