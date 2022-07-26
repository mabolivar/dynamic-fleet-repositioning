from copy import deepcopy
from source.scenario import Scenario


class State:
    def __init__(self, scenario: Scenario):
        self.scenario_ix = scenario.index
        self.epoch = 0
        self.locations = scenario.locations
        # Orders arose between t-1 and t
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        # Couriers arose between t-1 and t
        self.couriers = scenario.get_couriers(epoch=self.epoch)
        self.distance_map = scenario.distance_map
        self.neighbours_map = scenario.neighbours_map
        self.prev_actions = dict()

    def evaluate_cost_function(self, actions):
        if not self.orders:
            return 0, dict()
        nearest_order = dict()
        total_cost = 0
        for j, courier_id in enumerate(actions):
            action_lat, action_lng = actions[courier_id]['lat'], actions[courier_id]['lng']
            nearest_order[courier_id] = {'order_id': None, 'distance': float('inf'), 'lat': None,
                                         'lng': None}
            for i, order in enumerate(self.orders):
                order_lat, order_lng = order['lat'], order['lng']
                d = self.distance_map[(action_lat, action_lng)][(order_lat, order_lng)]
                if d < nearest_order[courier_id]['distance']:
                    nearest_order[courier_id] = {
                        'order_id': actions[courier_id].get('order_id', None),
                        'distance': d,
                        'courier_lat': self.couriers[courier_id]['lat'],
                        'courier_lng': self.couriers[courier_id]['lng'],
                        'action_lat': action_lat,
                        'action_lng': action_lng,
                        'order_lat': order_lat,
                        'order_lng': order_lng
                    }
            total_cost += nearest_order[courier_id]['distance']
        return total_cost, nearest_order

    def update(self, scenario, actions):
        self.epoch += 1
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        step_cost, nearest_order = self.evaluate_cost_function(actions)
        self.couriers = scenario.get_couriers(epoch=self.epoch) if self.epoch < scenario.epochs else None
        self.prev_actions = deepcopy(actions)
        return step_cost, nearest_order, self   # ToDo: return new state instead of updated_state
