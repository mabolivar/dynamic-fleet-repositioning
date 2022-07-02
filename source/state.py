import numpy as np
from itertools import product
from source.scenario import Scenario



def haversine_distance_deprecated(lat_1, lng_1, lat_2, lng_2):
    size = len(lat_1) * len(lat_2)
    # ToDo: Implement function
    return np.ones(shape=(1, size)) * 100


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km


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
        order_cords = [[order['lat'], order['lng']] for order in self.orders]
        courier_cords = [[courier['lat'], courier['lng']] for courier in self.couriers]
        order_exploited_cords, courier_exploited_cords = list(zip(*product(order_cords, courier_cords)))
        distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*courier_exploited_cords))
        nearest_order = dict()
        total_cost = 0
        for j, courier_id in enumerate(actions):
            nearest_order[courier_id] = {'order_id': None, 'distance': 99999, 'lat': None,
                                         'lng': None}  # ToDO: write infinity
            for i, order in enumerate(self.orders):
                d = distance_array[(i + j * len(self.orders))]
                if d < nearest_order[courier_id]['distance']:
                    nearest_order[courier_id] = {
                        'order_id': actions[courier_id].get('order_id', None),
                        'distance': d,
                        'courier_lat': self.couriers[courier_id]['lat'],
                        'courier_lng': self.couriers[courier_id]['lng'],
                        'action_lat': actions[courier_id]['lat'],
                        'action_lng': actions[courier_id]['lng'],
                        'order_lat': order['lat'],
                        'order_lng': order['lng']
                    }
            total_cost += nearest_order[courier_id]['distance']
        return total_cost, nearest_order

    def update(self, scenario, actions):
        self.epoch += 1
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        step_cost, nearest_order = self.evaluate_cost_function(actions)
        self.couriers = scenario.get_couriers(epoch=self.epoch) if self.epoch < scenario.epochs else None
        return step_cost, nearest_order, self   # ToDo: return new state instead of updated_state
