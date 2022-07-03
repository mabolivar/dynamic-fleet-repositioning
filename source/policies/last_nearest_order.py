from itertools import product

import numpy as np

from source.state import State
from source.policies.policy import Policy
from source.utils import haversine_distance

POLICY_NAME = 'LastNearestOrder'


class LastNearestOrder(Policy):
    def __init__(self, **kwargs):
        super(LastNearestOrder, self).__init__(
            name=POLICY_NAME,
            courier_km_per_minute=kwargs.get('courier_km_per_minute', 1.0),
            minutes_bucket_size=kwargs.get('minutes_bucket_size', 10)
        )

    def take_action(self, state: State):
        orders = state.orders
        couriers = state.couriers
        return self.get_current_nearest_order(orders, couriers)

    def get_current_nearest_order(self, orders, couriers):
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
                    move_lat, move_lng = self.compute_movement_location(courier['lat'], courier['lng'], order['lat'], order['lng'], d)
                    nearest_order[j] = {
                        'order_id': i,
                        'distance': d,
                        'lat': move_lat,
                        'lng': move_lng,
                    }
        return nearest_order

    def compute_movement_location(self, start_lat, start_lng, end_lat, end_lng, distance):
        movements = self.get_neighbours(start_lat, start_lng, precision=self.precision)
        order_exploited_cords, movement_exploited_cords = list(zip(*product([(end_lat, end_lng)], movements)))
        distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*movement_exploited_cords))
        d = float('inf')
        best_move = None
        for i, move in enumerate(movements):
            if distance_array[i] < d:
                best_move = move
                d = distance_array[i]

        return best_move
