import os
import csv
from source.scenario import Scenario
from source.utils import load_data, split_data
from source.policies.last_nearest_order import LastNearestOrder
from source.policies.do_nothing import DoNothing
from source.policies.vfa import VFA

INSTANCE_NAME = 'robotex5'
OUTPUT_FOLDER = 'results'
PARAMS = {
    'instance_name': INSTANCE_NAME,
    'input_data_path': f"./data/{INSTANCE_NAME}.csv",
    'policies': ['do_nothing', 'vfa', 'last_nearest_order'],
    'minutes_bucket_size': 10,
    'courier_km_per_minute': 1.0,
    'precision': 2,
    'train': True,
    'export_policy_details': True,
}


def get_policy(name):
    if name == 'last_nearest_order':
        return LastNearestOrder
    elif name == 'do_nothing':
        return DoNothing
    elif name == 'vfa':
        return VFA
    else:
        raise ValueError('Unknown policy: {}'.format(name))


if __name__ == '__main__':
    data = load_data(PARAMS['input_data_path'])
    train, test = split_data(data)
    train_scenarios = Scenario.generate_scenarios(
        label="train", data=train, minutes_bucket_size=PARAMS['minutes_bucket_size']
    ) if PARAMS['train'] else []
    test_scenarios = Scenario.generate_scenarios(
        label="test", data=test, minutes_bucket_size=PARAMS['minutes_bucket_size']
    )

    policies_performance = [("policy", "scenario", "reward", "perfect_reward", "execution_secs")]
    for policy_name in PARAMS.get('policies', []):
        policy = get_policy(policy_name)(**PARAMS)
        sum_cost, sum_gap = 0, 0
        num_scenarios = len(train_scenarios)
        for scenario in train_scenarios:
            solution = policy.train(scenario)
            sum_cost += solution['cost']
            # sum_gap += solution['gap']
            policies_performance.append(
                (policy_name, scenario.label, solution['cost'], scenario.perfect_cost, solution['execution_secs'])
            )
        if PARAMS['train']:
            print(
                f"Train -> Policy: {policy_name} "
                f"| Avg. reward: {sum_cost / num_scenarios} "
                f"| gap: {(sum_gap / num_scenarios * 100):.1f}%"
            )

        sum_cost, sum_gap = 0, 0
        num_scenarios = len(test_scenarios)
        for scenario in test_scenarios:
            solution = policy.train(scenario)
            sum_cost += solution['cost']
            # sum_gap += solution['gap']
            policies_performance.append(
                (policy_name, scenario.label, solution['cost'], scenario.perfect_cost, solution['execution_secs'])
            )

        print(
            f"Test -> Policy: {policy_name} "
            f"| Avg. reward: {sum_cost / num_scenarios} "
            f"| gap: {(sum_gap / num_scenarios * 100):.1f}%"
        )

    # Export performance metrics
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    file_name = PARAMS['input_data_path'].split('/')[-1].split('.')[0]
    output_file = f"{OUTPUT_FOLDER}/performance_{file_name}.csv"
    with open(output_file, "w") as out:
        csv_out = csv.writer(out, lineterminator='\n')
        for row in policies_performance:
            csv_out.writerow(row)
    print(f"Performance metrics exported to {output_file}")
