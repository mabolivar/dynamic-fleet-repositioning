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
            **kwargs,
        )

    def take_action(self, state: State):
        couriers = state.couriers
        return {
            ix: {'lat': courier['lat'], 'lng': courier['lng']}
            for ix, courier in enumerate(couriers)
        }
