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
        self.get_nearest_order(orders, couriers)

    @classmethod
    def get_nearest_order(cls, orders, couriers):
        distance_array = haversine_distance(orders, orders, couriers, couriers)
        nearest_order = dict()
        for j, courier_ix in enumerate(couriers):
            nearest_order[courier_ix] = {None, 99999, None, None, None} # ToDO: write infinity (order_ix, value, lat,lng)
            for i, order_ix in enumerate(orders):
                d = distance_array(i * (len(orders)) + j)
                if d < nearest_order[courier_ix][1]:
                    nearest_order[courier_ix] = (order_ix, d, orders[order_ix]['lat'], orders[order_ix]['lng'])
        return {
            (order_ix, courier_ix):
            for i, order_ix in enumerate(orders)
            for j, courier_ix in enumerate(couriers)
            }

