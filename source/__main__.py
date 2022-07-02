from source.scenario import Scenario
from source.utils import load_data, split_data
from source.policies.last_nearest_order import LastNearestOrder

PARAMS = {'input_data_path': "./data/robotex5.csv",
          'policies': ['last_nearest_order']}


def get_policy(name):
    if name == 'last_nearest_order':
        return LastNearestOrder()
    else:
        raise ValueError('Unknown policy: {}'.format(name))


if __name__ == '__main__':
    data = load_data(PARAMS['input_data_path'])
    train, test = split_data(data)
    train_scenarios = Scenario.generate_scenarios(label="train", data=train)
    test_scenarios = Scenario.generate_scenarios(label="test", data=test)

    policies_performance = [("policy", "scenario", "reward", "perfect_reward", "execution_secs")]
    for policy_name in PARAMS.get('policies', []):
        policy = get_policy(policy_name)
        sum_cost, sum_gap = 0, 0
        num_scenarios = len(test_scenarios)
        for scenario in train_scenarios:
            solution = policy.train(scenario)
            sum_cost += solution['cost']
            # sum_gap += solution['gap']
            policies_performance.append(
                (policy_name, scenario.label, solution['cost'], scenario.perfect_cost, solution['execution_secs'])
            )

        print(f"Policy: {policy_name} | Avg. reward: {sum_cost/num_scenarios} | gap: {(sum_gap/num_scenarios * 100):.1f}%")

