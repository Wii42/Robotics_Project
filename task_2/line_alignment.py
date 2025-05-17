"""
line_alignment.py

This module provides the LineAlignment class, which ensures that the robot follows
the outer edge of a line on the ground. The main objective is to keep one of the robot's
sensors in contact with the white ground (not the grey area), making it easier to detect
and follow the line. The class periodically checks if the robot is following the correct
side of the line and adjusts its behavior if necessary.

Classes:
    LineAlignment: Maintains and updates which side of the line the robot should follow.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

from determine_side import TrackSide


class LineAlignment:
    """
    The LineAlignment class ensures that the robot follows the outer edge of the line.
    The goal is to keep one sensor in contact with the white ground (not the grey area)
    for easier detection of the line. This class periodically checks if the robot is
    following the correct side of the line and adjusts the side if necessary.

    Attributes:
        follow_left_side (bool): True if following the left side, False if following the right.
    """

    def __init__(self, follow_left_side: bool = False):
        """
        Initialize the LineAlignment class.

        Args:
            follow_left_side (bool): Indicates whether the robot should follow
                the left side of the line. If False, the robot will follow the right side.
        """
        self.follow_left_side = follow_left_side  # True if following the left side, False otherwise.

    def get_follow_left_side(self) -> bool:
        """
        Get the current side the robot is following.

        Returns:
            bool: True if the robot is following the left side, False if following the right side.
        """
        return self.follow_left_side

    def check_line_alignment(self, current_side: TrackSide):
        """
        Check if the robot is following the correct side of the line. If the robot is
        on the wrong side, switch the side to follow.

        Args:
            current_side (TrackSide): The current side of the line the robot is on (LEFT, RIGHT, or UNKNOWN).

        Returns:
            None
        """
        # If the robot is on the left side but should follow the right side, switch to the left side.
        if current_side == TrackSide.LEFT and not self.follow_left_side:
            self.follow_left_side = True
        # If the robot is on the right side but should follow the left side, switch to the right side.
        elif current_side == TrackSide.RIGHT and self.follow_left_side:
            self.follow_left_side = False
