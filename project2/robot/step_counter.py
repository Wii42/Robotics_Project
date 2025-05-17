"""
step_counter.py

A simple step counter class for tracking the number of steps taken by the robot.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

class StepCounter:
    """
    A simple step counter class that keeps track of the number of steps taken.
    Created to distribute the step number to all classes that need it.
    """
    def __init__(self):
        """
        Initialize the step counter to zero.
        """
        self.steps = 0

    def step(self):
        """
        Increment the step counter by 1.

        Returns:
            None
        """
        self.steps += 1

    def get_steps(self) -> int:
        """
        Get the current number of steps.

        Returns:
            int: The number of steps taken.
        """
        return self.steps

    def reset(self):
        """
        Reset the step counter to zero.

        Returns:
            None
        """
        self.steps = 0