class StepCounter:
    def __init__(self):
        self.steps = 0

    def step(self):
        self.steps += 1

    def get_steps(self):
        return self.steps

    def reset(self):
        self.steps = 0