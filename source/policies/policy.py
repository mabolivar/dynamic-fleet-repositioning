import time
from source.scenario import Scenario
from source.state import State


class Policy:
    def __init__(self, name):
        self.name = name

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
