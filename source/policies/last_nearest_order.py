import numpy as np
from source.policies.policy import Policy
from source.state import State
POLICY_NAME = 'LastNearestOrder'


def haversine_distance(lat_1, lng_1, lat_2, lng_2):
    size = len(lat_1) * len(lat_2)
    # ToDo: Implement function
    return np.ones(shape=(1, size)) * 100


class LastNearestOrder(Policy):
    def __init__(self):
        super(LastNearestOrder, self).__init__(name=POLICY_NAME)

    def take_action(self, state: State):
        orders = state.orders
        couriers = state.couriers
        return self.get_current_nearest_order(orders, couriers)

    @classmethod
    def get_current_nearest_order(cls, orders, couriers):
        if not orders:
            return {
                ix: {'lat': courier['lat'], 'lng': courier['lng']}
                for ix, courier in enumerate(couriers)
            }
        distance_array = haversine_distance(orders, orders, couriers, couriers)
        nearest_order = dict()
        for j, courier_id in enumerate(couriers):
            nearest_order[courier_id] = {'order_id': None, 'distance': 99999, 'lat': None, 'lng': None} # ToDO: write infinity
            for i, order_id in enumerate(orders):
                d = distance_array(i * (len(orders)) + j)
                if d < nearest_order[courier_id]['distance']:
                    # ToDo: Don't allow long distance moves, i.e. compute max distance in the order direction
                    nearest_order[courier_id] = {'order_id': order_id, 'distance': d, 'lat': orders[order_id]['lat'], 'lng': orders[order_id]['lng']}
        return nearest_order

