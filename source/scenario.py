import numpy as np
import pandas as pd

DEFAULT_DELIVERY_DURATION_SECONDS = 20 * 60


def get_orders(data: pd.DataFrame):
    # orders = data.to_dict(orient="index").values()
    # return sorted(orders, key=lambda x: x["time_seconds"])
    orders = data.sort_values(by="time_seconds").reset_index(drop=True).to_dict(orient="index").values()
    return list(orders)    # ToDo: couriers should be a numpy array (?)


def get_couriers(data: pd.DataFrame):
    couriers = (
        data
        .drop(columns=["start_lat", "start_lng", "ride_value"])
        .rename(columns={"end_lat": "start_lat", "end_lng": "start_lng"})
        .assign(start_time=lambda x: x.start_time + pd.Timedelta(DEFAULT_DELIVERY_DURATION_SECONDS, "seconds"),
                time_seconds=lambda x: x.time_seconds + DEFAULT_DELIVERY_DURATION_SECONDS
                )
        .sort_values(by="time_seconds")
        .reset_index(drop=True)
        .to_dict(orient="index").values()
    )
    return list(couriers)   # ToDo: couriers should be a numpy array (?)


class Scenario:
    def __init__(self, index: int, label: str, data: pd.DataFrame):
        self.index = index
        self.label = label
        self.orders = get_orders(data)
        self.couriers = get_couriers(data)

    @classmethod
    def generate_scenarios(cls, label: str, data: pd.DataFrame):
        unique_dates = np.sort(data.start_date.unique())
        return [Scenario(i, label, data[lambda x: x.start_date == date]) for i, date in enumerate(unique_dates)]

    def get_orders(self, epoch):
        return self.orders[epoch] if epoch > 0 else None

    def get_couriers(self, epoch):
        return self.couriers[epoch]

