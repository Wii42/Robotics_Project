from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck


def set_leds_on_goal(robot: WifiEpuck):
    robot.enable_led(0)
    robot.enable_led(2)
    robot.enable_led(4)
    robot.enable_led(6)
    robot.enable_body_led()


def set_led_on_block(robot: WifiEpuck, block: str | None):
    if block is None:
        robot.disable_led(3)
    elif block == "Red Block":
        robot.enable_led(3, 100, 0, 0)
    elif block == "Green Block":
        robot.enable_led(3, 0, 100, 0)


def set_led_on_epuck(robot: WifiEpuck, has_detected: bool):
    if has_detected:
        robot.enable_led(0)
    else:
        robot.disable_led(0)


def set_led_on_side(robot: WifiEpuck, follows_left_side: bool):
    if follows_left_side:  # left side = led 6
        robot.enable_led(6)
        robot.disable_led(2)

    else:  # right side = led 2
        robot.enable_led(2)
        robot.disable_led(6)
