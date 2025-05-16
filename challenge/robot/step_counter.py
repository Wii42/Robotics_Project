class StepCounter:
    """
    A simple step counter class that keeps track of the number of steps taken.
    Created to distribute the step number to all classes that need it.
    """
    def __init__(self):
        self.steps = 0

    def step(self):
        """
        Increment the step counter by 1.
        :return: None
        """
        self.steps += 1

    def get_steps(self) -> int:
        """
        Get the current number of steps.
        :return: int - the number of steps taken.
        """
        return self.steps

    def reset(self):
        """
        Reset the step counter to 0.
        :return: None
        """
        self.steps = 0