import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import IsolationForest
import geopy.distance

def add_advanced_features(df: pd.DataFrame):
    df = df.copy()
    df['Hour'] = (df['Time'] / 3600) % 24
    df['DayOfWeek'] = (df['Time'] // (3600*24)) % 7
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x in [5, 6] else 0)
    if 'UserID' in df.columns:
        user_avg = df.groupby('UserID')['Amount'].mean()
        df['UserAvgAmount'] = df['UserID'].map(user_avg)
        df['AmtDeviationFromUser'] = df['Amount'] - df['UserAvgAmount']
    df['PrevTime'] = df['Time'].shift(1)
    df['TimeDelta'] = df['Time'] - df['PrevTime']
    df['HighVelocityFlag'] = (df['TimeDelta'] < 60).astype(int)
    if {'Lat', 'Lon'}.issubset(set(df.columns)):
        user_home = df.groupby('UserID').agg({'Lat':'mean','Lon':'mean'}).to_dict('index')
        def dist_from_home(row):
            if row['UserID'] in user_home:
                home_lat = user_home[row['UserID']]['Lat']
                home_lon = user_home[row['UserID']]['Lon']
                return geopy.distance.distance((home_lat, home_lon), (row['Lat'], row['Lon'])).km
            return 0
        df['DistFromHomeKM'] = df.apply(dist_from_home, axis=1)
    iso = IsolationForest(contamination=0.01, random_state=42)
    df['IsoAnomalyScore'] = iso.fit_predict(df.select_dtypes(include=np.number))
    df.fillna(0, inplace=True)
    return df
