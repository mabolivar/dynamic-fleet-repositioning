import os
import time
import json
import numpy as np
from source.scenario import Scenario
from source.state import State


class Policy:
    _excluded_keys = ['verbose']

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Policy')
        self.courier_km_per_minute = kwargs.get('courier_km_per_minute', 1.0)
        self.minutes_bucket_size = kwargs.get('minutes_bucket_size', 10)
        self.max_distance = self.courier_km_per_minute * self.minutes_bucket_size
        self.precision = kwargs.get('precision', 2)
        self.verbose = kwargs.get('verbose', False)
        self.export_details = kwargs.get('export_policy_details', False)
        self.logs_folder = 'logs/' + kwargs.get('instance_name', 'xxx') + '/' + self.name

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
        print(
            f"Policy: {self.name} - "
            f"Scenario: {scenario.index} - "
            f"Execution time: {execution_secs:.1f} - "
            f"Cost: {np.sum(scenario_costs):.1f} - "
            f"Perfect cost: {scenario.perfect_cost:.1f} - "
            f"Gap: {(np.sum(scenario_costs) - scenario.perfect_cost) / scenario.perfect_cost * 100:.1f}%"
        )
        if self.export_details:
            self.export_policy_as_dict(fname=f'{scenario.label}_{scenario.index}')

        return {
            'cost': round(sum(scenario_costs), 2),
            'actions': scenario_actions,
            'execution_secs': execution_secs,
            'gap': round((sum(scenario_costs) - scenario.perfect_cost)/scenario.perfect_cost, 2)
            }

    def take_action(self, state: State):
        raise NotImplementedError

    def dict_from_class(cls):
        return dict(
            (key, value)
            for (key, value) in cls.__dict__.items()
            if key not in cls._excluded_keys
        )

    def export_policy_as_dict(self, fname: str):
        os.makedirs(self.logs_folder, exist_ok=True)
        with open(f'{self.logs_folder}/{fname}.json', 'w') as f:
            json.dump(to_json(self.dict_from_class()), f, indent=2)


def key_to_json(data):
    if data is None or isinstance(data, (bool, int, float, str)):
        return data
    if isinstance(data, (tuple, frozenset)):
        return str(data)
    raise TypeError


def to_json(data):
    if data is None or isinstance(data, (bool, int, float, tuple, range, str, list)):
        return data
    if isinstance(data, (set, frozenset)):
        return sorted(data)
    if isinstance(data, dict):
        return {key_to_json(key): to_json(data[key]) for key in data}
    print(f'{type(data)}')
    raise TypeError
