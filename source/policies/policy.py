import time
import numpy as np
from source.scenario import Scenario
from source.state import State


def compute_precision(max_distance):
    return 2 # ToDo: Compute precision based on max_distance (and therefore speed)


class Policy:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Policy')
        self.courier_km_per_minute = kwargs.get('courier_km_per_minute', 1.0)
        self.minutes_bucket_size = kwargs.get('minutes_bucket_size', 10)
        self.max_distance = self.courier_km_per_minute * self.minutes_bucket_size
        self.precision = compute_precision(self.max_distance)

    def train(self, scenario: Scenario):
        now = time.time()
        state = State(scenario)
        scenario_actions = []
        scenario_costs = []
        for epoch in range(scenario.epochs):
            print(f"Scenario: {scenario.index} - Epoch: {epoch}")
            actions = self.take_action(state)
            cost, action_evaluation, state = state.update(scenario, actions)
            scenario_actions.append(action_evaluation)
            scenario_costs.append(cost)
        execution_secs = time.time() - now
        return {
            'cost': sum(scenario_costs),
            'actions': scenario_actions,
            'execution_secs': execution_secs
            }

    def take_action(self, state: State):
        raise NotImplementedError

    def get_neighbours(self, lat, lng, precision=2):
        moves = [0, -1, 1]
        scale = 10 ** precision
        return [(round(lat + i / scale, precision), round(lng + j / scale, precision))
                for i in moves for j in moves]
