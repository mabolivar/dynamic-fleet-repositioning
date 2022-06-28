from source.state import State


class Policy:
    def __init__(self, name):
        self.name = name

    def take_action(self, state: State):
        raise NotImplementedError
