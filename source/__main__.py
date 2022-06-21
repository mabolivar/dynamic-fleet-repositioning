from source.utils import load_data, split_data

PARAMS = {'input_data_path': "./data/robotex5.csv", }

if __name__ == '__main__':
    data = load_data(PARAMS['input_data_path'])
    train, test = split_data(data)
    train_scenarios = generate_scenarios(train)
    test_scenarios = generate_scenarios(test)

    policies_performance = [("policy", "scenario", "reward", "perfect_reward", "execution_secs")]
    for policy_name in PARAMS.get('policies', []):
        policy = get_policy(policy_name)
        train_performance, train_gap, train_performance_metrics = policy.train(train_scenarios)
        policies_performance = policies_performance + train_performance
        print(f"Policy: {policy_name} | Avg. reward: {avg_reward} | gap: {(avg_gap * 100):.1f}%")

