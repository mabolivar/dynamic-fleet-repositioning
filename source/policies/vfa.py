from itertools import product
from collections import defaultdict
from source.state import State
from source.policies.policy import Policy
from source.utils import haversine_distance

POLICY_NAME = 'VFA'


def find_closest_order(couriers, orders):
    order_cords = [[order['lat'], order['lng']] for order in orders]
    courier_cords = [[courier['lat'], courier['lng']] for courier in couriers]
    order_exploited_cords, courier_exploited_cords = list(zip(*product(order_cords, courier_cords)))
    distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*courier_exploited_cords))
    nearest_order = defaultdict()
    for j, courier in enumerate(couriers):
        location = (courier['lat'], courier['lng'])
        nearest_order[location] = {'distance': float('inf')}
        for i, order in enumerate(orders):
            d = distance_array[(i * len(couriers) + j)]
            if d < nearest_order[location]['distance']:
                nearest_order[location] = {
                    'order_id': i,
                    'distance': d,
                    'lat': order['lat'],
                    'lng': order['lng'],
                }
    return nearest_order


class VFA(Policy):
    def __init__(self, **kwargs):
        super(VFA, self).__init__(
            name=POLICY_NAME,
            courier_km_per_minute=kwargs.get('courier_km_per_minute', 1.0),
            minutes_bucket_size=kwargs.get('minutes_bucket_size', 10)
        )
        epoch_in_minutes = range(0, 24 * 60, self.minutes_bucket_size)
        self.V = {t: defaultdict() for t, _ in enumerate(epoch_in_minutes)}
        self.n = 1   # Sample path
        self.epoch = None

    def take_action(self, state: State):
        orders = state.orders
        couriers = state.couriers
        prev_actions = state.prev_actions
        all_locations = state.locations
        self.epoch = state.epoch
        actions = self.compute_actions(couriers)

        if state.epoch > 0 and orders:
            closest_order_per_location = find_closest_order(all_locations, orders)

            self.update_value_estimates(
                prev_epoch=state.epoch - 1,
                nearest_orders=closest_order_per_location
            )
        return actions

    def compute_actions(self, couriers):
        actions = {}
        for ix, courier in enumerate(couriers):
            move_lat, move_lng = self.compute_movement_location(courier['lat'], courier['lng'])
            actions[ix] = {'lat': move_lat, 'lng': move_lng}
        return actions

    def update_value_estimates(self, prev_epoch: int, nearest_orders: dict):
        alpha = 0.2 #* (1 - (self.num_iteration + 1) / self.total_iterations)
        # delta = ceil(10 * (1 - (self.num_iteration + 1) / self.total_iterations))
        if prev_epoch < 0:
            return
        # Value function update algorithm
        for location in nearest_orders:
            sampled_value = nearest_orders[location]['distance']
            for epoch in [prev_epoch - 1, prev_epoch, prev_epoch + 1]:
                if epoch < 0:
                    continue
                prev_value = self.V[epoch].get(location, sampled_value)
                self.V[epoch][location] = (1-alpha) * prev_value + alpha * sampled_value

    def compute_movement_location(self, start_lat, start_lng):
        movements = self.get_neighbours(start_lat, start_lng)
        d = float('inf')
        best_move = (start_lat, start_lng)
        for i, move in enumerate(movements):
            if self.V[self.epoch].get(move, d) < d:
                best_move = move
                d = self.V[self.epoch][move]
        return best_move
