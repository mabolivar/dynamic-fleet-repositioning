import numpy as np
import pandas as pd

DTYPES = {'start_time': str, 'start_lat': 'float',
          'start_lng': 'float', 'end_lat': 'float',
          'end_lng': 'float', 'ride_value': 'float'}


def load_data(path="data/data.csv"):
    return (
        pd.read_csv(path, dtype=DTYPES)
        [lambda x: ~(x.start_lng.isna() | x.end_lng.isna())]
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
