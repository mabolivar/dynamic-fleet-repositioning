from source.state import State
from source.policies.policy import Policy
from source.utils import get_nearest_order_per_courier

POLICY_NAME = 'LastNearestOrder'

class LastNearestOrder(Policy):
    def __init__(self, **kwargs):
        super(LastNearestOrder, self).__init__(
            name=POLICY_NAME,
            **kwargs,
        )

    def take_action(self, state: State):
        orders = state.orders
        couriers = state.couriers
        return get_nearest_order_per_courier(
            orders, couriers, state.distance_map, state.neighbours_map
        )

