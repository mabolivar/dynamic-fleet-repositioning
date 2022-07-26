from itertools import product

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
        return self.get_current_nearest_order(orders, couriers, state.distance_map, state.neighbours_map)

    def get_current_nearest_order(self, orders, couriers, distance_map, neighbours_map):
        if not orders:
            return {
                ix: {'lat': courier['lat'], 'lng': courier['lng']}
                for ix, courier in enumerate(couriers)
            }

        nearest_order = dict()
        for j, courier in enumerate(couriers):
            courier_lat, courier_lng = courier['lat'], courier['lng']
            nearest_order[j] = {'order_id': None, 'distance': float('inf'), 'lat': None, 'lng': None}
            for i, order in enumerate(orders):
                order_lat, order_lng = order['lat'], order['lng']
                d = distance_map[(courier_lat, courier_lng)][(order_lat, order_lng)]
                if d < nearest_order[j]['distance']:
                    move_lat, move_lng = compute_movement_location(courier_lat, courier_lng, order_lat, order_lng, neighbours_map)
                    nearest_order[j] = {
                        'order_id': i,
                        'distance': d,
                        'lat': move_lat,
                        'lng': move_lng,
                    }
        return nearest_order


def compute_movement_location(start_lat, start_lng, end_lat, end_lng, neighbours_map):
    movements = neighbours_map[(start_lat, start_lng)]
    order_exploited_cords, movement_exploited_cords = list(zip(*product([(end_lat, end_lng)], movements)))
    distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*movement_exploited_cords))
    d = float('inf')
    best_move = None
    for i, move in enumerate(movements):
        if distance_array[i] < d:
            best_move = move
            d = distance_array[i]

    return best_move

