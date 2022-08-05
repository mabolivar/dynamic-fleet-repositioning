import numpy as np
import pandas as pd
from source.utils import haversine_distance, get_nearest_order_per_courier

DEFAULT_PRECISION = 2
DEFAULT_DELIVERY_DURATION_SECONDS = 20 * 60
TIME_BUCKET_SIZE = '10min'


class Scenario:
    def __init__(
            self, index: int,
            label: str,
            data: pd.DataFrame,
            minutes_bucket_size: int,
            precision: int = DEFAULT_PRECISION
            ):
        self.index = index
        self.label = label
        self.minutes_bucket_size = minutes_bucket_size
        self.orders = orders_df_to_bucket_list(
            data, time_bucket_size=str(self.minutes_bucket_size) + "min", precision=precision
        )
        self.couriers = couriers_df_to_bucket_list(
            data, time_bucket_size=str(self.minutes_bucket_size) + "min", precision=precision
        )
        self.epochs = len(self.orders)
        self.precision = precision
        self.data_locations = get_locations(data, precision=self.precision)
        self.neighbours_map = self.get_neighbours_map()
        self.locations = self.get_all_locations()
        self.distance_map = self.get_distance_map()
        self.perfect_cost, _ = self.get_perfect_solution()

    @classmethod
    def generate_scenarios(cls, label: str, data: pd.DataFrame, minutes_bucket_size: int):
        unique_dates = np.sort(data.start_date.unique())
        return [Scenario(i, label, data[lambda x: x.start_date == date], minutes_bucket_size) for i, date in enumerate(unique_dates)]

    def get_orders(self, epoch):
        return self.orders[epoch] if epoch >= 0 else None

    def get_couriers(self, epoch):
        return self.couriers[epoch]

    def get_neighbours_map(self):
        """
        Returns a map of neighbours for each location.
        :return: dict of dicts {source: [destinations]}
        """
        return {
            (loc['lat'], loc['lng']): get_location_neighbours(loc['lat'], loc['lng'], self.precision)
            for loc in self.data_locations
        }

    def get_all_locations(self):
        neighbours_locations = [
            {'lat': loc[0], 'lng': loc[1]}
            for locations in list(self.neighbours_map.values())
            for loc in locations
        ]

        locations = pd.DataFrame(
            self.data_locations + neighbours_locations,
            columns=["lat", "lng"]
        ).drop_duplicates()

        return locations.to_dict(orient="records")

    def get_distance_map(self):
        """
        Returns a map of distances between locations.
        :return: dict of dicts {source: {destination: distance}}
        """
        location_df = pd.DataFrame(self.locations, columns=["lat", "lng"])

        distance_df = (
            location_df
            .merge(location_df, how='cross')
            .assign(
                source=lambda x: list(zip(x.lat_x, x.lng_x)),
                target=lambda x: list(zip(x.lat_y, x.lng_y)),
                distance=lambda x: haversine_distance(x.lat_x, x.lng_x, x.lat_y, x.lng_y)
            )
            [["source", "target", "distance"]]
            .pivot(index="source", columns="target", values="distance")
        )
        return distance_df.to_dict(orient='index')

    def get_perfect_solution(self):
        """
        Returns the perfect cost and solution for the scenario.
        :return:
        """
        best_decisions = dict()
        perfect_cost = 0
        for epoch in range(self.epochs):
            best_decisions[epoch] = dict()
            orders = self.get_orders(epoch)
            couriers = self.get_couriers(epoch)
            if orders is None or couriers is None:
                continue
            best_decisions[epoch]['actions'] = get_nearest_order_per_courier(
                orders, couriers, self.distance_map, self.neighbours_map
            )
            best_decisions[epoch]['cost'] = sum(v['distance'] for k, v in best_decisions[epoch]['actions'].items())
            perfect_cost += best_decisions[epoch]['cost']
        return perfect_cost, best_decisions


def orders_df_to_bucket_list(data: pd.DataFrame, time_bucket_size: str, precision: int):
    num_epochs = 24 * 60 // int(time_bucket_size[:-3])
    orders_per_epoch = [None] * num_epochs
    orders = (
        data
        .rename(columns={"start_lat": "lat", "start_lng": "lng"})
        .sort_values(by="time_seconds")
        .reset_index(drop=True)
        .assign(
                floor_startdatetime=lambda x: x.start_time.dt.floor(time_bucket_size),
                floor_time_seconds=lambda x: (
                        (x.floor_startdatetime - x.floor_startdatetime.dt.normalize())/pd.Timedelta('1 second')
                ).astype(int),
                epoch=lambda x: (x.floor_time_seconds/60 // int(time_bucket_size[:-3])).astype(int),
                lat=lambda x: x.lat.round(precision),
                lng=lambda x: x.lng.round(precision)
        )
        .drop(columns=["floor_startdatetime", "floor_time_seconds"])
        .groupby('epoch')
    )
    for epoch in orders.groups.keys():
        orders_per_epoch[epoch] = list(orders.get_group(epoch).to_dict(orient="index").values())

    return orders_per_epoch


def couriers_df_to_bucket_list(data: pd.DataFrame, time_bucket_size: str, precision: int):
    num_epochs = 24 * 60 // int(time_bucket_size[:-3])
    couriers_per_epoch = [None] * num_epochs
    couriers = (
        data
        .drop(columns=["start_lat", "start_lng", "ride_value"])
        .rename(columns={"end_lat": "lat", "end_lng": "lng"})
        .assign(start_time=lambda x: x.start_time + pd.Timedelta(DEFAULT_DELIVERY_DURATION_SECONDS, "seconds"),
                time_seconds=lambda x: x.time_seconds + DEFAULT_DELIVERY_DURATION_SECONDS
                )
        .sort_values(by="time_seconds")
        .reset_index(drop=True)
        .assign(
                floor_startdatetime=lambda x: x.start_time.dt.floor(time_bucket_size),
                floor_time_seconds=lambda x: (
                    (x.floor_startdatetime - x.floor_startdatetime.dt.normalize()) / pd.Timedelta('1 second')
                ).astype(int),
                epoch=lambda x: (x.floor_time_seconds / 60 // int(time_bucket_size[:-3])).astype(int),
                lat=lambda x: x.lat.round(precision),
                lng=lambda x: x.lng.round(precision)
        )
        .drop(columns=["floor_startdatetime", "floor_time_seconds"])
        .groupby('epoch')
    )
    for epoch in couriers.groups.keys():
        couriers_per_epoch[epoch] = list(couriers.get_group(epoch).to_dict(orient="index").values())

    return couriers_per_epoch


def get_locations(data: pd.DataFrame, precision: int):
    locations = (
        pd.concat([
            data[["start_lat", "start_lng"]].rename(columns={"start_lat": "lat", "start_lng": "lng"}),
            data[["end_lat", "end_lng"]].rename(columns={"end_lat": "lat", "end_lng": "lng"})
            ])
        .reset_index(drop=True)
        .assign(lat=lambda x: x.lat.round(precision),
                lng=lambda x: x.lng.round(precision))
        .drop_duplicates()
    )
    return locations.to_dict(orient="records")


def get_location_neighbours(lat, lng, precision: int):
    """
    Returns a list of neighbours for a given location (including itself).
    :param lat: latitude
    :param lng: longitude
    :param precision: The precision of the location coordinates.
    :return: list of tuples (lat, lng)
    """
    moves = [0, -1, 1]
    scale = 10 ** precision
    return [(round(lat + i / scale, precision), round(lng + j / scale, precision))
            for i in moves for j in moves]
