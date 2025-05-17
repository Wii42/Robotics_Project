"""
calibration.py

Ground sensor calibration utilities for the ePuck robot.

This module provides functions to normalize ground sensor readings based on
predefined calibration factors for each robot (identified by IP address).
Calibration ensures that sensor readings are consistent across different robots,
compensating for hardware variations.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

# Dictionary mapping robot IP addresses to their ground sensor calibration factors.
ground_sensor_calibration: dict[str, list[float]] = {
    "192.168.2.208": [1, 1.1, 0.9],
    "192.168.2.210": [1.02, 1, 1.02]
}


def normalize_gs(gs: list[float | int], robot_ip: str) -> list[float]:
    """
    Normalize the ground sensor values based on the calibration values for a specific robot.

    Args:
        gs (list[float | int]): List of ground sensor values.
        robot_ip (str): IP address of the robot.

    Returns:
        list[float]: Normalized ground sensor values.
    """
    # Apply calibration factors if the robot IP is known
    if robot_ip in ground_sensor_calibration:
        calibration = ground_sensor_calibration[robot_ip]
        for i in range(len(gs)):
            factor = get_safe(calibration, i, 1)
            gs[i] = gs[i] * factor
    return gs


def get_safe(lst, index, default=None):
    """
    Safely get an element from a list by index, returning a default value if out of bounds.

    Args:
        lst (list): The list to access.
        index (int): The index to retrieve.
        default (Any, optional): The value to return if index is out of bounds. Defaults to None.

    Returns:
        Any: The element at the specified index or the default value.
    """
    try:
        return lst[index]
    except IndexError:
        return default
