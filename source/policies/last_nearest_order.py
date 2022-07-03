from itertools import product
from source.state import State
from source.policies.policy import Policy
from source.utils import haversine_distance

POLICY_NAME = 'LastNearestOrder'


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

        order_cords = [[order['lat'], order['lng']] for order in orders]
        courier_cords = [[courier['lat'], courier['lng']] for courier in couriers]
        order_exploited_cords, courier_exploited_cords = list(zip(*product(order_cords, courier_cords)))
        distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*courier_exploited_cords))
        nearest_order = dict()
        for j, courier in enumerate(couriers):
            nearest_order[j] = {'order_id': None, 'distance': float('inf'), 'lat': None, 'lng': None}
            for i, order in enumerate(orders):
                d = distance_array[(i + j * len(orders))]
                if d < nearest_order[j]['distance']:
                    # ToDo: Don't allow long distance moves, i.e. compute max distance in the order direction
                    nearest_order[j] = {
                        'order_id': i,
                        'distance': d,
                        'lat': order['lat'],
                        'lng': order['lng']
                    }
        return nearest_order

