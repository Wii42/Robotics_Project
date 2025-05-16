ground_sensor_calibration: dict[str, list[float]] = {
    "192.168.2.208": [1, 1.1, 0.9],
    "192.168.2.210": [1.02, 1, 1.02]
}


def normalize_gs(gs: list[float | int], robot_ip: str) -> list[float]:
    """
    Normalize the ground sensor values based on the calibration values.
    :param gs: List of ground sensor values.
    :param robot_ip: IP address of the robot.
    :return: Normalized ground sensor values.
    """
    if robot_ip in ground_sensor_calibration:
        calibration = ground_sensor_calibration[robot_ip]
        for i in range(len(gs)):
            factor = get_safe(calibration, i, 1)
            gs[i] = gs[i] * factor
    return gs


def get_safe(lst, index, default=None):
    try:
        return lst[index]
    except IndexError:
        return default
