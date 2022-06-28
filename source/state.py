import numpy as np
from source.scenario import Scenario


def haversine_distance(lat_1, lng_1, lat_2, lng_2):
    size = len(lat_1) * len(lat_2)
    # ToDo: Implement function
    return np.ones(shape=(1, size)) * 100


class State:
    def __init__(self, scenario: Scenario):
        self.scenario_ix = scenario.index
        self.epoch = 0
        # Orders arose between t-1 and t
        self.orders = scenario.get_orders(epoch=self.epoch - 1)
        # Couriers arose between t-1 and t
        self.couriers = scenario.get_couriers(epoch=self.epoch)

    # ToDo: make it singleton
    @property
    def cost_function(self):
        # ToDo: get lat,lng coords and indexes
        distance_array = self.haversine_distance(self.orders, self.orders, self.couriers, self.couriers)
        return {
            (order_ix, courier_ix): distance_array(i * (len(self.orders)) + j)
            for i, order_ix in enumerate(self.orders)
            for j, courier_ix in enumerate(self.couriers)
            }


