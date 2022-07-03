from itertools import product

import numpy as np

from source.state import State
from source.policies.policy import Policy
from source.utils import haversine_distance

POLICY_NAME = 'DoNothing'


class DoNothing(Policy):
    def __init__(self, **kwargs):
        super(DoNothing, self).__init__(
            name=POLICY_NAME,
            courier_km_per_minute=kwargs.get('courier_km_per_minute', 1.0),
            minutes_bucket_size=kwargs.get('minutes_bucket_size', 10)
        )

    def take_action(self, state: State):
        couriers = state.couriers
        return {
            ix: {'lat': courier['lat'], 'lng': courier['lng']}
            for ix, courier in enumerate(couriers)
        }
