import numpy as np
from source.scenario import Scenario


def haversine_distance(lat_1, lng_1, lat_2, lng_2):
    size = len(lat_1) * len(lat_2)
    # ToDo: Implement function
    return np.ones(shape=(1, size)) * 100


class State:
    def __init__(self, scenario: Scenario):
        self.scenario_ix = scenario.index
        self.epoch = 0
        # Orders arose between t-1 and t
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        # Couriers arose between t-1 and t
        self.couriers = scenario.get_couriers(epoch=self.epoch)

    # ToDo: make it singleton
    def evaluate_cost_function(self, actions):
        if not self.orders:
            return 0, dict()
        distance_array = haversine_distance(self.orders, self.orders, actions, actions)
        nearest_order = dict()
        total_cost = 0
        for j, courier_id in enumerate(actions):
            nearest_order[courier_id] = {'order_id': None, 'distance': 99999, 'lat': None,
                                         'lng': None}  # ToDO: write infinity
            for i, order_id in enumerate(self.orders):
                d = distance_array[i * (len(self.orders)) + j]
                if d < nearest_order[courier_id]['distance']:
                    nearest_order[courier_id] = {
                        'order_id': order_id,
                        'distance': d,
                        'courier_lat': self.couriers[courier_id]['lat'],
                        'courier_lng': self.couriers[courier_id]['lng'],
                        'action_lat': actions[courier_id]['lat'],
                        'action_lng': actions[courier_id]['lng'],
                        'order_lat': self.orders[order_id]['lat'],
                        'order_lng': self.orders[order_id]['lng']
                    }
            total_cost += nearest_order[courier_id]['distance']
        return total_cost, nearest_order

        # ToDo: get lat,lng coords and indexes
        distance_array = self.haversine_distance(self.orders, self.orders, actions, actions)
        return {
            (order_id, courier_id): distance_array(i * (len(actions)) + j)
            for i, order_id in enumerate(self.orders)
            for j, courier_id in enumerate(actions)
            }

    def update(self, scenario, actions):
        self.epoch += 1
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        step_cost, nearest_order = self.evaluate_cost_function(actions)
        self.couriers = scenario.get_couriers(epoch=self.epoch)
        return step_cost, nearest_order, self   # ToDo: return new state instead of updated_state
