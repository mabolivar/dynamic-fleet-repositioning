import time
import numpy as np
from source.scenario import Scenario
from source.state import State


class Policy:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Policy')
        self.courier_km_per_minute = kwargs.get('courier_km_per_minute', 1.0)
        self.minutes_bucket_size = kwargs.get('minutes_bucket_size', 10)
        self.max_distance = self.courier_km_per_minute * self.minutes_bucket_size
        self.precision = kwargs.get('precision', 2)
        self.verbose = kwargs.get('verbose', False)

    def train(self, scenario: Scenario):
        now = time.time()
        state = State(scenario)
        scenario_actions = []
        scenario_costs = []
        for epoch in range(scenario.epochs):
            actions = self.take_action(state)
            cost, action_evaluation, state = state.update(scenario, actions)
            scenario_actions.append(action_evaluation)
            scenario_costs.append(cost)
            if self.verbose:
                print(f"Scenario: {scenario.index} - Epoch: {epoch} - Cost: {cost}")
        execution_secs = time.time() - now
        print(f"Policy: {self.name} - Scenario: {scenario.index} - Execution time: {execution_secs} - Cost: {np.sum(scenario_costs)}")
        return {
            'cost': sum(scenario_costs),
            'actions': scenario_actions,
            'execution_secs': execution_secs
            }

    def take_action(self, state: State):
        raise NotImplementedError
