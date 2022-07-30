import numpy as np
import pandas as pd
from itertools import product

DTYPES = {'start_time': str, 'start_lat': 'float',
          'start_lng': 'float', 'end_lat': 'float',
          'end_lng': 'float', 'ride_value': 'float'}


def load_data(path="data/data.csv"):
    return (
        pd.read_csv(path, dtype=DTYPES)
        [lambda x: ~(x.start_lng.isna() | x.end_lng.isna())]
        [lambda x: (x.end_lat > np.floor(np.quantile(x.start_lat, 0.001))) &
                   (x.end_lng > np.floor(np.quantile(x.start_lng, 0.001))) &
                   (x.end_lat < np.ceil(np.quantile(x.start_lat, 0.999))) &
                   (x.end_lng < np.ceil(np.quantile(x.start_lng, 0.999)))
        ]
        .assign(start_time=lambda x: pd.to_datetime(x.start_time, format='%Y-%m-%d %H:%M:%S', errors='coerce'),
                start_date=lambda x: x.start_time.dt.date,
                time_seconds=lambda x: (
                        (x.start_time - x.start_time.dt.normalize())/pd.Timedelta('1 second')).astype(int)
                )
    )


def split_data(data, test_size=0.2):
    unique_dates = np.sort(data.start_date.unique())
    num_days_test = int(len(unique_dates) * test_size)
    test_dates = unique_dates[-num_days_test:]
    test_data = data[data.start_date.isin(test_dates)]
    train_data = data[~data.start_date.isin(test_dates)]
    return train_data, test_data


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km


def get_nearest_order_per_courier(orders, couriers, distance_map, neighbours_map):
    """
    Returns the nearest order for each courier.
    :param orders:
    :param couriers:
    :param distance_map:
    :param neighbours_map:
    :return: dict of nearest order for each courier
    """
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
                move_lat, move_lng, move_distance = compute_movement_location(courier_lat, courier_lng, order_lat, order_lng, neighbours_map)
                nearest_order[j] = {
                    'order_id': i,
                    'distance': move_distance,
                    'lat': move_lat,
                    'lng': move_lng,
                }
    return nearest_order


def compute_movement_location(start_lat, start_lng, end_lat, end_lng, neighbours_map):
    """
    Compute the movement location for a courier based on neighbour map.
    :param start_lat:
    :param start_lng:
    :param end_lat:
    :param end_lng:
    :param neighbours_map:
    :return:
    """
    movements = neighbours_map[(start_lat, start_lng)]
    order_exploited_cords, movement_exploited_cords = list(zip(*product([(end_lat, end_lng)], movements)))
    distance_array = haversine_distance(*zip(*order_exploited_cords), *zip(*movement_exploited_cords))
    best_distance = float('inf')
    best_move = None
    for i, move in enumerate(movements):
        if distance_array[i] < best_distance:
            best_move = move
            best_distance = distance_array[i]

    return *best_move, best_distance

