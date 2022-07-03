import numpy as np
import pandas as pd

DEFAULT_DELIVERY_DURATION_SECONDS = 20 * 60
TIME_BUCKET_SIZE = '10min'

# ToDo: Assuming that all hours do we have orders and couriers... this might be wrong
def orders_df_to_bucket_list(data: pd.DataFrame, time_bucket_size: str):
    orders = (data
              .rename(columns={"start_lat": "lat", "start_lng": "lng"})
              .sort_values(by="time_seconds")
              .reset_index(drop=True)
              .assign(ceil_startdatetime=lambda x: x.start_time.dt.ceil(time_bucket_size))
              .groupby('ceil_startdatetime')
              )
    return [list(orders.get_group(x).to_dict(orient="index").values()) for x in orders.groups]   # ToDo: couriers should be a numpy array (?)


def couriers_df_to_bucket_list(data: pd.DataFrame, time_bucket_size: str):
    couriers = (
        data
        .drop(columns=["start_lat", "start_lng", "ride_value"])
        .rename(columns={"end_lat": "lat", "end_lng": "lng"})
        .assign(start_time=lambda x: x.start_time + pd.Timedelta(DEFAULT_DELIVERY_DURATION_SECONDS, "seconds"),
                time_seconds=lambda x: x.time_seconds + DEFAULT_DELIVERY_DURATION_SECONDS
                )
        .sort_values(by="time_seconds")
        .reset_index(drop=True)
        .assign(ceil_startdatetime=lambda x: x.start_time.dt.ceil(time_bucket_size))
        .groupby('ceil_startdatetime')
    )
    return [list(couriers.get_group(x).to_dict(orient="index").values()) for x in couriers.groups]   # ToDo: couriers should be a numpy array (?)


class Scenario:
    def __init__(self, index: int, label: str, data: pd.DataFrame, minutes_bucket_size: int):
        self.index = index
        self.label = label
        self.minutes_bucket_size = minutes_bucket_size
        self.orders = orders_df_to_bucket_list(data, time_bucket_size=str(self.minutes_bucket_size) + "min")
        self.couriers = couriers_df_to_bucket_list(data, time_bucket_size=str(self.minutes_bucket_size) + "min")
        self.epochs = len(self.orders)
        self.perfect_cost = self.get_perfect_cost()

    @classmethod
    def generate_scenarios(cls, label: str, data: pd.DataFrame, minutes_bucket_size: int):
        unique_dates = np.sort(data.start_date.unique())
        return [Scenario(i, label, data[lambda x: x.start_date == date], minutes_bucket_size) for i, date in enumerate(unique_dates)]

    def get_orders(self, epoch):
        return self.orders[epoch] if epoch > 0 else None

    def get_couriers(self, epoch):
        return self.couriers[epoch]

    def get_perfect_cost(self):
        # ToDo: implement this
        return None
