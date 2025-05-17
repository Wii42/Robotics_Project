"""
led_indicators.py

This module provides utility functions to control the LEDs of the e-puck robot
for various feedback scenarios, such as indicating goals, detected blocks, 
robot detection, and which side the robot is following.

Functions:
    set_leds_on_goal(robot): Illuminate LEDs to indicate the robot has reached a goal.
    set_led_on_block(robot, block): Set LED color based on detected block type.
    set_led_on_epuck(robot, has_detected): Indicate detection of another e-puck robot.
    set_led_on_side(robot, follows_left_side): Indicate which side of the track is being followed.

Authors:
    Lukas Künzi
    Thirith Yang
"""

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

def set_leds_on_goal(robot: WifiEpuck):
    """
    Illuminate LEDs to indicate the robot has reached a goal.

    Args:
        robot (WifiEpuck): The e-puck robot instance.
    """
    # Enable LEDs 0, 2, 4, 6 and the body LED for goal indication
    robot.enable_led(0)
    robot.enable_led(2)
    robot.enable_led(4)
    robot.enable_led(6)
    robot.enable_body_led()

def set_led_on_block(robot: WifiEpuck, block: str | None):
    """
    Set the color of LED 3 based on the detected block type.

    Args:
        robot (WifiEpuck): The e-puck robot instance.
        block (str | None): The type of block detected ("Red Block", "Green Block", or None).
    """
    # Disable LED 3 if no block is detected
    if block is None:
        robot.disable_led(3)
    # Set LED 3 to red for a red block
    elif block == "Red Block":
        robot.enable_led(3, 100, 0, 0)
    # Set LED 3 to green for a green block
    elif block == "Green Block":
        robot.enable_led(3, 0, 100, 0)

def set_led_on_epuck(robot: WifiEpuck, has_detected: bool):
    """
    Indicate detection of another e-puck robot using LED 0.

    Args:
        robot (WifiEpuck): The e-puck robot instance.
        has_detected (bool): True if another robot is detected, False otherwise.
    """
    # Enable LED 0 if another robot is detected, otherwise disable it
    if has_detected:
        robot.enable_led(0)
    else:
        robot.disable_led(0)

def set_led_on_side(robot: WifiEpuck, follows_left_side: bool):
    """
    Indicate which side of the track the robot is following using LEDs 2 and 6.

    Args:
        robot (WifiEpuck): The e-puck robot instance.
        follows_left_side (bool): True if following the left side, False if right.
    """
    # If following the left side, enable LED 6 and disable LED 2
    if follows_left_side:  # left side = led 6
        robot.enable_led(6)
        robot.disable_led(2)
    # If following the right side, enable LED 2 and disable LED 6
    else:  # right side = led 2
        robot.enable_led(2)
        robot.disable_led(6)
